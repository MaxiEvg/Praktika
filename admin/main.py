from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from database.session import init_db
from admin.routers.users import router as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("База данных инициализирована")
    yield
    # Закомментировал удаление таблиц, чтобы сохранять данные между запусками
    # await delete_tables()
    # print("База данных очищена")

app = FastAPI(
    title="Система адаптации сотрудников",
    description="API для управления процессом адаптации новых сотрудников",
    version="0.1.0",
    lifespan=lifespan
)

# Регистрация маршрутов
app.include_router(users_router)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="admin/static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, reload=True)

