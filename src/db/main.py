from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from src.config import Config

# Create async engine with proper connection pool settings
engine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=True,
    future=True,
    # Connection pool settings
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_timeout=30,
    # Additional async settings
    connect_args={
        "server_settings": {"application_name": "FastAPI App"},
        "command_timeout": 60,
    }
)

# Create async session maker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function to get database session"""
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        from src.books.models import Book
        await conn.run_sync(SQLModel.metadata.create_all)

async def close_db():
    """Close database connections"""
    await engine.dispose()

async def health_check():
    """Check database connectivity"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False