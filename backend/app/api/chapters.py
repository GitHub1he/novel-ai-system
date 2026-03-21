from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.exception_handler import BusinessException, NotFoundException
from app.core.logger import logger
from app.models.chapter import Chapter
from app.models.project import Project
from app.schemas.chapter import ChapterCreate, ChapterUpdate, ChapterResponse, ChapterListResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/chapters", tags=["章节管理"])


@router.post("/", summary="创建章节")
def create_chapter(
    chapter_data: ChapterCreate,
    db: Session = Depends(get_db)
):
    """创建新章节"""
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == chapter_data.project_id).first()
    if not project:
        raise NotFoundException("项目不存在")

    # 检查章节号是否已存在
    existing_chapter = db.query(Chapter).filter(
        Chapter.project_id == chapter_data.project_id,
        Chapter.chapter_number == chapter_data.chapter_number
    ).first()
    if existing_chapter:
        raise BusinessException("该章节号已存在")

    try:
        chapter = Chapter(
            project_id=chapter_data.project_id,
            title=chapter_data.title,
            chapter_number=chapter_data.chapter_number,
            outline=chapter_data.outline,
            summary=chapter_data.summary,
            volume=chapter_data.volume,
            pov_character_id=chapter_data.pov_character_id
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)

        logger.info(f"创建章节成功: {chapter.title} (ID: {chapter.id})")

        # 手动转换为字典以保持响应格式一致
        return {
            "code": 200,
            "message": "创建成功",
            "data": {
                "id": chapter.id,
                "project_id": chapter.project_id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "volume": chapter.volume,
                "content": chapter.content,
                "outline": chapter.outline,
                "summary": chapter.summary,
                "pov_character_id": chapter.pov_character_id,
                "featured_characters": chapter.featured_characters,
                "locations": chapter.locations,
                "status": chapter.status.value if hasattr(chapter.status, 'value') else str(chapter.status),
                "word_count": chapter.word_count,
                "version": chapter.version,
                "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
                "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None,
            }
        }
    except ValueError as e:
        raise BusinessException(str(e))
    except Exception as e:
        raise


@router.get("/{chapter_id}", summary="获取章节详情")
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """获取章节详情（包含完整内容）"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException("章节不存在")

    # 手动转换为字典以保持响应格式一致
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "id": chapter.id,
            "project_id": chapter.project_id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "volume": chapter.volume,
            "content": chapter.content,
            "outline": chapter.outline,
            "summary": chapter.summary,
            "pov_character_id": chapter.pov_character_id,
            "featured_characters": chapter.featured_characters,
            "locations": chapter.locations,
            "status": chapter.status.value if hasattr(chapter.status, 'value') else str(chapter.status),
            "word_count": chapter.word_count,
            "version": chapter.version,
            "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
            "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None,
        }
    }


@router.put("/{chapter_id}", summary="更新章节")
def update_chapter(
    chapter_id: int,
    chapter_data: ChapterUpdate,
    db: Session = Depends(get_db)
):
    """更新章节内容"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException("章节不存在")

    try:
        if chapter_data.title is not None:
            chapter.title = chapter_data.title
        if chapter_data.content is not None:
            chapter.content = chapter_data.content
            # 更新字数统计
            chapter.word_count = len(chapter_data.content)
        if chapter_data.outline is not None:
            chapter.outline = chapter_data.outline
        if chapter_data.summary is not None:
            chapter.summary = chapter_data.summary
        if chapter_data.status is not None:
            chapter.status = chapter_data.status

        db.commit()
        db.refresh(chapter)

        logger.info(f"更新章节成功: {chapter.title} (ID: {chapter.id})")

        # 手动转换为字典以保持响应格式一致
        return {
            "code": 200,
            "message": "更新成功",
            "data": {
                "id": chapter.id,
                "project_id": chapter.project_id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "volume": chapter.volume,
                "content": chapter.content,
                "outline": chapter.outline,
                "summary": chapter.summary,
                "pov_character_id": chapter.pov_character_id,
                "featured_characters": chapter.featured_characters,
                "locations": chapter.locations,
                "status": chapter.status.value if hasattr(chapter.status, 'value') else str(chapter.status),
                "word_count": chapter.word_count,
                "version": chapter.version,
                "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
                "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None,
            }
        }
    except Exception as e:
        raise


@router.get("/list/{project_id}", summary="获取章节列表")
def list_chapters(project_id: int, db: Session = Depends(get_db)):
    """获取项目的章节列表"""
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException("项目不存在")

    chapters = db.query(Chapter).filter(
        Chapter.project_id == project_id
    ).order_by(Chapter.chapter_number).all()

    total = len(chapters)

    # 手动转换为字典以保持响应格式一致
    # 注意：章节列表不返回 content 和 outline 字段，避免大量数据传输
    chapter_list = []
    for chapter in chapters:
        chapter_dict = {
            "id": chapter.id,
            "project_id": chapter.project_id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "volume": chapter.volume,
            "summary": chapter.summary,
            "pov_character_id": chapter.pov_character_id,
            "status": chapter.status.value if hasattr(chapter.status, 'value') else str(chapter.status),
            "word_count": chapter.word_count,
            "version": chapter.version,
            "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
            "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None,
            # 标记是否有大纲和内容
            "has_outline": bool(chapter.outline),
            "has_content": bool(chapter.content),
        }
        chapter_list.append(chapter_dict)

    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "chapters": chapter_list,
            "total": total
        }
    }


@router.post("/{chapter_id}/generate", summary="AI生成章节内容")
def generate_chapter_content(
    chapter_id: int,
    prompt: str,
    db: Session = Depends(get_db)
):
    """使用AI生成章节内容"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )

    project = db.query(Project).filter(Project.id == chapter.project_id).first()

    # TODO: 构建上下文（人物、世界观设定）
    context = ai_service._build_context(
        project_data={
            "title": project.title,
            "genre": project.genre,
            "summary": project.summary,
            "style": project.style
        },
        characters=[],
        world_settings=[]
    )

    # 生成内容
    try:
        content = ai_service.generate_chapter(
            prompt=prompt,
            context=context,
            word_count=project.target_words_per_chapter,
            style=project.style
        )

        # 保存生成的内容
        chapter.content = content
        chapter.word_count = len(content)
        db.commit()

        return {"content": content, "word_count": len(content)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
