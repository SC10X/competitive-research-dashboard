import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database — default relative path, can be overridden via DATABASE_URL env
    DATABASE_URL: str = f"sqlite:///{Path(__file__).parent.parent / 'data' / 'competitive_research.db'}"
    CORS_ORIGINS: str = "*"
    DATA_DIR: str = str(Path(__file__).parent.parent / "data")
    UPLOAD_DIR: str = str(Path(__file__).parent.parent / "uploads")

    # Ensure data/upload dirs exist
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
