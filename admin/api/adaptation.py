import json
import logging
from typing import Optional

from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    HTTPException,
    status
)
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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
logging.basicConfig(level=logging.INFO)

router = APIRouter()


async def get_session() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session


@router.get("/plans", response_class=HTMLResponse, name="list_plans")
async def list_plans(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Показать список всех планов адаптации
    """
    result = await session.execute(
        select(AdaptationPlan).options(
            joinedload(AdaptationPlan.stages).joinedload(AdaptationStage.tests)
        )
    )
    plans = result.scalars().all()
    return templates.TemplateResponse(
        "adaptation_list.html",
        {"request": request, "plans": plans}
    )


@router.get("/plans/form", response_class=HTMLResponse, name="create_plan_form")
async def create_plan_form(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Форма создания нового плана (с возможностью выбрать позицию)
    """
    materials = (await session.execute(select(ContentMaterial))).scalars().all()
    tests     = (await session.execute(select(Test))).scalars().all()
    positions = (await session.execute(select(Positions))).scalars().all()

    return templates.TemplateResponse(
        "adaptation_form.html",
        {
            "request":   request,
            "plan":      None,
            "materials": materials,
            "tests":     tests,
            "positions": positions,
            "stages":    []
        }
    )


@router.get("/plans/form/{plan_id}", response_class=HTMLResponse, name="edit_plan_form")
async def edit_plan_form(
    request: Request,
    plan_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Форма редактирования существующего плана, с выбором должности
    """
    result = await session.execute(
        select(AdaptationPlan).options(
            joinedload(AdaptationPlan.stages).joinedload(AdaptationStage.tests)
        ).where(AdaptationPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    materials = (await session.execute(select(ContentMaterial))).scalars().all()
    tests     = (await session.execute(select(Test))).scalars().all()
    positions = (await session.execute(select(Positions))).scalars().all()

    existing = []
    for s in sorted(plan.stages, key=lambda x: x.sequence_number or 0):
        existing.append({
            "title":      s.title,
            "content_id": s.content_id,
            "test_id":    s.tests[0].id if s.tests else None
        })

    return templates.TemplateResponse(
        "adaptation_form.html",
        {
            "request":   request,
            "plan":      plan,
            "materials": materials,
            "tests":     tests,
            "positions": positions,
            "stages":    existing
        }
    )


@router.get("/plans/{plan_id}", response_class=HTMLResponse, name="plan_detail")
async def plan_detail(
    request: Request,
    plan_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Просмотр одного плана вместе с этапами (только чтение)
    """
    result = await session.execute(
        select(AdaptationPlan).options(
            joinedload(AdaptationPlan.stages).joinedload(AdaptationStage.tests)
        ).where(AdaptationPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    stages = sorted(plan.stages, key=lambda x: x.sequence_number or 0)
    return templates.TemplateResponse(
        "adaptation_detail.html",
        {"request": request, "plan": plan, "stages": stages}
    )


@router.post("/plans/", response_class=RedirectResponse, name="create_update_plan")
async def create_update_plan(
    plan_id: Optional[int]     = Form(None),
    name: str                  = Form(...),
    description: Optional[str] = Form(None),
    position_id: Optional[int] = Form(None),
    stages_data: str           = Form("[]"),
    session: AsyncSession      = Depends(get_session)
):
    """
    Создать новый план или обновить существующий.
    По stages_data (JSON) воссоздаёт все этапы в указанном порядке.
    """
    # 1) Получаем или создаём план
    if plan_id:
        result = await session.execute(
            select(AdaptationPlan).options(
                joinedload(AdaptationPlan.stages).joinedload(AdaptationStage.tests)
            ).where(AdaptationPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        for st in plan.stages:
            await session.delete(st)
        await session.flush()
    else:
        plan = AdaptationPlan(name=name, description=description, position_id=position_id)
        session.add(plan)
        await session.flush()

    # 2) Обновляем поля плана
    plan.name        = name
    plan.description = description
    plan.position_id = position_id

    # 3) Разбираем JSON с этапами и создаём каждую запись
    stages = json.loads(stages_data)
    for idx, st in enumerate(stages, start=1):
        raw_content = st.get("content_id")
        content_id = int(raw_content) if raw_content not in (None, "", "null") else None

        stage = AdaptationStage(
            plan_id=plan.id,
            title=st["title"],
            content_id=content_id,
            sequence_number=idx
        )
        session.add(stage)
        await session.flush()

        raw_test = st.get("test_id")
        if raw_test:
            test = await session.get(Test, int(raw_test))
            if test:
                stage.tests.append(test)

    # 4) Сохраняем изменения
    await session.commit()
    return RedirectResponse(f"/plans/{plan.id}", status_code=status.HTTP_303_SEE_OTHER)
