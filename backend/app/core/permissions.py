"""
统一的权限检查依赖函数

类似 Spring AOP 的切面思想，将权限验证逻辑从业务接口中分离
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.chapter import Chapter
from app.models.character import Character
from app.models.world_setting import WorldSetting
from app.core.exception_handler import NotFoundException


def check_project_access(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    require_owner: bool = False
) -> Project:
    """
    检查项目访问权限

    Args:
        project_id: 项目ID
        current_user: 当前认证用户
        db: 数据库会话
        require_owner: 是否要求必须是项目所有者（False时管理员可访问）

    Returns:
        Project: 项目对象

    Raises:
        NotFoundException: 项目不存在
        HTTPException 403: 无权限访问
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException("项目不存在")

    # 管理员可访问所有项目
    # 非管理员只能访问自己的项目
    if current_user.is_admin != 1:
        if project.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限访问该项目"
            )

    return project


def check_project_ownership(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    """
    检查项目所有权（用于创建、更新、删除操作）

    Returns:
        Project: 项目对象
    """
    return check_project_access(project_id, current_user, db, require_owner=True)


def check_chapter_access(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    require_owner: bool = False
) -> Chapter:
    """
    检查章节访问权限（通过项目）

    Args:
        chapter_id: 章节ID
        current_user: 当前认证用户
        db: 数据库会话
        require_owner: 是否要求必须是项目所有者

    Returns:
        Chapter: 章节对象
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException("章节不存在")

    # 通过项目检查权限
    project = check_project_access(
        chapter.project_id,
        current_user,
        db,
        require_owner
    )

    # 将项目对象附加到章节上，避免后续重复查询
    chapter.project = project

    return chapter


def check_character_access(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    require_owner: bool = False
) -> Character:
    """
    检查人物访问权限（通过项目）
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise NotFoundException("人物不存在")

    # 通过项目检查权限
    project = check_project_access(
        character.project_id,
        current_user,
        db,
        require_owner
    )

    character.project = project
    return character


def check_world_setting_access(
    setting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    require_owner: bool = False
) -> WorldSetting:
    """
    检查世界观设定访问权限（通过项目）
    """
    setting = db.query(WorldSetting).filter(WorldSetting.id == setting_id).first()
    if not setting:
        raise NotFoundException("世界观设定不存在")

    # 通过项目检查权限
    project = check_project_access(
        setting.project_id,
        current_user,
        db,
        require_owner
    )

    setting.project = project
    return setting


# 便捷别名：用于读取操作（管理员可访问）
get_project = check_project_access
get_chapter = check_chapter_access
get_character = check_character_access
get_world_setting = check_world_setting_access

# 便捷别名：用于修改操作（要求所有权）
require_project = check_project_ownership


def require_chapter(chapter_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Chapter:
    """要求章节所有权（用于修改操作）"""
    return check_chapter_access(chapter_id, current_user, db, require_owner=True)


def require_character(character_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Character:
    """要求人物所有权（用于修改操作）"""
    return check_character_access(character_id, current_user, db, require_owner=True)


def require_world_setting(setting_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> WorldSetting:
    """要求世界观设定所有权（用于修改操作）"""
    return check_world_setting_access(setting_id, current_user, db, require_owner=True)
