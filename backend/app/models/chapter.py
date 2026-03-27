from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ChapterStatus(str, enum.Enum):
    DRAFT = "draft"  # 草稿
    REVISING = "revising"  # 修订中
    COMPLETED = "completed"  # 已完成


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # 章节信息
    chapter_number = Column(Integer, nullable=False)  # 章节号
    title = Column(String, nullable=False)  # 章节标题
    volume = Column(String, nullable=True)  # 所属卷

    # 内容
    content = Column(Text, nullable=True)  # 章节内容
    outline = Column(Text, nullable=True)  # 大纲
    summary = Column(Text, nullable=True)  # 续写摘要（用于生成下一章）
    display_summary = Column(Text, nullable=True)  # 展示摘要（用于页面显示）

    # 设定关联
    pov_character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)  # 视角人物
    featured_characters = Column(Text, nullable=True)  # 出场人物ID列表，JSON格式
    locations = Column(Text, nullable=True)  # 场景地点，JSON格式

    # 状态
    status = Column(Enum(ChapterStatus), default=ChapterStatus.DRAFT)
    word_count = Column(Integer, default=0)  # 字数

    # 版本
    version = Column(Integer, default=1)  # 版本号

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    project = relationship("Project", back_populates="chapters")
    pov_character = relationship("Character", foreign_keys=[pov_character_id])
