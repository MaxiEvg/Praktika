from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .templating import templates
from .auth import get_current_user_from_cookie
from db_helper import db_helper
from database.models import Test, User

router = APIRouter()

async def get_session() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

@router.get("/", response_class=RedirectResponse)
async def root(
    user: User = Depends(get_current_user_from_cookie)
):
    """
    Корневой маршрут: если авторизован — на dashboard, иначе HTTPException(401)
    Глобальный обработчик ошибок редиректит анонимных на /welcome
    """
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Test).order_by(Test.id.desc()).limit(5))
    recent_tests = result.scalars().all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "recent_tests": recent_tests
    })