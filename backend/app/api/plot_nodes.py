from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exception_handler import NotFoundException, BusinessException
from app.core.logger import logger
from app.models.plot_node import PlotNode
from app.models.project import Project
from app.schemas.plot_node import PlotNodeCreate, PlotNodeUpdate, PlotNodeResponse, PlotNodeListResponse

router = APIRouter(prefix="/plot-nodes", tags=["情节管理"])


@router.post("/", summary="创建情节节点")
def create_plot_node(
    plot_data: PlotNodeCreate,
    db: Session = Depends(get_db)
):
    """创建新情节节点"""
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == plot_data.project_id).first()
    if not project:
        raise NotFoundException("项目不存在")

    try:
        plot_node = PlotNode(**plot_data.model_dump())
        db.add(plot_node)
        db.commit()
        db.refresh(plot_node)

        logger.info(f"创建情节节点成功: {plot_node.title} (ID: {plot_node.id})")

        # 手动转换为字典以保持响应格式一致
        return {
            "code": 200,
            "message": "创建成功",
            "data": {
                "id": plot_node.id,
                "project_id": plot_node.project_id,
                "title": plot_node.title,
                "description": plot_node.description,
                "plot_type": plot_node.plot_type.value if hasattr(plot_node.plot_type, 'value') else str(plot_node.plot_type),
                "importance": plot_node.importance.value if hasattr(plot_node.importance, 'value') else str(plot_node.importance),
                "chapter_id": plot_node.chapter_id,
                "related_characters": plot_node.related_characters,
                "related_locations": plot_node.related_locations,
                "related_world_settings": plot_node.related_world_settings,
                "conflict_points": plot_node.conflict_points,
                "theme_tags": plot_node.theme_tags,
                "sequence_number": plot_node.sequence_number,
                "parent_plot_id": plot_node.parent_plot_id,
                "is_completed": plot_node.is_completed,
                "created_at": plot_node.created_at.isoformat() if plot_node.created_at else None,
                "updated_at": plot_node.updated_at.isoformat() if plot_node.updated_at else None,
            }
        }
    except ValueError as e:
        raise BusinessException(str(e))
    except Exception as e:
        raise


@router.get("/list/{project_id}", summary="获取项目情节列表")
def list_plot_nodes(
    project_id: int,
    plot_type: str = None,
    importance: str = None,
    db: Session = Depends(get_db)
):
    """获取项目的情节节点列表"""
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException("项目不存在")

    # 构建查询
    query = db.query(PlotNode).filter(PlotNode.project_id == project_id)

    # 按类型筛选
    if plot_type:
        query = query.filter(PlotNode.plot_type == plot_type)

    # 按重要程度筛选
    if importance:
        query = query.filter(PlotNode.importance == importance)

    # 按顺序排序
    plot_nodes = query.order_by(PlotNode.sequence_number, PlotNode.created_at).all()
    total = len(plot_nodes)

    # 手动转换为字典以保持响应格式一致
    plot_node_list = []
    for node in plot_nodes:
        node_dict = {
            "id": node.id,
            "project_id": node.project_id,
            "title": node.title,
            "description": node.description,
            "plot_type": node.plot_type.value if hasattr(node.plot_type, 'value') else str(node.plot_type),
            "importance": node.importance.value if hasattr(node.importance, 'value') else str(node.importance),
            "chapter_id": node.chapter_id,
            "related_characters": node.related_characters,
            "related_locations": node.related_locations,
            "related_world_settings": node.related_world_settings,
            "conflict_points": node.conflict_points,
            "theme_tags": node.theme_tags,
            "sequence_number": node.sequence_number,
            "parent_plot_id": node.parent_plot_id,
            "is_completed": node.is_completed,
            "created_at": node.created_at.isoformat() if node.created_at else None,
            "updated_at": node.updated_at.isoformat() if node.updated_at else None,
        }
        plot_node_list.append(node_dict)

    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "plot_nodes": plot_node_list,
            "total": total
        }
    }


@router.put("/{plot_id}", summary="更新情节节点")
def update_plot_node(
    plot_id: int,
    plot_data: PlotNodeUpdate,
    db: Session = Depends(get_db)
):
    """更新情节节点"""
    plot_node = db.query(PlotNode).filter(PlotNode.id == plot_id).first()
    if not plot_node:
        raise NotFoundException("情节节点不存在")

    try:
        # 更新字段
        update_data = plot_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plot_node, field, value)

        db.commit()
        db.refresh(plot_node)

        logger.info(f"更新情节节点成功: {plot_node.title} (ID: {plot_node.id})")

        # 手动转换为字典以保持响应格式一致
        return {
            "code": 200,
            "message": "更新成功",
            "data": {
                "id": plot_node.id,
                "project_id": plot_node.project_id,
                "title": plot_node.title,
                "description": plot_node.description,
                "plot_type": plot_node.plot_type.value if hasattr(plot_node.plot_type, 'value') else str(plot_node.plot_type),
                "importance": plot_node.importance.value if hasattr(plot_node.importance, 'value') else str(plot_node.importance),
                "chapter_id": plot_node.chapter_id,
                "related_characters": plot_node.related_characters,
                "related_locations": plot_node.related_locations,
                "related_world_settings": plot_node.related_world_settings,
                "conflict_points": plot_node.conflict_points,
                "theme_tags": plot_node.theme_tags,
                "sequence_number": plot_node.sequence_number,
                "parent_plot_id": plot_node.parent_plot_id,
                "is_completed": plot_node.is_completed,
                "created_at": plot_node.created_at.isoformat() if plot_node.created_at else None,
                "updated_at": plot_node.updated_at.isoformat() if plot_node.updated_at else None,
            }
        }
    except Exception as e:
        raise


@router.post("/{plot_id}/delete", summary="删除情节节点")
def delete_plot_node(
    plot_id: int,
    db: Session = Depends(get_db)
):
    """删除情节节点"""
    plot_node = db.query(PlotNode).filter(PlotNode.id == plot_id).first()
    if not plot_node:
        raise NotFoundException("情节节点不存在")

    try:
        db.delete(plot_node)
        db.commit()

        logger.info(f"删除情节节点成功: {plot_node.title} (ID: {plot_id})")

        return {
            "code": 200,
            "message": "删除成功",
            "data": None
        }
    except Exception as e:
        raise
