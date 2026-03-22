from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exception_handler import BusinessException, NotFoundException
from app.core.logger import logger
from app.core.permissions import get_project, require_project
from app.models.project import Project
from app.models.character import Character
from app.models.world_setting import WorldSetting
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.post("/create", summary="创建项目")
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的小说项目"""
    try:
        db_project = Project(**project.model_dump(), user_id=current_user.id)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)

        logger.info(f"创建项目成功: {db_project.title} (ID: {db_project.id})")

        # 手动转换为字典
        return {
            "code": 200,
            "message": "创建成功",
            "data": {
                "id": db_project.id,
                "user_id": db_project.user_id,
                "title": db_project.title,
                "author": db_project.author,
                "genre": db_project.genre,
                "summary": db_project.summary,
                "target_readers": db_project.target_readers,
                "status": db_project.status.value if hasattr(db_project.status, 'value') else str(db_project.status),
                "default_pov": db_project.default_pov,
                "style": db_project.style,
                "target_words_per_chapter": db_project.target_words_per_chapter,
                "tags": db_project.tags,
                "background_template": db_project.background_template,
                "total_words": db_project.total_words,
                "total_chapters": db_project.total_chapters,
                "completion_rate": db_project.completion_rate,
                "created_at": db_project.created_at.isoformat() if db_project.created_at else None,
                "updated_at": db_project.updated_at.isoformat() if db_project.updated_at else None,
            }
        }
    except ValueError as e:
        # 验证错误（如 Pydantic validator 抛出的 ValueError）
        raise BusinessException(str(e))
    except Exception as e:
        # 其他未知错误 - 会被全局异常处理器捕获
        raise


@router.get("/list", summary="获取项目列表")
def get_projects(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的项目列表（管理员可查看所有项目）"""
    try:
        # 添加调试日志
        logger.info(f"=== 项目列表查询 ===")
        logger.info(f"当前用户: {current_user.username} (ID: {current_user.id})")
        logger.info(f"is_admin 类型: {type(current_user.is_admin)}, 值: {current_user.is_admin}")
        logger.info(f"is_admin == 1: {current_user.is_admin == 1}")
        logger.info(f"is_admin != 0: {current_user.is_admin != 0}")

        # 构建查询：管理员可以查看所有项目，普通用户只能查看自己的
        query = db.query(Project)

        # 关键修复：is_admin 是 Integer 类型，需要正确判断
        if not (current_user.is_admin == 1):
            logger.info(f"不是管理员，只查询自己的项目 (user_id={current_user.id})")
            query = query.filter(Project.user_id == current_user.id)
        else:
            logger.info(f"是管理员，查询所有项目")

        projects = query.offset(skip).limit(limit).all()
        total = query.count()

        logger.info(f"获取项目列表成功: user_id={current_user.id}, is_admin={current_user.is_admin}, count={len(projects)}, total={total}")

        # 手动转换为字典
        project_list = []
        for p in projects:
            project_dict = {
                "id": p.id,
                "user_id": p.user_id,
                "title": p.title,
                "author": p.author,
                "genre": p.genre,
                "summary": p.summary,
                "target_readers": p.target_readers,
                "status": p.status.value if hasattr(p.status, 'value') else str(p.status),
                "default_pov": p.default_pov,
                "style": p.style,
                "target_words_per_chapter": p.target_words_per_chapter,
                "tags": p.tags,
                "background_template": p.background_template,
                "total_words": p.total_words,
                "total_chapters": p.total_chapters,
                "completion_rate": p.completion_rate,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            project_list.append(project_dict)

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "projects": project_list,
                "total": total
            }
        }
    except Exception as e:
        # 会被全局异常处理器捕获
        raise


@router.get("/detail/{project_id}", summary="获取项目详情")
def get_project_detail(
    project: Project = Depends(get_project),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目详情
    - 管理员可查看任何项目
    - 普通用户只能查看自己的项目
    """
    try:
        logger.info(f"获取项目详情成功: {project.title} (ID: {project.id})")

        # 手动转换为字典
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "id": project.id,
                "user_id": project.user_id,
                "title": project.title,
                "author": project.author,
                "genre": project.genre,
                "summary": project.summary,
                "target_readers": project.target_readers,
                "status": project.status.value if hasattr(project.status, 'value') else str(project.status),
                "default_pov": project.default_pov,
                "style": project.style,
                "target_words_per_chapter": project.target_words_per_chapter,
                "tags": project.tags,
                "background_template": project.background_template,
                "total_words": project.total_words,
                "total_chapters": project.total_chapters,
                "completion_rate": project.completion_rate,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            }
        }
    except NotFoundException:
        # 重新抛出 NotFoundException
        raise
    except Exception as e:
        # 会被全局异常处理器捕获
        raise


@router.post("/update/{project_id}", summary="更新项目")
def update_project(
    project_update: ProjectUpdate,
    project: Project = Depends(require_project),
    db: Session = Depends(get_db)
):
    """
    更新项目信息
    - 管理员可更新任何项目
    - 普通用户只能更新自己的项目
    """
    try:
        # 更新项目信息
        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        db.commit()
        db.refresh(project)

        logger.info(f"更新项目成功: {project.title} (ID: {project.id})")

        # 手动转换为字典
        return {
            "code": 200,
            "message": "更新成功",
            "data": {
                "id": project.id,
                "user_id": project.user_id,
                "title": project.title,
                "author": project.author,
                "genre": project.genre,
                "summary": project.summary,
                "target_readers": project.target_readers,
                "status": project.status.value if hasattr(project.status, 'value') else str(project.status),
                "default_pov": project.default_pov,
                "style": project.style,
                "target_words_per_chapter": project.target_words_per_chapter,
                "tags": project.tags,
                "background_template": project.background_template,
                "total_words": project.total_words,
                "total_chapters": project.total_chapters,
                "completion_rate": project.completion_rate,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            }
        }
    except NotFoundException:
        # 重新抛出 NotFoundException
        raise
    except ValueError as e:
        # 验证错误
        raise BusinessException(str(e))
    except Exception as e:
        # 会被全局异常处理器捕获
        raise


@router.post("/del/{project_id}", summary="删除项目")
def delete_project(
    project: Project = Depends(require_project),
    db: Session = Depends(get_db)
):
    """
    删除项目
    - 管理员可删除任何项目
    - 普通用户只能删除自己的项目
    """
    try:
        project_title = project.title
        db.delete(project)
        db.commit()

        logger.info(f"删除项目成功: {project_title} (ID: {project.id})")

        return {
            "code": 200,
            "message": "删除成功",
            "data": None
        }
    except NotFoundException:
        # 重新抛出 NotFoundException
        raise
    except Exception as e:
        # 会被全局异常处理器捕获
        raise
