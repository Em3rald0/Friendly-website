from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./walkwithfriends.db"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    YANDEX_MAPS_API_KEY: str = "your-yandex-maps-api-key"

    class Config:
        env_file = ".env"

settings = Settings()