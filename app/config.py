from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    base_url: str = "http://localhost:8000"
    short_id_length: int = 7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()