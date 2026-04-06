from pydantic import BaseModel, field_validator, ConfigDict, field_serializer
from datetime import datetime
from typing import Optional, Dict, Any, Union, List
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
    attributes: Optional[Union[str, Dict[str, Any]]] = None
    related_entities: Optional[Union[str, List]] = None
    is_core_rule: Optional[int] = None
    image: Optional[str] = None

    @field_validator('attributes', mode='before')
    @classmethod
    def validate_attributes(cls, v):
        """将 attributes 字典转换为 JSON 字符串"""
        if v is None:
            return None
        if isinstance(v, dict):
            return json.dumps(v, ensure_ascii=False)
        if isinstance(v, str):
            # 如果已经是字符串，尝试解析并重新序列化以确保格式正确
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict):
                    return json.dumps(parsed, ensure_ascii=False)
            except:
                pass
            return v
        return v

    @field_validator('related_entities', mode='before')
    @classmethod
    def validate_related_entities(cls, v):
        """将 related_entities 列表转换为 JSON 字符串"""
        if v is None:
            return None
        if isinstance(v, list):
            return json.dumps(v, ensure_ascii=False)
        if isinstance(v, str):
            # 如果已经是字符串，尝试解析并重新序列化以确保格式正确
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return json.dumps(parsed, ensure_ascii=False)
            except:
                pass
            return v
        return v


class WorldSettingResponse(BaseModel):
    """世界观设定响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    setting_type: str
    description: Optional[str] = None
    attributes: Optional[Union[str, Dict[str, Any]]] = None
    related_entities: Optional[Union[str, List]] = None
    is_core_rule: int
    image: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_serializer('attributes')
    def serialize_attributes(self, value: Optional[str]) -> Optional[Dict[str, Any]]:
        """将 attributes JSON 字符串转换为字典"""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except:
                return None
        return value

    @field_serializer('related_entities')
    def serialize_related_entities(self, value: Optional[str]) -> Optional[List]:
        """将 related_entities JSON 字符串转换为列表"""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except:
                return None
        return value


class WorldSettingListResponse(BaseModel):
    """世界观设定列表响应"""
    settings: list[WorldSettingResponse]
    total: int
