from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List
import json


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Novel AI System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 数据库配置
    # 选项1: PostgreSQL (生产环境推荐)
    DATABASE_URL: str = "postgresql://novel_ai_user:novel_ai_password@localhost:5432/novel_ai_db"
    # 选项2: SQLite (开发环境，无需安装数据库)
    # DATABASE_URL: str = "sqlite:///./novel_ai.db"

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # AI配置 - 智谱AI (GLM)
    ZHIPUAI_API_KEY: Optional[str] = None  # 智谱AI API密钥
    OPENAI_API_KEY: Optional[str] = None  # 保留兼容性
    OPENAI_API_BASE: str = "https://open.bigmodel.cn/api/paas/v4/"  # 智谱AI API端点
    AI_MODEL: str = "glm-4-flash"  # 默认使用GLM-4 Flash（速度快、成本低）

    # 实体提取配置
    ENTITY_SIMILARITY_THRESHOLD: float = 0.7  # 名称相似度阈值（0-1）

    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "ws://localhost:3000",
        "ws://localhost:5173",
        "ws://127.0.0.1:5173",
        "http://localhost:8000",
        "ws://localhost:8000",
        "https://totry.vip",
        "https://www.totry.vip"
    ]

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # 尝试解析 JSON 数组
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # 如果不是 JSON，按逗号分隔
                return [origin.strip() for origin in v.split(',')]
        return v

    class Config:
        env_file = ".env"


settings = Settings()
