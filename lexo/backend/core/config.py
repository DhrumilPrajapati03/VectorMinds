from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    cors_origins: list[str] = ["http://localhost:3000"]

    exa_api_key: str = ""
    elevenlabs_api_key: str = ""
    wispr_api_key: str = ""
    llm_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
