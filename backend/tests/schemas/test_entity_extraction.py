import pytest
from pydantic import ValidationError
from app.schemas.entity_extraction import (
    ExtractedCharacter,
    ExtractedWorldSetting,
    EntityExtractionResponse
)
from app.models.character import CharacterRole
from app.models.world_setting import SettingType

def test_extracted_character_valid():
    """测试有效的人物数据"""
    data = {
        "name": "张三",
        "age": 25,
        "gender": "男",
        "appearance": "身材高大",
        "identity": "剑客",
        "role": CharacterRole.SUPPORTING
    }
    character = ExtractedCharacter(**data)
    assert character.name == "张三"
    assert character.age == 25

def test_extracted_character_requires_name():
    """测试姓名为必填字段"""
    with pytest.raises(ValidationError):
        ExtractedCharacter(age=25)

def test_extracted_character_default_role():
    """测试默认角色为 SUPPORTING"""
    character = ExtractedCharacter(name="李四")
    assert character.role == CharacterRole.SUPPORTING

def test_extracted_world_setting_valid():
    """测试有效的世界观设定数据"""
    data = {
        "name": "青云剑派",
        "setting_type": SettingType.FACTION,
        "description": "著名的剑术门派"
    }
    setting = ExtractedWorldSetting(**data)
    assert setting.name == "青云剑派"
    assert setting.setting_type == SettingType.FACTION

def test_entity_extraction_response():
    """测试完整的提取响应"""
    data = {
        "characters": {"added": 5, "skipped": 2},
        "world_settings": {"added": 3, "skipped": 1}
    }
    response = EntityExtractionResponse(**data)
    assert response.characters["added"] == 5