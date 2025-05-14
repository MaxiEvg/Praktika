import logging
from typing import Optional
from fastapi import (
    APIRouter, Depends, Request,
    HTTPException, Form, status
)
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_current_user_from_cookie
from .templating import templates
from database.models import User, Department, Positions
from db_helper import db_helper

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Users"])

async def get_session() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

@router.get("/profile", response_class=HTMLResponse, name="user_profile")
async def get_profile(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(User)
        .options(joinedload(User.department), joinedload(User.position))
        .where(User.id == user.id)
    )
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": {
                "username": db_user.username,
                "full_name": f"{db_user.first_name} {db_user.last_name}",
                "email": db_user.email,
                "role": db_user.role.value,
                "department": db_user.department.name if db_user.department else "",
                "position": db_user.position.name if db_user.position else ""
            }
        }
    )

@router.get("/profile/edit", response_class=HTMLResponse, name="edit_profile_form")
async def edit_profile_form(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    departments = (await session.execute(select(Department))).scalars().all()
    positions = (await session.execute(select(Positions))).scalars().all()

    return templates.TemplateResponse(
        "profile_edit.html",
        {
            "request": request,
            "user": user,
            "departments": departments,
            "positions": positions
        }
    )

@router.post("/profile/update", response_class=RedirectResponse)
async def update_profile(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    department_id: Optional[int] = Form(None),
    position_id: Optional[int] = Form(None),
    new_department: Optional[str] = Form(None),
    new_position: Optional[str] = Form(None),
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session)
):
    try:
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if new_department:
            department = Department(name=new_department.strip())
            session.add(department)
            await session.flush()
            user.department = department
        elif department_id:
            department = await session.get(Department, department_id)
            if not department:
                raise HTTPException(status_code=400, detail="Invalid department")
            user.department = department

        if new_position:
            position = Positions(name=new_position.strip())
            session.add(position)
            await session.flush()
            user.position = position
        elif position_id:
            position = await session.get(Positions, position_id)
            if not position:
                raise HTTPException(status_code=400, detail="Invalid position")
            user.position = position

        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )

    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
