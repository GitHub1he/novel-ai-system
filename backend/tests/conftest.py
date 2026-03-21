import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal, Base, engine
from app.models.project import Project
from app.models.chapter import Chapter
from app.models.character import Character
from app.models.content_generation_draft import ContentGenerationDraft


@pytest.fixture(scope="function")
def db():
    """
    创建测试数据库会话

    该fixture会：
    1. 在每个测试前创建所有表
    2. 提供一个数据库会话
    3. 测试完成后回滚事务并清理

    使用scope="function"确保每个测试都有干净的数据库状态。
    """
    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 创建会话
    session = SessionLocal()
    try:
        yield session
    finally:
        # 回滚当前会话的任何未提交更改
        try:
            session.rollback()
        except Exception:
            pass
        finally:
            session.close()

        # 清理：删除表中的所有数据，而不是删除表本身
        # 这样可以避免外键约束问题
        try:
            with engine.connect() as conn:
                # 禁用外键约束检查
                conn.execute(text("SET session_replication_role = replica;"))
                conn.commit()
                # 删除所有表的数据
                for table in reversed(Base.metadata.sorted_tables):
                    conn.execute(text(f"DELETE FROM {table.name}"))
                    conn.commit()
                # 重新启用外键约束检查
                conn.execute(text("SET session_replication_role = DEFAULT;"))
                conn.commit()
        except Exception:
            # 如果失败，尝试删除并重建表
            try:
                Base.metadata.drop_all(bind=engine)
                Base.metadata.create_all(bind=engine)
            except Exception:
                pass


@pytest.fixture(scope="function")
def test_project(db: Session):
    """创建测试项目"""
    project = Project(
        title="Test Project",
        author="Test Author",
        genre="测试类型",
        user_id=1
    )
    db.add(project)
    db.flush()
    return project


@pytest.fixture(scope="function")
def test_chapter(db: Session, test_project: Project):
    """创建测试章节"""
    chapter = Chapter(
        project_id=test_project.id,
        chapter_number=1,
        title="Test Chapter"
    )
    db.add(chapter)
    db.flush()
    return chapter


@pytest.fixture(scope="function")
def test_draft(db: Session, test_chapter: Chapter):
    """创建测试草稿"""
    draft = ContentGenerationDraft(
        chapter_id=test_chapter.id,
        version_id="v1",
        content="这是测试内容",
        word_count=6,
        summary="测试摘要"
    )
    db.add(draft)
    db.commit()
    return draft

