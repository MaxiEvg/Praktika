import json
import logging
from typing import Optional, List

from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    HTTPException,
    status
)
from fastapi.responses import RedirectResponse, HTMLResponse
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
from db_helper import db_helper  # Убедитесь, что путь к модулю указан правильно

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

async def get_session() -> AsyncSession:
    async for session in db_helper.session_getter():
        yield session

@router.get("/plans", response_class=HTMLResponse, name="list_plans")
async def list_plans(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(AdaptationPlan))
    plans = result.scalars().all()
    return templates.TemplateResponse(
        "adaptation_list.html",
        {"request": request, "plans": plans}
    )

@router.get("/plans/form", response_class=HTMLResponse, name="create_plan_form")
async def create_plan_form(request: Request, session: AsyncSession = Depends(get_session)):
    materials = (await session.execute(select(ContentMaterial))).scalars().all()
    tests = (await session.execute(select(Test).options(selectinload(Test.questions)))).scalars().all()
    positions = (await session.execute(select(Positions))).scalars().all()

    return templates.TemplateResponse(
        "adaptation_form.html",
        {
            "request": request,
            "plan": None,
            "materials": materials,
            "tests": tests,
            "positions": positions,
            "stages": []
        }
    )

@router.get("/plans/form/{plan_id}", response_class=HTMLResponse, name="edit_plan_form")
async def edit_plan_form(
    request: Request,
    plan_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(AdaptationPlan)
        .options(
            selectinload(AdaptationPlan.stages)
            .selectinload(AdaptationStage.test)
        )
        .where(AdaptationPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    materials = (await session.execute(select(ContentMaterial))).scalars().all()
    tests = (await session.execute(select(Test).options(selectinload(Test.questions)))).scalars().all()
    positions = (await session.execute(select(Positions))).scalars().all()

    existing = []
    for s in sorted(plan.stages, key=lambda x: x.sequence_number or 0):
        existing.append({
            "title": s.title,
            "content_id": s.content_id,
            "test_id": s.test_id
        })

    return templates.TemplateResponse(
        "adaptation_form.html",
        {
            "request": request,
            "plan": plan,
            "materials": materials,
            "tests": tests,
            "positions": positions,
            "stages": existing
        }
    )

@router.post("/plans/", response_class=RedirectResponse, name="create_update_plan")
async def create_update_plan(
    request: Request,
    plan_id: Optional[int] = Form(None),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    position_id: Optional[int] = Form(None),
    stages_data: str = Form("[]"),
    session: AsyncSession = Depends(get_session),
):
    try:
        stages = json.loads(stages_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    async with session.begin():
        if plan_id:
            result = await session.execute(
                select(AdaptationPlan)
                .options(selectinload(AdaptationPlan.stages))
                .where(AdaptationPlan.id == plan_id)
            )
            plan = result.scalar_one_or_none()
            if not plan:
                raise HTTPException(status_code=404, detail="Plan not found")

            await session.execute(
                delete(AdaptationStage).where(AdaptationStage.plan_id == plan.id)
            )
        else:
            plan = AdaptationPlan(
                name=name,
                description=description,
                position_id=position_id
            )
            session.add(plan)

        await session.flush()

        plan.name = name
        plan.description = description
        plan.position_id = position_id

        for idx, st in enumerate(stages, start=1):
            content_id = st.get("content_id")
            if content_id not in (None, "", "null"):
                content = await session.get(ContentMaterial, int(content_id))
                if not content:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Content material {content_id} not found"
                    )
                content_id = int(content_id)
            else:
                content_id = None

            stage = AdaptationStage(
                plan_id=plan.id,
                title=st["title"],
                content_id=content_id,
                sequence_number=idx
            )
            session.add(stage)
            await session.flush()

            test_id = st.get("test_id")
            if test_id not in (None, "", "null"):
                test = await session.get(Test, int(test_id))
                if not test:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Test {test_id} not found"
                    )
                stage.test_id = test.id
                await session.flush()

        await session.commit()

    return RedirectResponse(f"/plans/{plan.id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/plans/{plan_id}", response_class=HTMLResponse, name="plan_detail")
async def plan_detail(
    request: Request,
    plan_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(AdaptationPlan)
        .options(
            selectinload(AdaptationPlan.stages)
            .selectinload(AdaptationStage.test)
            .selectinload(Test.questions)
        )
        .where(AdaptationPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    stages = sorted(plan.stages, key=lambda x: x.sequence_number or 0)
    return templates.TemplateResponse(
        "adaptation_detail.html",
        {"request": request, "plan": plan, "stages": stages}
    )
