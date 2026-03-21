from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.character import CharacterRole
import json


class CharacterBase(BaseModel):
    """人物基础信息"""
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    appearance: Optional[str] = None  # 外貌描述
    identity: Optional[str] = None  # 身份
    hometown: Optional[str] = None  # 籍贯

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('姓名不能为空')
        return v.strip()


class CharacterCore(BaseModel):
    """人物核心信息"""
    role: CharacterRole = CharacterRole.SUPPORTING
    personality: Optional[str] = None  # 性格标签，JSON格式
    core_motivation: Optional[str] = None  # 核心动机
    fears: Optional[str] = None  # 恐惧
    desires: Optional[str] = None  # 欲望


class CharacterArc(BaseModel):
    """人物弧光"""
    initial_state: Optional[str] = None  # 起始状态
    turning_point: Optional[str] = None  # 转折点
    final_state: Optional[str] = None  # 最终状态


class CharacterVoice(BaseModel):
    """语音风格"""
    speech_style: Optional[str] = None  # 语音风格描述
    sample_dialogue: Optional[str] = None  # 样本对话


class CharacterCreate(CharacterBase, CharacterCore, CharacterArc, CharacterVoice):
    """创建人物"""
    project_id: int
    avatar: Optional[str] = None


class CharacterUpdate(BaseModel):
    """更新人物"""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    appearance: Optional[str] = None
    identity: Optional[str] = None
    hometown: Optional[str] = None
    role: Optional[CharacterRole] = None
    personality: Optional[str] = None
    core_motivation: Optional[str] = None
    fears: Optional[str] = None
    desires: Optional[str] = None
    initial_state: Optional[str] = None
    turning_point: Optional[str] = None
    final_state: Optional[str] = None
    speech_style: Optional[str] = None
    sample_dialogue: Optional[str] = None
    avatar: Optional[str] = None


class CharacterResponse(BaseModel):
    """人物响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    appearance: Optional[str] = None
    identity: Optional[str] = None
    hometown: Optional[str] = None
    role: str
    personality: Optional[str] = None
    core_motivation: Optional[str] = None
    fears: Optional[str] = None
    desires: Optional[str] = None
    initial_state: Optional[str] = None
    turning_point: Optional[str] = None
    final_state: Optional[str] = None
    speech_style: Optional[str] = None
    sample_dialogue: Optional[str] = None
    avatar: Optional[str] = None
    appearance_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class CharacterListResponse(BaseModel):
    """人物列表响应"""
    characters: List[CharacterResponse]
    total: int
