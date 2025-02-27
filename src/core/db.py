from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base
from src.core.config import settings

engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
  autocommit=False, 
  autoflush=False, 
  bind=engine,
)

async def get_db():
  async with AsyncSessionLocal() as session:
    try: 
      yield session
      await session.commit()
    except exc.SQLAlchemyError as error:
      await session.rollback()
      raise

Base = declarative_base()
