from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    base_url: str = "http://localhost:8000"
    short_id_length: int = 7
    postgres_password: str
    postgres_user: str
    postgres_db: str


settings = Settings()