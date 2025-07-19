from sqlalchemy.ext.asyncio import async_sessionmaker

from Database import engine

async_session_factory = async_sessionmaker(
    bind=engine
)