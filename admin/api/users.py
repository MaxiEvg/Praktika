import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter, Depends, Request,
    HTTPException, Form, status
)
from passlib.context import CryptContext
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .auth import get_current_user_from_cookie
from .templating import templates
from database.models import (
    User, Department, Positions, UserRole,
    AdaptationPlan, AdaptationStage,
    UserAdaptationProgress, ProgressStatus
)
from db_helper import db_helper

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_session() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session


# — PROFILE — #
@router.get("/profile", response_class=HTMLResponse, name="user_profile")
async def get_profile(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(User)
        .options(
            joinedload(User.department),
            joinedload(User.position)
        )
        .where(User.id == current_user.id)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": {
                "username":    db_user.username,
                "full_name":   f"{db_user.first_name} {db_user.last_name}",
                "email":       db_user.email,
                "role":        db_user.role.value,
                "department":  db_user.department.name if db_user.department else "",
                "position":    db_user.position.name if db_user.position else ""
            }
        }
    )


# — EDIT PROFILE — #
@router.get("/profile/edit", response_class=HTMLResponse, name="edit_profile_form")
async def edit_profile_form(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    departments = (await session.execute(select(Department))).scalars().all()
    positions   = (await session.execute(select(Positions))).scalars().all()

    return templates.TemplateResponse(
        "profile_edit.html",
        {
            "request": request,
            "user":        current_user,
            "departments": departments,
            "positions":   positions
        }
    )


@router.post("/profile/update", response_class=RedirectResponse)
async def update_profile(
    request: Request,
    first_name: str = Form(...),
    last_name:  str = Form(...),
    email:      str = Form(...),
    department_id: Optional[int]  = Form(None),
    position_id:   Optional[int]  = Form(None),
    new_department: Optional[str] = Form(None),
    new_position:   Optional[str] = Form(None),
    current_user:   User         = Depends(get_current_user_from_cookie),
    session:        AsyncSession = Depends(get_session)
):
    try:
        current_user.first_name = first_name.strip()
        current_user.last_name  = last_name.strip()
        current_user.email      = email.strip()

        if new_department:
            dep = Department(name=new_department.strip())
            session.add(dep)
            await session.flush()
            current_user.department = dep
        elif department_id:
            dep = await session.get(Department, department_id)
            if not dep:
                raise HTTPException(status_code=400, detail="Invalid department")
            current_user.department = dep

        if new_position:
            pos = Positions(name=new_position.strip())
            session.add(pos)
            await session.flush()
            current_user.position = pos
        elif position_id:
            pos = await session.get(Positions, position_id)
            if not pos:
                raise HTTPException(status_code=400, detail="Invalid position")
            current_user.position = pos

        await session.commit()
    except Exception:
        await session.rollback()
        logger.exception("Error updating profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )

    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)


# — LIST USERS — #
@router.get("/users", response_class=HTMLResponse, name="list_users")
async def list_users(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    # 1) Жадно загрузим department, position, и прогресс с планами:
    stmt = (
        select(User)
        .options(
            joinedload(User.department),
            joinedload(User.position),
            joinedload(User.adaptation_progress)
              .joinedload(UserAdaptationProgress.stage)
              .joinedload(AdaptationStage.plan)
        )
        .where(User.role == UserRole.EMPLOYEE)
        .order_by(User.last_name, User.first_name)
    )
    result = await session.execute(stmt)
    users: List[User] = result.unique().scalars().all()

    # 2) Собираем JSON так, чтобы планы были именно из прогресса пользователя:
    employees_json: List[Dict[str, Any]] = []
    for u in users:
        # уникальные планы через set()
        plan_set = { prog.stage.plan for prog in u.adaptation_progress if prog.stage and prog.stage.plan }
        plans = [{"id": p.id, "name": p.name} for p in plan_set]

        employees_json.append({
            "id":         u.id,
            "first_name": u.first_name or "",
            "last_name":  u.last_name or "",
            "email":      u.email or "",
            "department": u.department.name if u.department else "",
            "position":   u.position.name if u.position else "",
            "plans":      plans
        })

    return templates.TemplateResponse(
        "users.html",
        {
            "request":        request,
            "employees":      users,
            "employees_json": employees_json,
            "current_user":   current_user
        }
    )

# — ASSIGN PLAN — #
@router.get("/users/{user_id}/plans/add", response_class=HTMLResponse, name="add_plan_to_user_form")
async def add_plan_form(
    request: Request,
    user_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can assign plans")

    plans = (await session.execute(select(AdaptationPlan).order_by(AdaptationPlan.name))).scalars().all()
    return templates.TemplateResponse(
        "assign_plan.html",
        {"request": request, "user_id": user_id, "plans": plans}
    )


@router.post("/users/{user_id}/plans/assign", response_class=RedirectResponse, name="assign_plan")
async def assign_plan(
    request: Request,
    user_id: int,
    plan_id: int = Form(...),
    current_user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can assign plans")

    user = await session.get(User, user_id)
    plan = await session.get(AdaptationPlan, plan_id)
    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or Plan not found")

    for stage in plan.stages:
        session.add(UserAdaptationProgress(
            user_id=user_id,
            stage_id=stage.id,
            status=ProgressStatus.PENDING
        ))
    await session.commit()

    return RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)


# — VIEW PROGRESS — #
@router.get("/users/{user_id}/progress/{plan_id}", response_class=HTMLResponse, name="view_progress")
async def view_progress(
    request: Request,
    user_id: int,
    plan_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    stmt = (
        select(UserAdaptationProgress)
        .options(
            joinedload(UserAdaptationProgress.stage)
            .joinedload(AdaptationStage.plan)
        )
        .where(UserAdaptationProgress.user_id == user_id)
        .order_by(UserAdaptationProgress.id)
    )
    progress = (await session.execute(stmt)).scalars().all()

    return templates.TemplateResponse(
        "user_progress.html",
        {
            "request": request,
            "progress": progress,
            "user_id":  user_id,
            "plan_id":  plan_id
        }
    )


# ─── ADD EMPLOYEE ────────────────────────────────────────────────
@router.get("/users/add", response_class=HTMLResponse, name="add_employee_form")
async def add_employee_form(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can add employees")

    departments = (await session.execute(select(Department))).scalars().all()
    positions   = (await session.execute(select(Positions))).scalars().all()

    return templates.TemplateResponse(
        "user_form.html",
        {
            "request":     request,
            "user":        None,
            "departments": departments,
            "positions":   positions,
            "action_url":  request.url_for("create_employee")
        }
    )


@router.post("/users/add", response_class=RedirectResponse, name="create_employee")
async def create_employee(
    request: Request,
    first_name: str       = Form(...),
    last_name: str        = Form(...),
    username: str         = Form(...),
    email: str            = Form(...),
    password: str         = Form(...),
    department_id: Optional[int] = Form(None),
    position_id:   Optional[int] = Form(None),
    current_user:  User         = Depends(get_current_user_from_cookie),
    session:       AsyncSession = Depends(get_session)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can add employees")

    exists = await session.execute(
        select(User).where((User.username == username) | (User.email == email))
    )
    if exists.scalar_one_or_none():
        return templates.TemplateResponse(
            "user_form.html",
            {
                "request":     request,
                "user":        None,
                "error":       "Username or email already taken",
                "departments": (await session.execute(select(Department))).scalars().all(),
                "positions":   (await session.execute(select(Positions))).scalars().all(),
                "action_url":  request.url_for("create_employee")
            }
        )

    hashed = pwd_context.hash(password)
    new_user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        username=username.strip(),
        email=email.strip(),
        hashed_password=hashed,
        is_active=True,
        role=UserRole.EMPLOYEE,
        registration_date=datetime.utcnow()  # устанавливаем вручную
    )

    if department_id:
        dep = await session.get(Department, department_id)
        if not dep:
            raise HTTPException(status_code=400, detail="Invalid department")
        new_user.department = dep

    if position_id:
        pos = await session.get(Positions, position_id)
        if not pos:
            raise HTTPException(status_code=400, detail="Invalid position")
        new_user.position = pos

    session.add(new_user)
    await session.commit()

    return RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)
