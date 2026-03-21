from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.exception_handler import BusinessException, NotFoundException
from app.core.logger import logger
from app.models.project import Project
from app.models.character import Character
from app.models.world_setting import WorldSetting
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.post("/create", summary="创建项目")
def create_project(project: ProjectCreate, user_id: int = 1, db: Session = Depends(get_db)):
    """创建新的小说项目"""
    # TODO: 从JWT token中获取user_id
    try:
        db_project = Project(**project.model_dump(), user_id=user_id)
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
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """获取用户的项目列表"""
    # TODO: 从JWT token中获取user_id
    try:
        projects = db.query(Project).filter(Project.user_id == user_id).offset(skip).limit(limit).all()
        total = db.query(Project).filter(Project.user_id == user_id).count()

        logger.info(f"获取项目列表成功: user_id={user_id}, count={len(projects)}, total={total}")

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
def get_project(project_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """获取项目详情"""
    # TODO: 从JWT token中获取user_id
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()

        if not project:
            raise NotFoundException(f"项目 {project_id} 不存在")

        logger.info(f"获取项目详情成功: {project.title} (ID: {project_id})")

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
    project_id: int,
    project_update: ProjectUpdate,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """更新项目信息"""
    # TODO: 从JWT token中获取user_id
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()

        if not project:
            raise NotFoundException(f"项目 {project_id} 不存在")

        # 更新项目信息
        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        db.commit()
        db.refresh(project)

        logger.info(f"更新项目成功: {project.title} (ID: {project_id})")

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
def delete_project(project_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """删除项目"""
    # TODO: 从JWT token中获取user_id
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()

        if not project:
            raise NotFoundException(f"项目 {project_id} 不存在")

        project_title = project.title
        db.delete(project)
        db.commit()

        logger.info(f"删除项目成功: {project_title} (ID: {project_id})")

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
