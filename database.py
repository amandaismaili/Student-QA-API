from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings

engine = create_async_engine(settings.database_url)

#all requests get a session
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_ = AsyncSession,
    expire_on_commit = False
)

class Base(DeclarativeBase):
    pass

#provides sessions for the paths
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
