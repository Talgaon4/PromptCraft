import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env if exists

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/promptcraft")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
