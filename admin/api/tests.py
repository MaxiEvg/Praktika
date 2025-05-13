import os
import json
import logging
from uuid import uuid4
from typing import List, Optional

import aiofiles
from fastapi import (
    APIRouter, Depends, Request,
    HTTPException, UploadFile, File, Form, status
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .templating import templates
from .auth import get_current_user_from_cookie  # Зависимость авторизации
from database.models import Test, TestQuestion, TestOption, User
from db_helper import db_helper

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def get_session() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

router = APIRouter()
router.mount("/static", StaticFiles(directory="static"), name="static")

# 1) Список тестов — только для авторизованных
@router.get("/tests", response_class=HTMLResponse)
async def list_tests(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    logger.info("Получение списка всех тестов")
    stmt = select(Test).options(
        selectinload(Test.questions).selectinload(TestQuestion.options)
    )
    result = await session.execute(stmt)
    tests = result.scalars().all()
    return templates.TemplateResponse("tests_list.html", {"request": request, "user": user, "tests": tests})

# 2) Форма создания — только авторизованные
@router.get("/tests/form", response_class=HTMLResponse)
async def create_test_form(
    request: Request,
    user: User = Depends(get_current_user_from_cookie)
):
    logger.info("Отображение формы создания нового теста")
    return templates.TemplateResponse("test_form.html", {
        "request": request,
        "user": user,
        "test": None,
        "question_count": 0,
        "questions_data": []
    })

# 3) Форма редактирования — только авторизованные
@router.get("/tests/form/{test_id}", response_class=HTMLResponse)
async def edit_test_form(
    request: Request,
    test_id: int,
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session),
):
    logger.info(f"Редактирование теста с ID {test_id}")
    stmt = (
        select(Test)
        .options(
            selectinload(Test.questions).selectinload(TestQuestion.options)
        )
        .filter(Test.id == test_id)
    )
    result = await session.execute(stmt)
    test = result.scalars().first()
    if not test:
        logger.error(f"Тест с ID {test_id} не найден")
        raise HTTPException(status_code=404, detail="Test not found")

    questions_data = []
    for q in test.questions:
        answers = [opt.option_text for opt in q.options]
        correct_index = next((idx for idx, opt in enumerate(q.options) if opt.is_correct), 0)
        questions_data.append({
            "text": q.question_text,
            "answers": answers,
            "correct": correct_index,
            "image_path": q.image_path or ""
        })

    return templates.TemplateResponse(
        "test_edit.html",
        {
            "request": request,
            "user": user,
            "test": test,
            "question_count": len(test.questions),
            "questions_data": questions_data
        }
    )

# 4) Создать или обновить — только авторизованные
@router.post("/tests/", response_class=RedirectResponse)
async def create_update_test(
    request: Request,
    test_id: Optional[int] = Form(None),
    title: str = Form(...),
    description: str = Form(""),
    questions_data: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session),
):
    if test_id:
        logger.info(f"Обновление теста с ID {test_id}")
        stmt = select(Test).options(
            selectinload(Test.questions).selectinload(TestQuestion.options)
        ).filter(Test.id == test_id)
        result = await session.execute(stmt)
        test = result.scalars().first()
        if not test:
            logger.error(f"Тест с ID {test_id} не найден")
            raise HTTPException(status_code=404, detail="Test not found")
        # удаляем старые вопросы
        for q in list(test.questions):
            await session.delete(q)
    else:
        logger.info("Создание нового теста")
        test = Test(title=title, description=description)
        session.add(test)
        await session.flush()

    test.title = title
    test.description = description

    questions = json.loads(questions_data)
    logger.info(f"Добавление {len(questions)} вопросов")

    for idx, q in enumerate(questions, start=1):
        q_obj = TestQuestion(
            test_id=test.id,
            question_text=q["text"],
            question_type=q.get("type", "single"),
            sequence_number=idx,
        )
        session.add(q_obj)
        await session.flush()

        img_field = q.get("image_field")
        if img_field:
            upload = next((f for f in files if f.filename == img_field), None)
            if upload:
                ext = os.path.splitext(upload.filename)[1]
                fname = f"{uuid4().hex}{ext}"
                fpath = os.path.join(UPLOAD_DIR, fname)
                async with aiofiles.open(fpath, "wb") as out:
                    await out.write(await upload.read())
                q_obj.image_path = f"uploads/{fname}"

        for a_idx, answer in enumerate(q.get("answers", [])):
            opt = TestOption(
                question_id=q_obj.id,
                option_text=answer,
                is_correct=(a_idx == q.get("correct", 0)),
            )
            session.add(opt)

    await session.commit()
    logger.info(f"Тест с ID {test.id} успешно сохранён")
    return RedirectResponse(url=f"/tests/{test.id}", status_code=status.HTTP_303_SEE_OTHER)

# 5) Просмотр теста — только авторизованные
@router.get("/tests/{test_id}", response_class=HTMLResponse)
async def test_view(
    request: Request,
    test_id: int,
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    logger.info(f"Получение теста с ID {test_id} для просмотра")
    stmt = select(Test).options(
        selectinload(Test.questions).selectinload(TestQuestion.options)
    ).filter(Test.id == test_id)
    result = await session.execute(stmt)
    test = result.scalars().first()
    if not test:
        logger.error(f"Тест с ID {test_id} не найден")
        raise HTTPException(status_code=404, detail="Test not found")

    return templates.TemplateResponse("test_view.html", {"request": request, "user": user, "test": test})

# 6) Удаление теста — только авторизованные
@router.post("/tests/{test_id}/delete", response_class=RedirectResponse)
async def delete_test(
    test_id: int,
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    logger.info(f"Удаление теста с ID {test_id}")
    test = await session.get(Test, test_id)
    if test:
        await session.delete(test)
        await session.commit()
        logger.info(f"Тест с ID {test_id} удалён")
    else:
        logger.warning(f"Тест с ID {test_id} не найден при удалении")
    return RedirectResponse(url="/tests", status_code=status.HTTP_303_SEE_OTHER)
