from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ContentGenerationDraft(Base):
    """
    内容生成草稿模型 - 用于保存多个生成版本供用户选择

    该模型支持AI生成内容的版本管理，允许为同一章节生成多个版本，
    用户可以选择最满意的版本。主要功能包括：
    - 保存AI生成的多个版本（v1, v2, v3...）
    - 记录生成参数（temperature, generation_mode）
    - 标记用户选择的版本
    - 支持字数统计和摘要

    示例用法：
    ```python
    draft = ContentGenerationDraft(
        chapter_id=chapter.id,
        version_id="v1",
        content="这是AI生成的章节内容...",
        word_count=1500,
        summary="版本摘要：描述主要情节",
        generation_mode="advanced",
        temperature=0.85
    )
    ```

    注意：
    - chapter_id有CASCADE删除约束，删除章节时会自动删除相关草稿
    - 同一章节的version_id必须唯一
    - temperature值应在0.0-1.0范围内
    """
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
    temperature = Column(Numeric(3, 2), nullable=True)  # 温度参数，范围0.00-1.00

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    chapter = relationship("Chapter", backref="generation_drafts", passive_deletes="all")

    # 约束
    __table_args__ = (
        UniqueConstraint('chapter_id', 'version_id', name='uq_chapter_version'),
        CheckConstraint(
            "temperature IS NULL OR (temperature >= 0.0 AND temperature <= 1.0)",
            name="check_temperature_range"
        ),
    )

    def __repr__(self):
        return f"<ContentGenerationDraft(id={self.id}, version_id={self.version_id}, chapter_id={self.chapter_id})>"
