from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exception_handler import BusinessException, NotFoundException
from app.core.logger import logger
from app.models.chapter import Chapter
from app.models.content_generation_draft import ContentGenerationDraft
from app.models.project import Project
from app.models.user import User
from app.schemas.chapter import ChapterCreate, ChapterUpdate, ChapterResponse, ChapterListResponse
from app.schemas.content_generation import (
    ChapterGenerateRequest, ChapterGenerateResponse,
    GeneratedVersion, ContextUsed, SelectVersionRequest
)
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


@router.post("/generate", summary="统一章节生成")
def generate_chapter_versions(
    request: ChapterGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    统一的章节生成端点，支持首章和续写模式

    Args:
        request: 生成请求，包含生成模式和相关参数
        current_user: 当前认证用户
        db: 数据库会话

    Returns:
        ChapterGenerateResponse: 包含生成的版本列表
    """
    # 验证项目所有权
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise NotFoundException("项目不存在")

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问该项目"
        )

    # 验证章节号是否超出范围
    existing_chapters = db.query(Chapter).filter(
        Chapter.project_id == request.project_id
    ).count()

    if request.chapter_number > existing_chapters + 1:
        raise BusinessException(
            f"章节号超出范围，当前最多可创建第{existing_chapters + 1}章"
        )

    # 转换请求数据为字典格式
    request_dict = request.model_dump()

    # 生成多个版本
    try:
        versions, context_used = ai_service.generate_chapter_versions(request_dict, db)

        # 删除旧的草稿
        db.query(ContentGenerationDraft).filter(
            ContentGenerationDraft.chapter_id == request.chapter_number
        ).delete(synchronize_session=False)

        # 保存新版本到草稿表
        for version in versions:
            draft = ContentGenerationDraft(
                chapter_id=request.chapter_number,
                version_id=version["version_id"],
                content=version["content"],
                word_count=version["word_count"],
                summary=version["summary"],
                generation_mode=request_dict.get("mode", "standard"),
                temperature=request_dict.get("temperature")
            )
            db.add(draft)

        db.commit()

        # 构建响应数据
        response_data = {
            "chapter_id": request.chapter_number,
            "versions": [
                {
                    "version_id": v["version_id"],
                    "content": v["content"],
                    "word_count": v["word_count"],
                    "summary": v["summary"]
                }
                for v in versions
            ],
            "context_used": context_used
        }

        return ChapterGenerateResponse(
            code=200,
            message="生成成功",
            data=response_data
        )

    except Exception as e:
        logger.error(f"章节生成失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失败: {str(e)}"
        )


@router.post("/{chapter_id}/select-version", summary="选择版本")
def select_version(
    chapter_id: int,
    request: SelectVersionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    选择并应用特定的生成版本

    Args:
        chapter_id: 章节ID
        request: 版本选择请求
        current_user: 当前认证用户
        db: 数据库会话

    Returns:
        更新后的章节信息
    """
    # 获取章节并验证权限
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException("章节不存在")

    # 验证项目所有权
    if chapter.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问该章节"
        )

    # 查找指定的版本
    draft = db.query(ContentGenerationDraft).filter(
        ContentGenerationDraft.chapter_id == chapter_id,
        ContentGenerationDraft.version_id == request.version_id
    ).first()

    if not draft:
        raise NotFoundException("指定的版本不存在")

    # 更新章节内容
    content_to_use = request.edited_content if request.edited_content else draft.content
    chapter.content = content_to_use
    chapter.word_count = len(content_to_use)
    chapter.status = chapter.__class__.status.DRAFT
    chapter.version = chapter.version + 1

    # 标记选中的版本
    draft.is_selected = True

    # 取消其他版本的选中状态
    db.query(ContentGenerationDraft).filter(
        ContentGenerationDraft.chapter_id == chapter_id,
        ContentGenerationDraft.id != draft.id
    ).update({"is_selected": False})

    db.commit()
    db.refresh(chapter)

    logger.info(f"章节 {chapter_id} 选择版本成功: {request.version_id}")

    return {
        "code": 200,
        "message": "选择成功",
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


@router.get("/{chapter_id}/drafts", summary="获取生成版本列表")
def get_generation_drafts(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取章节的所有生成版本

    Args:
        chapter_id: 章节ID
        current_user: 当前认证用户
        db: 数据库会话

    Returns:
        所有生成版本的列表
    """
    # 获取章节并验证权限
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException("章节不存在")

    # 验证项目所有权
    if chapter.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问该章节"
        )

    # 获取所有草稿
    drafts = db.query(ContentGenerationDraft).filter(
        ContentGenerationDraft.chapter_id == chapter_id
    ).order_by(ContentGenerationDraft.created_at.desc()).all()

    # 转换为响应格式
    draft_list = []
    for draft in drafts:
        draft_list.append({
            "id": draft.id,
            "version_id": draft.version_id,
            "content": draft.content,
            "word_count": draft.word_count,
            "summary": draft.summary,
            "is_selected": draft.is_selected,
            "generation_mode": draft.generation_mode,
            "temperature": float(draft.temperature) if draft.temperature else None,
            "created_at": draft.created_at.isoformat() if draft.created_at else None,
        })

    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "chapter_id": chapter_id,
            "drafts": draft_list,
            "total": len(draft_list)
        }
    }
