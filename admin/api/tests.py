from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json
from typing import List, Optional

from .templating import templates
from database.models import Test, TestQuestion, TestOption
from db_helper import db_helper

# Зависимость для получения сессии
async def get_session() -> AsyncSession:
    async for s in db_helper.session_getter():
        yield s

router = APIRouter()

# Список всех тестов
@router.get("/tests", response_class=HTMLResponse)
async def list_tests(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Test))
    tests = result.scalars().all()
    return templates.TemplateResponse("tests_list.html", {"request": request, "tests": tests})

# Форма для создания нового теста
@router.get("/tests/form", response_class=HTMLResponse)
async def create_test_form(request: Request):
    return templates.TemplateResponse("test_form.html", {"request": request, "test": None})

# Форма для редактирования существующего теста
@router.get("/tests/form/{test_id}", response_class=HTMLResponse)
async def edit_test_form(request: Request, test_id: int, session: AsyncSession = Depends(get_session)):
    test = await session.get(Test, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    await session.refresh(test)
    return templates.TemplateResponse("test_form.html", {"request": request, "test": test})

# Создание или обновление теста
@router.post("/tests/", response_class=RedirectResponse)
async def create_update_test(
    request: Request,
    test_id: Optional[int] = Form(None),
    title: str = Form(...),
    description: str = Form(""),
    questions_data: str = Form(...),  # JSON-строка с описанием вопросов
    files: List[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session)
):
    # Если test_id задан — обновляем, иначе создаём новый
    if test_id:
        test = await session.get(Test, test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        # удаляем старые вопросы
        for q in list(test.questions):
            await session.delete(q)
    else:
        test = Test(title=title, description=description)
        session.add(test)
        await session.flush()

    test.title = title
    test.description = description

    questions = json.loads(questions_data)
    # Создаём вопросы и ответы
    for idx, q in enumerate(questions):
        q_obj = TestQuestion(
            test_id=test.id,
            question_text=q['text'],
            question_type=q.get('type', 'single'),
            sequence_number=idx + 1
        )
        session.add(q_obj)
        await session.flush()

        # Если есть изображение
        img_field = q.get('image_field')
        if img_field:
            upload = next((f for f in files if f.filename == img_field), None)
            if upload:
                q_obj.image_data = await upload.read()

        for a_idx, answer in enumerate(q.get('answers', [])):
            opt = TestOption(
                question_id=q_obj.id,
                option_text=answer,
                is_correct=(a_idx == q.get('correct', 0))
            )
            session.add(opt)

    await session.commit()
    return RedirectResponse(url=f"/tests/{test.id}", status_code=303)

# Удаление теста
@router.post("/tests/{test_id}/delete", response_class=RedirectResponse)
async def delete_test(test_id: int, session: AsyncSession = Depends(get_session)):
    test = await session.get(Test, test_id)
    if test:
        await session.delete(test)
        await session.commit()
    return RedirectResponse(url="/tests", status_code=303)