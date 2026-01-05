from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


# ---------------------------
# Database setup (async)
# ---------------------------
DATABASE_URL = 'postgresql+asyncpg://postgres:9922296@localhost:5432/food'
engine = create_async_engine(DATABASE_URL, future=True)     # can add 'echo=True' for debuging, will show SQL quearies in terminal
AsyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# ---------------------------
# Dependency
# ---------------------------
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session