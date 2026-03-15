from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class CharacterRole(str, enum.Enum):
    PROTAGONIST = "protagonist"  # 主角
    ANTAGONIST = "antagonist"  # 反派
    SUPPORTING = "supporting"  # 配角
    MINOR = "minor"  # 次要角色


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # 基础信息
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    appearance = Column(Text, nullable=True)  # 外貌描述
    identity = Column(String, nullable=True)  # 身份
    hometown = Column(String, nullable=True)  # 籍贯

    # 核心人设
    role = Column(Enum(CharacterRole), default=CharacterRole.SUPPORTING)
    personality = Column(Text, nullable=True)  # 性格标签，JSON格式
    core_motivation = Column(Text, nullable=True)  # 核心动机
    fears = Column(Text, nullable=True)  # 恐惧
    desires = Column(Text, nullable=True)  # 欲望

    # 人物弧光
    initial_state = Column(Text, nullable=True)  # 起始状态
    turning_point = Column(Text, nullable=True)  # 转折点
    final_state = Column(Text, nullable=True)  # 最终状态

    # 语音风格
    speech_style = Column(Text, nullable=True)  # 语音风格描述
    sample_dialogue = Column(Text, nullable=True)  # 样本对话，供AI学习

    # 头像
    avatar = Column(String, nullable=True)

    # 统计
    appearance_count = Column(Integer, default=0)  # 出场次数

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    project = relationship("Project", back_populates="characters")
