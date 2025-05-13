from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from core.config import settings
from database.models import Base

class DatabaseHelper:
    def __init__(
            self,
            url: str,
            echo: bool = False,
            echo_pool: bool = False,
            pool_size: int = 5,
            max_overflow: int = 10,
    ):
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            connect_args={
                "server_settings": {
                    "application_name": "adaptacore",
                    "timezone": "UTC",
                },
                "command_timeout": 60,
            }
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    async def create_tables(self):
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise

db_helper = DatabaseHelper(
    url=str(settings.db.url),
    echo=True,
    echo_pool=True,
    pool_size=5,
    max_overflow=10,
)