from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.project import Project
from app.models.character import Character
from app.models.world_setting import WorldSetting
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.post("/", response_model=ProjectResponse, summary="创建项目")
def create_project(project: ProjectCreate, user_id: int = 1, db: Session = Depends(get_db)):
    """创建新的小说项目"""
    # TODO: 从JWT token中获取user_id
    db_project = Project(**project.model_dump(), user_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/", response_model=ProjectListResponse, summary="获取项目列表")
def get_projects(
    skip: int = 0,
    limit: int = 10,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """获取用户的项目列表"""
    # TODO: 从JWT token中获取user_id
    projects = db.query(Project).filter(Project.user_id == user_id).offset(skip).limit(limit).all()
    total = db.query(Project).filter(Project.user_id == user_id).count()
    return {"projects": projects, "total": total}


@router.get("/{project_id}", response_model=ProjectResponse, summary="获取项目详情")
def get_project(project_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """获取项目详情"""
    # TODO: 从JWT token中获取user_id
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )

    return project


@router.put("/{project_id}", response_model=ProjectResponse, summary="更新项目")
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """更新项目信息"""
    # TODO: 从JWT token中获取user_id
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )

    # 更新项目信息
    for field, value in project_update.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", summary="删除项目")
def delete_project(project_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """删除项目"""
    # TODO: 从JWT token中获取user_id
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )

    db.delete(project)
    db.commit()
    return {"message": "项目已删除"}
