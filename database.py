from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from settings import settings

engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=settings.ENVIRONMENT == "development", 
    pool_size=10, 
    max_overflow=20
)
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL, 
    echo=settings.ENVIRONMENT == "development", 
    pool_size=10, 
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
database_connection = Annotated[AsyncSession, Depends(get_db)]
