from fastapi import FastAPI
from contextlib import asynccontextmanager

from Database import close_db, init_db
from Auth.auth import auth_router
from Dashboard.home import home_router
from Dashboard.profile import profile_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(home_router)