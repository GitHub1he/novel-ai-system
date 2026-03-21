import pytest
from sqlalchemy.orm import Session
from app.models.content_generation_draft import ContentGenerationDraft
from app.models.chapter import Chapter
from app.models.project import Project
from app.core.database import get_db


def test_create_draft(db: Session):
    """测试创建草稿记录"""
    # 创建测试项目
    project = Project(
        title="Test Project",
        author="Test Author",
        genre="测试类型",
        user_id=1
    )
    db.add(project)
    db.flush()

    # 创建测试章节
    chapter = Chapter(
        project_id=project.id,
        chapter_number=1,
        title="Test Chapter"
    )
    db.add(chapter)
    db.flush()

    # 创建草稿
    draft = ContentGenerationDraft(
        chapter_id=chapter.id,
        version_id="v1",
        content="这是测试内容",
        word_count=6,
        summary="测试摘要"
    )
    db.add(draft)
    db.commit()

    # 验证
    assert draft.id is not None
    assert draft.version_id == "v1"
    assert draft.is_selected is False


def test_unique_version_per_chapter(db: Session):
    """测试同一章节不能有相同version_id"""
    # 创建测试项目
    project = Project(
        title="Test Project",
        author="Test Author",
        genre="测试类型",
        user_id=1
    )
    db.add(project)
    db.flush()

    # 创建测试章节
    chapter = Chapter(
        project_id=project.id,
        chapter_number=1,
        title="Test Chapter"
    )
    db.add(chapter)
    db.flush()

    # 创建第一个草稿
    draft1 = ContentGenerationDraft(
        chapter_id=chapter.id,
        version_id="v1",
        content="内容1"
    )
    db.add(draft1)
    db.commit()

    # 尝试添加重复version_id
    draft2 = ContentGenerationDraft(
        chapter_id=chapter.id,
        version_id="v1",  # 重复
        content="内容2"
    )
    db.add(draft2)

    # 应该抛出IntegrityError
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        db.commit()


def test_draft_chapter_relationship(db: Session):
    """测试草稿与章节的关系"""
    # 创建测试项目
    project = Project(
        title="Test Project",
        author="Test Author",
        genre="测试类型",
        user_id=1
    )
    db.add(project)
    db.flush()

    # 创建测试章节
    chapter = Chapter(
        project_id=project.id,
        chapter_number=1,
        title="Test Chapter"
    )
    db.add(chapter)
    db.flush()

    # 创建多个草稿
    draft1 = ContentGenerationDraft(
        chapter_id=chapter.id,
        version_id="v1",
        content="内容1"
    )
    draft2 = ContentGenerationDraft(
        chapter_id=chapter.id,
        version_id="v2",
        content="内容2"
    )
    db.add(draft1)
    db.add(draft2)
    db.commit()

    # 验证关系
    assert len(chapter.generation_drafts) == 2
    assert draft1.chapter == chapter
    assert draft2.chapter == chapter


def test_multiple_drafts_per_chapter(db: Session):
    """测试一个章节可以有多个不同版本的草稿"""
    # 创建测试项目
    project = Project(
        title="Test Project",
        author="Test Author",
        genre="测试类型",
        user_id=1
    )
    db.add(project)
    db.flush()

    # 创建测试章节
    chapter = Chapter(
        project_id=project.id,
        chapter_number=1,
        title="Test Chapter"
    )
    db.add(chapter)
    db.flush()

    # 创建多个不同版本的草稿
    drafts = []
    for i in range(1, 4):
        draft = ContentGenerationDraft(
            chapter_id=chapter.id,
            version_id=f"v{i}",
            content=f"这是第{i}个版本的内容",
            word_count=10 + i,
            is_selected=(i == 2)  # 选中第二个版本
        )
        db.add(draft)
        drafts.append(draft)

    db.commit()

    # 验证
    assert len(drafts) == 3
    assert drafts[0].version_id == "v1"
    assert drafts[1].version_id == "v2"
    assert drafts[2].version_id == "v3"
    assert drafts[1].is_selected is True  # v2被选中
    assert drafts[0].is_selected is False
    assert drafts[2].is_selected is False


def test_draft_metadata_fields(db: Session):
    """测试草稿的元数据字段"""
    from decimal import Decimal

    # 创建测试项目
    project = Project(
        title="Test Project",
        author="Test Author",
        genre="测试类型",
        user_id=1
    )
    db.add(project)
    db.flush()

    # 创建测试章节
    chapter = Chapter(
        project_id=project.id,
        chapter_number=1,
        title="Test Chapter"
    )
    db.add(chapter)
    db.flush()

    # 创建包含元数据的草稿
    draft = ContentGenerationDraft(
        chapter_id=chapter.id,
        version_id="v1",
        content="内容",
        word_count=2,
        summary="这是AI生成的版本摘要",
        is_selected=True,
        generation_mode="advanced",
        temperature=Decimal("0.85")
    )
    db.add(draft)
    db.commit()

    # 验证元数据
    assert draft.generation_mode == "advanced"
    assert draft.temperature == Decimal("0.85")
    assert draft.summary == "这是AI生成的版本摘要"
    assert draft.word_count == 2
    assert draft.is_selected is True


def test_cascade_delete_chapter_deletes_drafts(db: Session):
    """测试删除章节时级联删除相关草稿"""
    from sqlalchemy import text

    # 创建测试项目
    project = Project(
        title="Test Project",
        author="Test Author",
        genre="测试类型",
        user_id=1
    )
    db.add(project)
    db.commit()

    # 创建测试章节
    chapter = Chapter(
        project_id=project.id,
        chapter_number=1,
        title="Test Chapter"
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    # 保存chapter_id在变量中，因为chapter对象会被删除
    chapter_id = chapter.id

    # 创建多个草稿
    draft1 = ContentGenerationDraft(
        chapter_id=chapter_id,
        version_id="v1",
        content="内容1"
    )
    draft2 = ContentGenerationDraft(
        chapter_id=chapter_id,
        version_id="v2",
        content="内容2"
    )
    db.add(draft1)
    db.add(draft2)
    db.commit()
    db.refresh(draft1)
    db.refresh(draft2)

    # 记录草稿ID
    draft1_id = draft1.id
    draft2_id = draft2.id

    # 验证草稿存在
    assert db.query(ContentGenerationDraft).filter_by(id=draft1_id).first() is not None
    assert db.query(ContentGenerationDraft).filter_by(id=draft2_id).first() is not None

    # 使用原生SQL删除章节（测试数据库级联删除）
    db.execute(text("DELETE FROM chapters WHERE id = :chapter_id"), {"chapter_id": chapter_id})
    db.commit()

    # 验证章节被删除
    assert db.query(Chapter).filter_by(id=chapter_id).first() is None

    # 验证草稿被级联删除
    assert db.query(ContentGenerationDraft).filter_by(id=draft1_id).first() is None, f"Draft {draft1_id} should be deleted"
    assert db.query(ContentGenerationDraft).filter_by(id=draft2_id).first() is None, f"Draft {draft2_id} should be deleted"
