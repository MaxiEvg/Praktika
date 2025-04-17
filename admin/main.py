import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from core.config import settings
from api import router as api_router
from db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_helper.create_tables()
    yield
    await db_helper.dispose()
    print("Engine disposed")

main_app = FastAPI(
    title="Система адаптации сотрудников",
    description="API для управления процессом адаптации новых сотрудников",
    version="0.1.0",
    lifespan=lifespan
)

main_app.mount("/static", StaticFiles(directory="static"), name="static")
main_app.include_router(
    api_router,
    prefix=settings.api.prefix,
)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True
    )