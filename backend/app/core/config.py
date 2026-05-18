import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    ENVIRONMENT: str
    DATABASE_URL: str

    OLLAMA_URL : str
    OLLAMA_MODEL: str

    FAISS_INDEX_PATH: str = os.path.join(os.path.dirname(__file__), "../../faiss_index")

    model_config = SettingsConfigDict(
        env_file = os.path.join(os.path.dirname(__file__), "../../.env"),
        extra="ignore"
    )

settings = Settings()