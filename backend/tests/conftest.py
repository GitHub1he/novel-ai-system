import pytest
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.project import Project
from app.models.chapter import Chapter
from app.models.character import Character
from app.models.content_generation_draft import ContentGenerationDraft


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 创建会话
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理所有表（忽略依赖对象错误）
        try:
            Base.metadata.drop_all(bind=engine)
        except Exception:
            # 忽略外键依赖导致的清理错误
            pass
        Base.metadata.create_all(bind=engine)
