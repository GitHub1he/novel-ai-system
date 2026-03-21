from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class PlotType(str, enum.Enum):
    """情节类型"""
    MEETING = "meeting"  # 相遇
    BETRAYAL = "betrayal"  # 背叛
    RECONCILIATION = "reconciliation"  # 和解
    CONFLICT = "conflict"  # 冲突
    REVELATION = "revelation"  # 揭示
    TRANSFORMATION = "transformation"  # 转变
    CLIMAX = "climax"  # 高潮
    RESOLUTION = "resolution"  # 结局
    OTHER = "other"  # 其他


class PlotImportance(str, enum.Enum):
    """情节重要程度"""
    MAIN = "main"  # 主线
    BRANCH = "branch"  # 支线
    BACKGROUND = "background"  # 背景


class PlotNode(Base):
    __tablename__ = "plot_nodes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # 基本信息
    title = Column(String, nullable=False)  # 情节标题
    description = Column(Text, nullable=True)  # 情节描述
    plot_type = Column(Enum(PlotType), default=PlotType.OTHER)  # 情节类型
    importance = Column(Enum(PlotImportance), default=PlotImportance.MAIN)  # 重要程度

    # 关联信息
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)  # 关联章节
    related_characters = Column(Text, nullable=True)  # 关联人物ID列表（JSON数组）
    related_locations = Column(Text, nullable=True)  # 关联地点ID列表（JSON数组）
    related_world_settings = Column(Text, nullable=True)  # 关联世界观ID列表（JSON数组）

    # 情节内容
    conflict_points = Column(Text, nullable=True)  # 冲突点描述
    theme_tags = Column(Text, nullable=True)  # 主题标签（JSON数组）

    # 结构信息
    sequence_number = Column(Integer, default=0)  # 顺序号（用于排序）
    parent_plot_id = Column(Integer, ForeignKey("plot_nodes.id"), nullable=True)  # 父情节节点

    # 状态
    is_completed = Column(Integer, default=0)  # 是否完成（0=未完成，1=已完成）

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    project = relationship("Project", backref="plot_nodes")
    chapter = relationship("Chapter", backref="plot_nodes")
    parent_plot = relationship("PlotNode", remote_side=[id], backref="child_plots")
