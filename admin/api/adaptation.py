import os
import json
import logging
from typing import List, Optional
from fastapi import status
from fastapi import (
    APIRouter, Depends, Request,
    HTTPException, UploadFile, File, Form
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .templating import templates
from database.models import (
    AdaptationPlan,
    AdaptationStage,
    ContentMaterial,
    Test,
    Positions
)
from db_helper import db_helper

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ─── Настройка загрузки статических файлов ───────────────────────────────────────────
UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()
router.mount("/static", StaticFiles(directory="static"), name="static")


async def get_session() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session


# ─── 1) Список планов адаптации ───────────────────────────────────────────────────────
@router.get("/plans", response_class=HTMLResponse, name="list_plans")
async def list_plans(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Список всех планов с должностями и этапами (жадная загрузка stages -> тесты)
    """
    result = await session.execute(
        select(AdaptationPlan)
        .options(
            selectinload(AdaptationPlan.position),
            selectinload(AdaptationPlan.stages).selectinload(AdaptationStage.test)
        )
    )
    plans = result.scalars().all()
    return templates.TemplateResponse(
        "adaptation_list.html",
        {"request": request, "plans": plans}
    )


# ─── 2) Форма создания нового плана ────────────────────────────────────────────────────
@router.get("/plans/form", response_class=HTMLResponse)
async def create_plan_form(request: Request, session: AsyncSession = Depends(get_session)):
    logger.info("Отображение формы создания плана")
    materials = (await session.execute(select(ContentMaterial))).scalars().all()
    tests     = (await session.execute(select(Test))).scalars().all()
    positions = (await session.execute(select(Positions))).scalars().all()

    return templates.TemplateResponse("adaptation_form.html", {
        "request": request,
        "plan": None,
        "materials": materials,
        "tests": tests,
        "positions": positions,
        "stages": []
    })


# ─── 3) Форма редактирования существующего плана ─────────────────────────────────────
@router.get("/plans/form/{plan_id}", response_class=HTMLResponse)
async def edit_plan_form(
    request: Request,
    plan_id: int,
    session: AsyncSession = Depends(get_session)
):
    logger.info(f"Редактирование плана ID={plan_id}")
    stmt = select(AdaptationPlan).options(
        selectinload(AdaptationPlan.stages).selectinload(AdaptationStage.test)
    ).where(AdaptationPlan.id == plan_id)
    result = await session.execute(stmt)
    plan = result.scalar_one_or_none()
    if not plan:
        logger.error("План не найден")
        raise HTTPException(status_code=404, detail="Plan not found")

    materials = (await session.execute(select(ContentMaterial))).scalars().all()
    tests     = (await session.execute(select(Test))).scalars().all()
    positions = (await session.execute(select(Positions))).scalars().all()

    # Подготовка существующих этапов для JS
    existing = []
    for s in sorted(plan.stages, key=lambda e: e.sequence_number or 0):
        existing.append({
            "title": s.title,
            "content_id": s.content_id,
            "test_id": s.test_id
        })

    return templates.TemplateResponse("adaptation_form.html", {
        "request": request,
        "plan": plan,
        "materials": materials,
        "tests": tests,
        "positions": positions,
        "stages": existing
    })


# ─── 4) Создание или обновление плана ──────────────────────────────────────────────────
@router.post("/plans/", response_class=RedirectResponse)
async def create_update_plan(
    request: Request,
    plan_id: Optional[int]     = Form(None),
    name: str                  = Form(...),
    description: Optional[str] = Form(None),
    position_id: Optional[int] = Form(None),
    stages_data: str           = Form("[]"),
    session: AsyncSession      = Depends(get_session)
):
    logger.info("Сохранение плана адаптации")
    try:
        stages = json.loads(stages_data)
    except json.JSONDecodeError:
        logger.error("Неправильный формат JSON для stages_data")
        raise HTTPException(status_code=400, detail="Invalid stages JSON")

    async with session.begin():
        # Если обновляем — удаляем старые этапы
        if plan_id:
            logger.info(f"Удаляем старые этапы для плана {plan_id}")
            await session.execute(delete(AdaptationStage).where(AdaptationStage.plan_id == plan_id))
            plan = await session.get(AdaptationPlan, plan_id)
            if not plan:
                raise HTTPException(status_code=404, detail="Plan not found")
        else:
            plan = AdaptationPlan(name=name, description=description, position_id=position_id)
            session.add(plan)
            await session.flush()

        # Обновляем поля плана
        plan.name        = name
        plan.description = description
        plan.position_id = position_id

        # Создаём новые этапы в указанном порядке
        for idx, st in enumerate(stages, start=1):
            cid = int(st["content_id"]) if st.get("content_id") else None
            tid = int(st["test_id"])    if st.get("test_id")    else None

            stage = AdaptationStage(
                plan_id=plan.id,
                title=st["title"],
                sequence_number=idx,
                content_id=cid,
                test_id=tid
            )
            session.add(stage)

    # После session.begin() он автоматически коммитит, потому Redirect
    return RedirectResponse(f"/plans/{plan.id}", status_code=status.HTTP_303_SEE_OTHER)


# ─── 5) Просмотр одного плана ─────────────────────────────────────────────────────────
@router.get("/plans/{plan_id}", response_class=HTMLResponse)
async def plan_detail(
    request: Request,
    plan_id: int,
    session: AsyncSession = Depends(get_session)
):
    logger.info(f"Просмотр плана ID={plan_id}")
    stmt = select(AdaptationPlan).options(
        selectinload(AdaptationPlan.stages).selectinload(AdaptationStage.test)
    ).where(AdaptationPlan.id == plan_id)
    result = await session.execute(stmt)
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    stages = sorted(plan.stages, key=lambda e: e.sequence_number or 0)
    return templates.TemplateResponse("adaptation_detail.html", {
        "request": request,
        "plan": plan,
        "stages": stages
    })

@router.post("/plans/delete/{plan_id}", name="delete_plan")
async def delete_plan(
    plan_id: int,
    session: AsyncSession = Depends(get_session)
):
    logger.info(f"Удаление плана адаптации ID={plan_id}")
    plan = await session.get(AdaptationPlan, plan_id)
    if plan:
        # удаляем все этапы (cascade="all, delete-orphan" уже в модели позаботится об этапах)
        await session.delete(plan)
        await session.commit()
        logger.info(f"План ID={plan_id} успешно удалён")
    else:
        logger.warning(f"Попытка удалить несуществующий план ID={plan_id}")
    return RedirectResponse(url="/plans", status_code=status.HTTP_303_SEE_OTHER)