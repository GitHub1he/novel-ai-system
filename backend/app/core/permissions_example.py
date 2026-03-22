"""
统一权限检查使用示例

展示如何重构 API 代码，使用统一的权限检查依赖
"""

# ============================================
# 重构前（在每个接口都写权限判断）
# ============================================
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project

@router.get("/detail/{project_id}")
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 获取项目
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException("项目不存在")

    # 检查权限（每个接口都要写这些代码！）
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问该项目"
        )

    # 业务逻辑...
    return {"code": 200, "data": project}
"""

# ============================================
# 重构后（使用统一权限检查）
# ============================================
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import get_project, require_project
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectUpdate

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.get("/detail/{project_id}", summary="获取项目详情")
def get_project_detail(
    project: Project = Depends(get_project),  # 自动权限检查！
    current_user: User = Depends(get_current_user)
):
    """
    获取项目详情
    - 管理员可访问任何项目
    - 普通用户只能访问自己的项目
    """
    # 业务逻辑（权限已经检查过了，直接使用）
    return {
        "code": 200,
        "message": "获取成功",
        "data": project
    }


@router.post("/update/{project_id}", summary="更新项目")
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    project: Project = Depends(require_project),  # 要求所有权！
    db: Session = Depends(get_db)
):
    """
    更新项目信息
    - 管理员可更新任何项目
    - 普通用户只能更新自己的项目
    """
    # 业务逻辑
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return {
        "code": 200,
        "message": "更新成功",
        "data": project
    }


# ============================================
# 章节权限检查示例
# ============================================
from app.core.permissions import get_chapter, require_chapter
from app.models.chapter import Chapter
from app.schemas.chapter import ChapterUpdate

chapter_router = APIRouter(prefix="/chapters", tags=["章节管理"])


@chapter_router.get("/{chapter_id}", summary="获取章节详情")
def get_chapter_detail(
    chapter: Chapter = Depends(get_chapter),  # 自动通过项目检查权限！
):
    """
    获取章节详情
    - 自动通过 chapter.project_id 检查项目权限
    - 管理员可访问任何章节
    - 普通用户只能访问自己项目的章节
    """
    return {
        "code": 200,
        "message": "获取成功",
        "data": chapter
    }


@chapter_router.put("/{chapter_id}", summary="更新章节")
def update_chapter(
    chapter_id: int,
    chapter_update: ChapterUpdate,
    chapter: Chapter = Depends(require_chapter),  # 要求项目所有权！
    db: Session = Depends(get_db)
):
    """
    更新章节内容
    - 自动检查项目权限
    - chapter.project 已经预加载，无需重复查询
    """
    update_data = chapter_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chapter, field, value)

    db.commit()
    db.refresh(chapter)

    return {
        "code": 200,
        "message": "更新成功",
        "data": chapter
    }


# ============================================
# 列表查询示例（需要自定义权限检查）
# ============================================
@router.get("/list/{project_id}", summary="获取章节列表")
def list_chapters(
    project_id: int,
    project: Project = Depends(get_project),  # 先检查项目权限
    db: Session = Depends(get_db)
):
    """
    获取项目的章节列表
    - 使用 get_project 依赖确保有权限访问该项目
    - 然后查询该项目的章节
    """
    from app.models.chapter import Chapter

    chapters = db.query(Chapter).filter(
        Chapter.project_id == project_id
    ).order_by(Chapter.chapter_number).all()

    total = db.query(Chapter).filter(
        Chapter.project_id == project_id
    ).count()

    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "chapters": chapters,
            "total": total
        }
    }


# ============================================
# 创建资源示例（需要先检查项目所有权）
# ============================================
from app.schemas.chapter import ChapterCreate

@chapter_router.post("/", summary="创建章节")
def create_chapter(
    chapter_data: ChapterCreate,
    project: Project = Depends(require_project),  # 要求项目所有权！
    db: Session = Depends(get_db)
):
    """
    创建新章节
    - 使用 require_project 确保用户有权在该项目中创建章节
    - 管理员可在任何项目中创建
    - 普通用户只能在自己的项目中创建
    """
    # 检查章节号是否已存在
    existing = db.query(Chapter).filter(
        Chapter.project_id == chapter_data.project_id,
        Chapter.chapter_number == chapter_data.chapter_number
    ).first()

    if existing:
        raise BusinessException("该章节号已存在")

    chapter = Chapter(**chapter_data.model_dump())
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    return {
        "code": 200,
        "message": "创建成功",
        "data": chapter
    }


# ============================================
# 删除资源示例
# ============================================
@chapter_router.delete("/{chapter_id}", summary="删除章节")
def delete_chapter(
    chapter: Chapter = Depends(require_chapter),  # 要求项目所有权！
    db: Session = Depends(get_db)
):
    """
    删除章节
    - 使用 require_chapter 确保有权限删除
    - 管理员可删除任何章节
    - 普通用户只能删除自己项目的章节
    """
    db.delete(chapter)
    db.commit()

    return {
        "code": 200,
        "message": "删除成功",
        "data": None
    }


# ============================================
# 对比总结
# ============================================
"""
重构前：
- 每个接口 5-10 行权限检查代码
- 权限逻辑分散在各个接口
- 修改权限规则需要改所有接口
- 容易出现权限检查遗漏

重构后：
- 每个接口 1 行依赖注入
- 权限逻辑集中在 permissions.py
- 修改权限规则只需改一个地方
- 不会遗漏，更安全
"""

# 代码量对比：
"""
重构前的接口（约 30 行）：
@router.get("/detail/{project_id}")
def get_project(project_id, current_user, db):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException("项目不存在")
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限")
    # ... 业务逻辑 ...

重构后的接口（约 10 行）：
@router.get("/detail/{project_id}")
def get_project(project: Project = Depends(get_project)):
    # ... 业务逻辑 ...
"""

# 性能优化：
"""
重构后，权限检查函数会预加载关联对象（如 project），
避免业务代码重复查询数据库：
"""
def get_chapter_detail(
    chapter: Chapter = Depends(get_chapter)  # chapter.project 已预加载
):
    # 不需要再次查询 chapter.project
    project_name = chapter.project.title  # 直接使用，无额外查询
    return {"chapter": chapter, "project_name": project_name}
