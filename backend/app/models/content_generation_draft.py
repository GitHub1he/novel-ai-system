from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ContentGenerationDraft(Base):
    """内容生成草稿模型 - 用于保存多个生成版本供用户选择"""
    __tablename__ = "content_generation_drafts"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)

    # 版本信息
    version_id = Column(String(50), nullable=False)  # 如 "v1", "v2", "v3"
    content = Column(Text, nullable=False)  # 生成的完整内容
    word_count = Column(Integer, default=0)  # 字数统计
    summary = Column(Text, nullable=True)  # AI生成的版本摘要

    # 状态
    is_selected = Column(Boolean, default=False)  # 是否被用户选中

    # 生成元数据（可选，用于分析）
    generation_mode = Column(String(50), nullable=True)  # "simple", "standard", "advanced"
    temperature = Column(String(50), nullable=True)  # 如 "0.8", "0.85"

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    chapter = relationship("Chapter", backref="generation_drafts")

    def __repr__(self):
        return f"<ContentGenerationDraft(id={self.id}, version_id={self.version_id}, chapter_id={self.chapter_id})>"
