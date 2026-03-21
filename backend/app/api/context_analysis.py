from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exception_handler import NotFoundException, BusinessException
from app.core.logger import logger
from app.models.user import User
from app.models.project import Project
from app.schemas.context_analysis import ContextAnalysisRequest, ContextAnalysisResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/chapters", tags=["章节上下文分析"])


@router.post("/analyze-context", summary="分析章节上下文需求")
async def analyze_context(
    request: ContextAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ContextAnalysisResponse:
    """
    分析章节上下文需求，AI智能推荐可用的角色、世界观设定和情节节点

    Args:
        request: 包含项目ID、情节方向、前一章ID和章节号的分析请求
        current_user: 当前认证用户
        db: 数据库会话

    Returns:
        ContextAnalysisResponse: 包含AI推荐的角色、世界观设定和情节节点
    """
    # 验证项目是否存在且属于当前用户
    project = db.query(Project).filter(
        Project.id == request.project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise NotFoundException(f"项目 {request.project_id} 不存在")

    logger.info(f"用户 {current_user.username} 开始分析项目 {project.title} 的上下文需求")

    try:
        # 调用AI服务分析上下文需求
        analysis_result = ai_service.analyze_context_requirements(
            project_id=request.project_id,
            previous_chapter_id=request.previous_chapter_id,
            plot_direction=request.plot_direction
        )

        logger.info(f"上下文分析完成，推荐结果：角色 {len(analysis_result['validated_characters'])} 个，"
                   f"世界观 {len(analysis_result['validated_world_settings'])} 个，"
                   f"情节节点 {len(analysis_result['validated_plot_nodes'])} 个")

        return ContextAnalysisResponse(
            project_id=request.project_id,
            chapter_number=request.chapter_number,
            plot_direction=request.plot_direction,
            validated_characters=analysis_result['validated_characters'],
            validated_world_settings=analysis_result['validated_world_settings'],
            validated_plot_nodes=analysis_result['validated_plot_nodes']
        )

    except ValueError as e:
        # AI服务配置错误
        raise BusinessException(f"AI服务未正确配置：{str(e)}")
    except Exception as e:
        # 其他错误（网络、AI调用失败等）
        logger.error(f"上下文分析失败：{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上下文分析失败：{str(e)}"
        )