import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем .env из корня проекта
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Settings:
    # Telegram
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    EXPERT_TELEGRAM_ID: int = int(os.getenv("EXPERT_TELEGRAM_ID", 0))
    
    # Ollama (локальная LLM вместо OpenAI)
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    
    # Базы данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/expert_bot")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Админка
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH: str = os.getenv("ADMIN_PASSWORD_HASH", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-secret-key-minimum-32-characters")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # RAG настройки
    RAG_SIMILARITY_THRESHOLD: int = int(os.getenv("RAG_SIMILARITY_THRESHOLD", 85))
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # Поведение бота
    MAX_QUESTION_LENGTH: int = int(os.getenv("MAX_QUESTION_LENGTH", 1000))
    BOT_SEND_TYPING: bool = True

settings = Settings()

# Проверка обязательных переменных
if not settings.BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env")
if not settings.EXPERT_TELEGRAM_ID:
    raise ValueError("EXPERT_TELEGRAM_ID не задан в .env")
