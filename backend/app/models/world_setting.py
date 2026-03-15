from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class SettingType(str, enum.Enum):
    ERA = "era"  # 时代
    REGION = "region"  # 地域
    RULE = "rule"  # 规则（魔法/科技体系）
    CULTURE = "culture"  # 文化习俗
    POWER = "power"  # 权力结构
    LOCATION = "location"  # 地点
    FACTION = "faction"  # 势力
    ITEM = "item"  # 物品
    EVENT = "event"  # 历史事件


class WorldSetting(Base):
    __tablename__ = "world_settings"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # 基础信息
    name = Column(String, nullable=False)  # 设定名称
    setting_type = Column(Enum(SettingType), nullable=False)  # 设定类型
    description = Column(Text, nullable=True)  # 详细描述

    # 扩展属性（JSON格式，灵活存储不同类型的属性）
    attributes = Column(JSON, nullable=True)  # 例如：{"level": "高级", "effect": "..."}

    # 关联关系
    related_entities = Column(JSON, nullable=True)  # 关联实体ID列表
    is_core_rule = Column(Integer, default=0)  # 是否为核心规则（不可变）

    # 图片
    image = Column(String, nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    project = relationship("Project", back_populates="world_settings")
