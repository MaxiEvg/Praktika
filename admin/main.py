import uvicorn
from fastapi import FastAPI
from core.config import settings
from contextlib import asynccontextmanager

from api import router as api_router
from db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_helper.create_tables()
    yield
    # shutdown
    print("dispose engine")
    await db_helper.dispose()

main_app = FastAPI(
    title="Система адаптации сотрудников",
    description="API для управления процессом адаптации новых сотрудников",
    version="0.1.0",
    lifespan=lifespan
)
main_app.include_router(
    api_router,
    prefix=settings.api.prefix,
)
if __name__ == "__main__":
    uvicorn.run("main:main_app",
                host=settings.run.host,
                port=settings.run.port,
                reload=True,
    )

