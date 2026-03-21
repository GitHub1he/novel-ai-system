from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.world_setting import SettingType
import json


class WorldSettingBase(BaseModel):
    """世界观设定基础信息"""
    name: str
    setting_type: SettingType
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('设定名称不能为空')
        return v.strip()


class WorldSettingCreate(WorldSettingBase):
    """创建世界观设定"""
    project_id: int
    attributes: Optional[Dict[str, Any]] = None  # 扩展属性，JSON格式
    related_entities: Optional[list] = None  # 关联实体ID列表
    is_core_rule: int = 0  # 是否为核心规则（不可变）
    image: Optional[str] = None


class WorldSettingUpdate(BaseModel):
    """更新世界观设定"""
    name: Optional[str] = None
    setting_type: Optional[SettingType] = None
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    related_entities: Optional[list] = None
    is_core_rule: Optional[int] = None
    image: Optional[str] = None


class WorldSettingResponse(BaseModel):
    """世界观设定响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    setting_type: str
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    related_entities: Optional[list] = None
    is_core_rule: int
    image: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class WorldSettingListResponse(BaseModel):
    """世界观设定列表响应"""
    settings: list[WorldSettingResponse]
    total: int
