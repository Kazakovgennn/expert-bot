from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Движок для PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # True для отладки SQL
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """Dependency для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Создание таблиц при первом запуске"""
    from db.models import Base
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # осторожно! удалит данные
        await conn.run_sync(Base.metadata.create_all)
    logger.info("База данных инициализирована, таблицы созданы")
