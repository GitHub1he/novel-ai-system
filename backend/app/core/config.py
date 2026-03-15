from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Novel AI System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 数据库配置
    # 选项1: PostgreSQL (生产环境推荐)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/novel_ai"
    # 选项2: SQLite (开发环境，无需安装数据库)
    # DATABASE_URL: str = "sqlite:///./novel_ai.db"

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # AI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None  # 支持自定义API端点
    AI_MODEL: str = "gpt-3.5-turbo"

    # CORS配置
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()
