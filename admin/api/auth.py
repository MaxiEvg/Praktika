import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .templating import templates
from database.models import User, UserRole
from db_helper import db_helper

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Настройки JWT
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


async def get_session() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exception
    return user


# ─── Маршрут токена для SPA или API ────────────────────────────────────────────
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# ─── Веб-страницы: вход и регистрация ────────────────────────────────────────────
@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверное имя пользователя или пароль"
        })
    # Сохраняем дату последнего входа
    user.last_login = datetime.utcnow()
    await session.commit()
    # Выполняем редирект на защищённую страницу
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    # При SSR можно хранить токен в куки
    access_token = create_access_token({"sub": user.username})
    response.set_cookie("access_token", f"Bearer {access_token}", httponly=True)
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@router.post("/register", response_class=HTMLResponse)
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    if password != password_confirm:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Пароли не совпадают"
        })

    # Проверяем занятость логина/почты
    existing = await session.execute(select(User).where((User.username == username) | (User.email == email)))
    if existing.scalar_one_or_none():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Имя пользователя или email уже заняты"
        })

    # Создаём админа (регистрируются как ADMIN по умолчанию)
    new_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        is_active=True,
        role=UserRole.ADMIN.value,        # именно .value = "admin"
        registration_date=datetime.utcnow().date(),
    )
    session.add(new_user)
    await session.commit()

    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


# ─── Регистрация через Telegram-бота ────────────────────────────────────────────
@router.post("/telegram/register")
async def telegram_register(
    telegram_id: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(None),
    username: str = Form(None),
    session: AsyncSession = Depends(get_session),
):
    # Если уже есть, просто возвращаем ОК
    existing = await session.execute(select(User).where(User.telegram_id == telegram_id))
    if existing.scalar_one_or_none():
        return {"status": "already_registered"}

    new_emp = User(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name or "",
        username=username or "",
        is_active=True,
        role=UserRole.EMPLOYEE.value,
        registration_date=datetime.utcnow().date(),
    )
    session.add(new_emp)
    await session.commit()
    return {"status": "registered"}
