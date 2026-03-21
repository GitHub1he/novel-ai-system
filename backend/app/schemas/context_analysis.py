from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ContextAnalysisRequest(BaseModel):
    """章节上下文分析请求"""
    project_id: int
    plot_direction: Optional[str] = None
    previous_chapter_id: Optional[int] = None
    chapter_number: int

    @field_validator('project_id')
    @classmethod
    def positive_project_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('项目ID必须大于0')
        return v

    @field_validator('chapter_number')
    @classmethod
    def positive_chapter_number(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('章节号必须大于0')
        return v


class CharacterSuggestion(BaseModel):
    """角色建议"""
    id: int
    name: str
    role: str
    personality: Optional[str] = ""
    core_motivation: Optional[str] = ""
    age: Optional[int] = None
    gender: Optional[str] = None
    appearance: Optional[str] = ""
    identity: Optional[str] = ""


class WorldSettingSuggestion(BaseModel):
    """世界观设定建议"""
    id: int
    name: str
    type: str
    description: Optional[str] = ""
    attributes: Optional[Dict[str, Any]] = {}
    is_core_rule: bool

    @field_validator('attributes')
    @classmethod
    def validate_attributes(cls, v):
        """确保attributes是字典类型，如果是字符串则解析为JSON"""
        if v is None:
            return {}
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except:
                return {}
        return v


class PlotNodeSuggestion(BaseModel):
    """情节节点建议"""
    id: int
    title: str
    type: str
    importance: str
    description: Optional[str] = ""
    conflict_points: Optional[str] = ""
    theme_tags: Optional[List[str]] = []
    sequence_number: Optional[int] = None


class ContextAnalysisResponse(BaseModel):
    """章节上下文分析响应"""
    project_id: int
    chapter_number: int
    plot_direction: Optional[str] = None
    validated_characters: List[CharacterSuggestion]
    validated_world_settings: List[WorldSettingSuggestion]
    validated_plot_nodes: List[PlotNodeSuggestion]

    # 添加一个用于统一响应格式的包装器方法
    def to_api_response(self) -> Dict[str, Any]:
        """转换为统一的API响应格式"""
        return {
            "code": 200,
            "message": "上下文分析完成",
            "data": {
                "project_id": self.project_id,
                "chapter_number": self.chapter_number,
                "plot_direction": self.plot_direction,
                "validated_characters": self.validated_characters,
                "validated_world_settings": self.validated_world_settings,
                "validated_plot_nodes": self.validated_plot_nodes
            }
        }