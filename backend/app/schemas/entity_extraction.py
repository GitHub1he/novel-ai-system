from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, List
from app.models.character import CharacterRole
from app.models.world_setting import SettingType


class ExtractedCharacter(BaseModel):
    """AI 提取的人物数据"""
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    appearance: Optional[str] = None
    identity: Optional[str] = None
    hometown: Optional[str] = None
    role: CharacterRole = CharacterRole.SUPPORTING  # AI 未明确指定时的默认值
    personality: Optional[str] = None
    core_motivation: Optional[str] = None
    fears: Optional[str] = None
    desires: Optional[str] = None


class ExtractedWorldSetting(BaseModel):
    """AI 提取的世界观设定数据"""
    name: str
    setting_type: SettingType
    description: Optional[str] = None
    attributes: Optional[Dict] = None
    is_core_rule: int = 0


class EntityExtractionResponse(BaseModel):
    """实体提取响应"""
    characters: Dict[str, int]  # {"added": 5, "skipped": 2}
    world_settings: Dict[str, int]


class CreateEntitiesRequest(BaseModel):
    """批量创建实体请求"""
    characters: List[ExtractedCharacter] = []
    world_settings: List[ExtractedWorldSetting] = []