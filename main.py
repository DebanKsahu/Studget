from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Auth.auth import auth_router
from Dashboard.home import home_router
from Dashboard.profile import profile_router
from Database import close_db, init_db
from Database.Redis import init_redis
from Dashboard.chatbot import bot_router
from Dashboard.agent_routes import agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    app.state.redis_client = await init_redis()
    yield
    await close_db()
    await app.state.redis_client.aclose()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(home_router)
app.include_router(bot_router)
app.include_router(agent_router)