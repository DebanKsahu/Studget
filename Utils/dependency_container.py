from fastapi.security import OAuth2PasswordBearer
from Utils.factory import async_session_factory

class DatabaseDependency():

    @staticmethod
    async def get_session():
        async with async_session_factory() as session:
            yield session

class AuthTokenDependency():

    oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

class DependencyContainer(
    DatabaseDependency,
    AuthTokenDependency
):
    pass