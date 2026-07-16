import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    DB_NAME: str = "ledgerdesk_ca"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    GEMINI_API_KEY: str = ""
    UPLOAD_DIR: str = "./uploads"
    PORT: int = 8000

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
