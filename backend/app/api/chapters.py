from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Optional, List
import asyncio
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exception_handler import BusinessException, NotFoundException
from app.core.logger import logger
from app.core.permissions import get_project, require_project, get_chapter, require_chapter
from app.models.chapter import Chapter
from app.models.content_generation_draft import ContentGenerationDraft
from app.models.project import Project
from app.models.user import User
from app.models.character import Character
from app.models.world_setting import WorldSetting
from app.schemas.chapter import ChapterCreate, ChapterUpdate, ChapterResponse, ChapterListResponse, ChapterContentGenerateRequest
from app.schemas.content_generation import (
    ChapterGenerateRequest, ChapterGenerateResponse,
    GeneratedVersion, ContextUsed, SelectVersionRequest
)
from app.services.ai_service import ai_service
from app.services.entity_extraction_service import entity_extraction_service
from app.core.websocket_manager import send_websocket_message

router = APIRouter(prefix="/chapters", tags=["章节管理"])


@router.post("/", summary="创建章节")
def create_chapter(
    chapter_data: ChapterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新章节
    - 管理员可在任何项目中创建章节
    - 普通用户只能在自己的项目中创建章节
    """
    # 验证项目权限（统一权限检查）
    project = require_project(chapter_data.project_id, current_user, db)

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
def get_chapter_detail(
    chapter: Chapter = Depends(get_chapter)
):
    """
    获取章节详情（包含完整内容）
    - 管理员可访问任何章节
    - 普通用户只能访问自己项目的章节
    """

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
            "display_summary": chapter.display_summary,
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
async def update_chapter(
    chapter_data: ChapterUpdate,
    chapter: Chapter = Depends(require_chapter),
    db: Session = Depends(get_db)
):
    """
    更新章节内容
    - 管理员可更新任何章节
    - 普通用户只能更新自己项目的章节
    """

    try:
        content_changed = False
        if chapter_data.title is not None:
            chapter.title = chapter_data.title
        if chapter_data.content is not None:
            chapter.content = chapter_data.content
            # 更新字数统计
            chapter.word_count = len(chapter_data.content)
            content_changed = True
        if chapter_data.outline is not None:
            chapter.outline = chapter_data.outline
        if chapter_data.summary is not None:
            chapter.summary = chapter_data.summary
        if chapter_data.status is not None:
            chapter.status = chapter_data.status

        # 自动生成摘要（每次保存都重新生成，并行调用）
        if content_changed and chapter.content:
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            loop = asyncio.get_event_loop()

            try:
                # 使用线程池并行执行两个同步的 AI 调用
                with ThreadPoolExecutor(max_workers=2) as executor:
                    # 提交两个任务
                    summary_future = loop.run_in_executor(
                        executor,
                        ai_service.generate_chapter_summary,
                        chapter.content,
                        chapter.title
                    )
                    display_summary_future = loop.run_in_executor(
                        executor,
                        ai_service.generate_display_summary,
                        chapter.content,
                        chapter.title
                    )

                    # 并行等待结果
                    summary, display_summary = await asyncio.gather(
                        summary_future,
                        display_summary_future
                    )

                # 更新摘要
                if summary:
                    chapter.summary = summary
                    logger.info(f"自动生成续写摘要成功: 章节 {chapter.title}")
                if display_summary:
                    chapter.display_summary = display_summary
                    logger.info(f"自动生成展示摘要成功: 章节 {chapter.title}")

            except Exception as e:
                logger.warning(f"并行生成摘要失败，降级到串行执行: {str(e)}")
                # 降级到串行执行
                try:
                    summary = ai_service.generate_chapter_summary(chapter.content, chapter.title)
                    chapter.summary = summary
                    logger.info(f"串行：生成续写摘要成功: 章节 {chapter.title}")
                except Exception as e2:
                    logger.warning(f"串行：生成续写摘要失败: {str(e2)}")

                try:
                    display_summary = ai_service.generate_display_summary(chapter.content, chapter.title)
                    chapter.display_summary = display_summary
                    logger.info(f"串行：生成展示摘要成功: 章节 {chapter.title}")
                except Exception as e2:
                    logger.warning(f"串行：生成展示摘要失败: {str(e2)}")

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
                "display_summary": chapter.display_summary,
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
def list_chapters(
    project_id: int,
    project: Project = Depends(get_project),
    db: Session = Depends(get_db)
):
    """
    获取项目的章节列表
    - 管理员可访问任何项目的章节
    - 普通用户只能访问自己项目的章节
    """

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
            "display_summary": chapter.display_summary,
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
    request: ChapterContentGenerateRequest,
    chapter: Chapter = Depends(require_chapter),
    db: Session = Depends(get_db)
):
    """
    使用AI生成章节内容
    - 管理员可为任何章节生成内容
    - 普通用户只能为自己项目的章节生成内容
    """
    # 使用预加载的项目对象
    project = chapter.project

    # 查询项目的人物和世界观设定
    characters = db.query(Character).filter(
        Character.project_id == project.id
    ).all()

    world_settings = db.query(WorldSetting).filter(
        WorldSetting.project_id == project.id
    ).all()

    logger.info(f"查询到人物: {len(characters)}个, 世界观设定: {len(world_settings)}个")

    # 构建上下文（人物、世界观设定）
    context = ai_service._build_context(
        project_data={
            "title": project.title,
            "genre": project.genre,
            "summary": project.summary,
            "style": project.style
        },
        characters=[{
            "name": c.name,
            "role": c.role.value if hasattr(c.role, 'value') else str(c.role),
            "personality": c.personality,
            "appearance": c.appearance,
            "core_motivation": c.core_motivation,
            "identity": c.identity
        } for c in characters],
        world_settings=[{
            "name": s.name,
            "type": s.setting_type.value if hasattr(s.setting_type, 'value') else str(s.setting_type),
            "description": s.description,
            "is_core": s.is_core_rule == 1
        } for s in world_settings]
    )

    logger.info(f"上下文构建完成，人物信息: {len(characters)}条，世界观: {len(world_settings)}条")

    # 生成内容
    try:
        logger.info(f"开始生成章节内容: chapter_id={chapter.id}, word_count={project.target_words_per_chapter}")
        content = ai_service.generate_chapter(
            prompt=request.prompt,
            context=context,
            word_count=project.target_words_per_chapter,
            style=project.style
        )
        logger.info(f"AI 生成完成: chapter_id={chapter.id}, content_length={len(content)}")

        # 保存生成的内容
        chapter.content = content
        chapter.word_count = len(content)
        db.commit()

        logger.info(f"章节内容已保存: chapter_id={chapter.id}")
        return {"content": content, "word_count": len(content)}
    except Exception as e:
        logger.error(f"AI 生成失败: chapter_id={chapter.id}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/generate", summary="统一章节生成")
async def generate_chapter_versions(
    request: ChapterGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    统一的章节生成端点，支持首章和续写模式

    - 管理员可在任何项目中生成章节
    - 普通用户只能在自己的项目中生成章节
    """
    # 验证项目权限（统一权限检查）
    project = require_project(request.project_id, current_user, db)

    # 验证章节号是否超出范围
    existing_chapters = db.query(Chapter).filter(
        Chapter.project_id == request.project_id
    ).count()

    if request.chapter_number > existing_chapters + 1:
        raise BusinessException(
            f"章节号超出范围，当前最多可创建第{existing_chapters + 1}章"
        )

    # 生成唯一的task_id
    task_id = str(uuid.uuid4())

    # 转换请求数据为字典格式
    request_dict = request.model_dump()

    # 处理枚举类型，转换为字符串
    if request_dict.get('mode') and hasattr(request_dict['mode'], 'value'):
        request_dict['mode'] = request_dict['mode'].value

    # 获取前一章的摘要（用于续写）
    if request.chapter_number > 1:
        previous_chapter = db.query(Chapter).filter(
            Chapter.project_id == request.project_id,
            Chapter.chapter_number == request.chapter_number - 1
        ).first()

        if previous_chapter and previous_chapter.summary:
            request_dict['previous_chapter_summary'] = previous_chapter.summary
            logger.info(f"获取到前一章摘要，章节号: {request.chapter_number - 1}")

    # 生成多个版本
    try:
        # 查询实际的章节ID（如果章节已存在）
        chapter = db.query(Chapter).filter(
            Chapter.project_id == request.project_id,
            Chapter.chapter_number == request.chapter_number
        ).first()

        # 发送开始事件
        await send_websocket_message(task_id, "started", {
            "message": "开始生成章节版本",
            "chapter_number": request.chapter_number,
            "versions_count": request_dict.get('versions', 3)
        })

        versions, context_used = await ai_service.generate_chapter_versions_async(
            request_dict, db, task_id
        )

        # 获取实际的章节ID（用于外键关联）
        actual_chapter_id = chapter.id if chapter else None

        # 如果章节不存在，需要先创建章节（用于保存草稿的外键引用）
        if not actual_chapter_id:
            # 创建一个临时章节用于存储草稿
            chapter = Chapter(
                project_id=request.project_id,
                chapter_number=request.chapter_number,
                title=f"第{request.chapter_number}章（待编辑）",
                status="draft"
            )
            db.add(chapter)
            db.flush()  # 获取ID但不提交
            actual_chapter_id = chapter.id

        # 删除旧的草稿
        db.query(ContentGenerationDraft).filter(
            ContentGenerationDraft.chapter_id == actual_chapter_id
        ).delete(synchronize_session=False)

        # 保存新版本到草稿表
        for version in versions:
            # 确保枚举类型转换为字符串
            mode_value = request_dict.get("mode", "standard")
            if hasattr(mode_value, 'value'):
                mode_value = mode_value.value

            draft = ContentGenerationDraft(
                chapter_id=actual_chapter_id,
                version_id=version["version_id"],
                content=version["content"],
                word_count=version["word_count"],
                summary=version["summary"],
                generation_mode=mode_value,
                temperature=request_dict.get("temperature")
            )
            db.add(draft)

        db.commit()

        # 发送完成事件
        await send_websocket_message(task_id, "completed", {
            "message": "章节生成完成",
            "chapter_number": request.chapter_number,
            "versions_count": len(versions)
        })

        # 构建响应数据
        response_data = {
            "chapter_id": actual_chapter_id,
            "chapter_number": request.chapter_number,
            "task_id": task_id,  # 返回task_id供WebSocket连接使用
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
        # 发送错误事件
        await send_websocket_message(task_id, "error", {
            "message": f"生成失败: {str(e)}",
            "error": str(e)
        })

        logger.error(f"章节生成失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失败: {str(e)}"
        )


@router.post("/{chapter_id}/select-version", summary="选择版本")
def select_version(
    request: SelectVersionRequest,
    chapter: Chapter = Depends(require_chapter),
    db: Session = Depends(get_db)
):
    """
    选择并应用特定的生成版本
    - 管理员可选择任何章节的版本
    - 普通用户只能选择自己项目的章节版本
    """

    # 查找指定的版本
    draft = db.query(ContentGenerationDraft).filter(
        ContentGenerationDraft.chapter_id == chapter.id,
        ContentGenerationDraft.version_id == request.version_id
    ).first()

    if not draft:
        raise NotFoundException("指定的版本不存在")

    # 更新章节内容
    content_to_use = request.edited_content if request.edited_content else draft.content
    chapter.content = content_to_use
    chapter.word_count = len(content_to_use)
    # 保持当前状态不变，或者如果需要可以设置为 draft
    # chapter.status = ChapterStatus.DRAFT
    chapter.version = chapter.version + 1

    # 自动生成摘要
    try:
        summary = ai_service.generate_chapter_summary(chapter.content, chapter.title)
        chapter.summary = summary
        logger.info(f"自动生成摘要成功: 章节 {chapter.title}")
    except Exception as e:
        logger.warning(f"自动生成摘要失败: {str(e)}")

    # 标记选中的版本
    draft.is_selected = True

    # 取消其他版本的选中状态
    db.query(ContentGenerationDraft).filter(
        ContentGenerationDraft.chapter_id == chapter.id,
        ContentGenerationDraft.id != draft.id
    ).update({"is_selected": False})

    db.commit()
    db.refresh(chapter)

    logger.info(f"章节 {chapter.id} 选择版本成功: {request.version_id}")

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
    chapter: Chapter = Depends(get_chapter),
    db: Session = Depends(get_db)
):
    """
    获取章节的所有生成版本
    - 管理员可访问任何章节的生成版本
    - 普通用户只能访问自己项目的章节生成版本
    """
    # 获取所有草稿
    drafts = db.query(ContentGenerationDraft).filter(
        ContentGenerationDraft.chapter_id == chapter.id
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


@router.delete("/{chapter_id}", summary="删除章节")
def delete_chapter(
    chapter: Chapter = Depends(require_chapter),
    db: Session = Depends(get_db)
):
    """
    删除章节
    - 管理员可删除任何章节
    - 普通用户只能删除自己项目的章节
    """
    try:
        # 记录日志
        logger.info(f"删除章节: 第{chapter.chapter_number}章《{chapter.title}》 (ID: {chapter.id})")

        # 删除章节（级联删除相关的草稿）
        db.delete(chapter)
        db.commit()

        return {
            "code": 200,
            "message": "删除成功",
            "data": None
        }
    except Exception as e:
        db.rollback()
        logger.error(f"删除章节失败: {str(e)}")
        raise BusinessException("删除失败")


@router.post("/generate-text", summary="AI生成文本（支持选中文本修改）")
def generate_text(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI生成文本，支持修改选中的文本或插入新文本

    使用结构化提示词：
    - 基础上下文（人物、世界观、情节）+ 场景特殊提示词

    Args:
        request_data: {
            chapter_id: int,
            selected_text: str (可选),
            mode: 'replace' | 'insert_before' | 'insert_after',
            position: int,
            custom_prompt: str (可选，场景特殊提示词),
            context: {
                project_id: int,
                chapter_number: int
            }
        }
    """
    try:
        chapter_id = request_data.get('chapter_id')
        selected_text = request_data.get('selected_text', '')
        mode = request_data.get('mode', 'replace')
        position = request_data.get('position', 0)
        custom_prompt = request_data.get('custom_prompt', '')
        context_data = request_data.get('context', {})

        # 查询章节
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise NotFoundException("章节不存在")

        # 权限检查
        project = db.query(Project).filter(Project.id == chapter.project_id).first()
        if not project:
            raise NotFoundException("项目不存在")

        if project.user_id != current_user.id and current_user.is_admin != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限访问此章节"
            )

        # 构建请求字典，用于调用 _build_generation_context
        # 这个方法需要 project_id, chapter_number 等字段
        request_dict = {
            'project_id': project.id,
            'chapter_number': chapter.chapter_number,
            'featured_characters': [],  # 使用项目所有人物
            'related_world_settings': [],  # 使用项目所有世界观
            'related_plot_nodes': [],  # 使用项目所有情节节点
            'word_count': len(selected_text) if selected_text else project.target_words_per_chapter // 3
        }

        # 使用 _build_generation_context 构建基础上下文
        context_str, context_used = ai_service._build_generation_context(request_dict, db)

        # 使用 _build_system_prompt 构建系统提示词
        system_prompt = ai_service._build_system_prompt(request_dict, context_str)

        # 构建场景特定的用户提示词
        user_prompt_parts = []

        # 如果是插入模式，需要获取当前章节的内容作为上下文
        if mode in ['insert_before', 'insert_after'] and chapter.content:
            # 获取光标位置前面的内容（前800字符），作为上下文
            context_before = chapter.content[:position] if position < len(chapter.content) else chapter.content
            if len(context_before) > 800:
                context_before = context_before[-800:]  # 只取最后800个字符

            if context_before.strip():
                user_prompt_parts.append("# 当前章节前文内容")
                user_prompt_parts.append(context_before.strip())
                user_prompt_parts.append("")

        if custom_prompt:
            # 使用前端传入的场景提示词（续写一段、扩展描写等）
            user_prompt_parts.append(f"# 任务说明")
            user_prompt_parts.append(custom_prompt)
            user_prompt_parts.append("")

        if selected_text:
            user_prompt_parts.append("# 要修改的原文内容")
            user_prompt_parts.append(selected_text)
            user_prompt_parts.append("")

        # 添加操作模式说明
        if mode == 'replace' and selected_text:
            user_prompt_parts.append("# 操作要求")
            user_prompt_parts.append("- 请修改/重写上述原文内容")
            user_prompt_parts.append("- 保持原有情节走向，改进文字表达")
            user_prompt_parts.append("- 字数与原文相近")
        elif mode == 'insert_before':
            user_prompt_parts.append("# 操作要求")
            user_prompt_parts.append("- 在上述内容的基础上续写一段")
            user_prompt_parts.append("- 保持情节连贯，与前面的内容自然衔接")
            user_prompt_parts.append(f"- 目标字数：约{request_dict['word_count']}字")
        elif mode == 'insert_after':
            user_prompt_parts.append("# 操作要求")
            user_prompt_parts.append("- 在上述内容后继续续写一段")
            user_prompt_parts.append("- 保持情节连贯，自然过渡")
            user_prompt_parts.append(f"- 目标字数：约{request_dict['word_count']}字")
        else:
            # 无选中文本的插入模式
            user_prompt_parts.append("# 操作要求")
            user_prompt_parts.append("- 生成新的内容")
            user_prompt_parts.append("- 与前后内容自然衔接")
            user_prompt_parts.append(f"- 目标字数：约{request_dict['word_count']}字")

        user_prompt = "\n".join(user_prompt_parts)

        # 生成内容
        logger.info(f"开始生成文本: chapter_id={chapter_id}, mode={mode}")
        logger.info(f"系统提示词长度: {len(system_prompt)}, 用户提示词长度: {len(user_prompt)}")

        generated_content = ai_service.generate_chapter(
            prompt=user_prompt,
            context=system_prompt,  # 使用系统提示词作为context
            word_count=request_dict['word_count'],
            style=project.style
        )

        logger.info(f"文本生成完成: chapter_id={chapter_id}, content_length={len(generated_content)}")

        return {
            "code": 200,
            "message": "生成成功",
            "data": {
                "content": generated_content,
                "word_count": len(generated_content),
                "mode": mode,
                "position": position
            }
        }
    except NotFoundException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文本生成失败: {str(e)}")
        raise BusinessException(f"生成失败: {str(e)}")


@router.post("/{chapter_id}/extract-entities", summary="从章节提取实体")
def extract_entities_from_chapter(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从章节内容中提取人物和世界观设定

    返回统计信息：
    - characters: {"added": 数量, "skipped": 数量}
    - world_settings: {"added": 数量, "skipped": 数量}
    """
    # 获取章节
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException("章节不存在")

    # 验证项目权限
    project = require_project(chapter.project_id, current_user, db)

    # 检查章节内容
    if not chapter.content or not chapter.content.strip():
        raise BusinessException("章节内容为空，无法提取实体")

    try:
        # 注入 AI 服务
        from app.services.ai_service import ai_service
        entity_extraction_service.ai_service = ai_service

        # 提取人物
        characters_result = entity_extraction_service.extract_characters(
            db=db,
            project_id=project.id,
            content=chapter.content
        )

        # 提取世界观设定
        settings_result = entity_extraction_service.extract_world_settings(
            db=db,
            project_id=project.id,
            content=chapter.content
        )

        # 构建响应
        message_parts = []
        if characters_result["added"] > 0:
            message_parts.append(f"{characters_result['added']} 个人物")
        if settings_result["added"] > 0:
            message_parts.append(f"{settings_result['added']} 个世界观设定")

        message_text = "、".join(message_parts) if message_parts else "未发现新实体"
        if not message_text.startswith("未"):
            message_text = f"成功添加 {message_text}"

        return {
            "code": 200,
            "message": message_text,
            "data": {
                "characters": characters_result,
                "world_settings": settings_result
            }
        }

    except Exception as e:
        logger.error(f"提取实体失败: {e}")
        raise BusinessException(f"提取实体失败: {str(e)}")


