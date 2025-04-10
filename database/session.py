import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager
from database.models.base import Base
# Импортируем модели, чтобы они зарегистрировались в Base.metadata
import database.models.users
import database.models.departments  
import database.models.positions 
import database.models.adaptation 
import database.models.content
import database.models.tests 
import database.models.feedback 
import database.models.notifications  

# Получаем URL базы данных из переменных окружения или используем значение по умолчанию
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///tasks.db")

# Настройки для SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Создаем асинхронный движок с оптимизированными настройками
engine = create_async_engine(
    DATABASE_URL,
    echo=os.environ.get("SQL_ECHO", "").lower() in ("true", "1"),  # Логирование SQL-запросов
    pool_pre_ping=True,  # Проверка соединений перед использованием
    pool_recycle=3600,   # Переиспользование соединений через час
    connect_args=connect_args
)

# Создаем фабрику асинхронных сессий
async_session = async_sessionmaker(
    engine, 
    expire_on_commit=False,  # Не сбрасывать атрибуты объектов после commit
    class_=AsyncSession       # Указываем класс сессии
)

@asynccontextmanager
async def get_session():

    session = async_session()
    try:
        yield session
    finally:
        await session.close()

# Псевдоним для get_session для обратной совместимости
new_session = get_session

async def create_tables():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def delete_tables():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def init_db():
    await create_tables()
    # Здесь можно добавить код для начальной миграции/наполнения данными
