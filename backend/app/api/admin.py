from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.admin_dependencies import get_current_admin
from app.core.exception_handler import NotFoundException, BusinessException
from app.core.logger import logger
from app.models.user import User
from app.models.project import Project
from app.models.chapter import Chapter

router = APIRouter(prefix="/admin", tags=["管理员"])


@router.get("/users", summary="获取所有用户列表")
def get_all_users(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员获取所有用户列表"""
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        total = db.query(User).count()

        logger.info(f"管理员 {admin.username} 获取用户列表: count={len(users)}, total={total}")

        user_list = []
        for u in users:
            user_list.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "is_admin": u.is_admin,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "project_count": len(u.projects) if u.projects else 0
            })

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "users": user_list,
                "total": total
            }
        }
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        raise


@router.post("/users/{user_id}/toggle-admin", summary="切换用户管理员权限")
def toggle_user_admin(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员切换指定用户的管理员权限"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException(f"用户 {user_id} 不存在")

        # 不能修改自己的管理员权限
        if user.id == admin.id:
            raise BusinessException("不能修改自己的管理员权限")

        # 切换管理员状态
        user.is_admin = 1 if user.is_admin == 0 else 0
        db.commit()

        logger.info(f"管理员 {admin.username} 切换用户 {user.username} 的管理员权限为: {user.is_admin}")

        return {
            "code": 200,
            "message": f"已{'授予' if user.is_admin else '撤销'}管理员权限",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "is_admin": user.is_admin
            }
        }
    except NotFoundException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"切换管理员权限失败: {str(e)}")
        raise BusinessException("操作失败")


@router.post("/users/{user_id}/toggle-active", summary="启用/禁用用户")
def toggle_user_active(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员启用或禁用指定用户"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException(f"用户 {user_id} 不存在")

        # 不能禁用自己
        if user.id == admin.id:
            raise BusinessException("不能禁用自己的账号")

        # 切换激活状态
        user.is_active = 1 if user.is_active == 0 else 0
        db.commit()

        logger.info(f"管理员 {admin.username} {'启用' if user.is_active else '禁用'}了用户 {user.username}")

        return {
            "code": 200,
            "message": f"用户已{'启用' if user.is_active else '禁用'}",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "is_active": user.is_active
            }
        }
    except NotFoundException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"切换用户状态失败: {str(e)}")
        raise BusinessException("操作失败")


@router.get("/projects", summary="获取所有项目列表")
def get_all_projects(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员获取所有项目列表"""
    try:
        projects = db.query(Project).offset(skip).limit(limit).all()
        total = db.query(Project).count()

        logger.info(f"管理员 {admin.username} 获取项目列表: count={len(projects)}, total={total}")

        project_list = []
        for p in projects:
            project_list.append({
                "id": p.id,
                "user_id": p.user_id,
                "title": p.title,
                "author": p.author,
                "genre": p.genre,
                "status": p.status.value if hasattr(p.status, 'value') else str(p.status),
                "total_words": p.total_words,
                "total_chapters": p.total_chapters,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "owner_username": p.user.username if p.user else None
            })

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "projects": project_list,
                "total": total
            }
        }
    except Exception as e:
        logger.error(f"获取项目列表失败: {str(e)}")
        raise


@router.get("/stats", summary="获取系统统计信息")
def get_system_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员获取系统统计信息"""
    try:
        user_count = db.query(User).count()
        admin_count = db.query(User).filter(User.is_admin == 1).count()
        project_count = db.query(Project).count()
        chapter_count = db.query(Chapter).count()

        logger.info(f"管理员 {admin.username} 获取系统统计")

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "user_count": user_count,
                "admin_count": admin_count,
                "project_count": project_count,
                "chapter_count": chapter_count
            }
        }
    except Exception as e:
        logger.error(f"获取系统统计失败: {str(e)}")
        raise
