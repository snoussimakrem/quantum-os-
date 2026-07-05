from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from quantum_os.infrastructure.database.base import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()