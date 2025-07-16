from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str
    secret_key: str
    algorithm: str
    redis_host: str
    redis_username: str
    redis_password: str
    redis_port: int

    model_config = {
        "env_file": ".env"
    }


settings = Settings() # type: ignore