from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from config import settings
from Database.Models.info_models import StudentInDB
from Database.Models.transaction_models import TransactionInDB

engine = create_async_engine(
    url = settings.db_url,
    echo = True
)

async def init_db():
    async with engine.begin() as async_engine:
        await async_engine.run_sync(SQLModel.metadata.create_all)

async def close_db():
    await engine.dispose()