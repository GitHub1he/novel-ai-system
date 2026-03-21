from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"  # 草稿
    WRITING = "writing"  # 写作中
    COMPLETED = "completed"  # 已完成
    ARCHIVED = "archived"  # 已归档


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 基本信息
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)  # 作者名
    genre = Column(Text, nullable=False)  # 类型：支持 JSON 数组格式，如 ["玄幻","修仙","热血"]
    tags = Column(Text, nullable=True)  # 标签，JSON格式存储
    summary = Column(Text, nullable=True)  # 简介
    target_readers = Column(String, nullable=True)  # 目标读者

    # 创作设置
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    default_pov = Column(String, nullable=True)  # 默认视角
    style = Column(String, nullable=True)  # 文风预设
    style_keywords = Column(Text, nullable=True)  # 文风关键词（JSON数组）
    language_style = Column(String, nullable=True)  # 语言风格
    sensory_focus = Column(Text, nullable=True)  # 感官重点（JSON数组）
    style_intensity = Column(Integer, default=70)  # 风格匹配度(0-100)
    target_words_per_chapter = Column(Integer, default=2000)  # 每章目标字数

    # 背景模板
    background_template = Column(Text, nullable=True)  # JSON格式存储背景配置

    # 统计信息
    total_words = Column(Integer, default=0)  # 总字数
    total_chapters = Column(Integer, default=0)  # 总章节数
    completion_rate = Column(Integer, default=0)  # 完成度百分比

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="projects")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    world_settings = relationship("WorldSetting", back_populates="project", cascade="all, delete-orphan")
