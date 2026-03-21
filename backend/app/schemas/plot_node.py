from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.plot_node import PlotType, PlotImportance


class PlotNodeBase(BaseModel):
    title: str
    description: Optional[str] = None
    plot_type: PlotType = PlotType.OTHER
    importance: PlotImportance = PlotImportance.MAIN

    @field_validator('title')
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('标题不能为空')
        return v.strip()


class PlotNodeCreate(PlotNodeBase):
    project_id: int
    chapter_id: Optional[int] = None
    related_characters: Optional[str] = None
    related_locations: Optional[str] = None
    related_world_settings: Optional[str] = None
    conflict_points: Optional[str] = None
    theme_tags: Optional[str] = None
    sequence_number: Optional[int] = 0
    parent_plot_id: Optional[int] = None


class PlotNodeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    plot_type: Optional[PlotType] = None
    importance: Optional[PlotImportance] = None
    chapter_id: Optional[int] = None
    related_characters: Optional[str] = None
    related_locations: Optional[str] = None
    related_world_settings: Optional[str] = None
    conflict_points: Optional[str] = None
    theme_tags: Optional[str] = None
    sequence_number: Optional[int] = None
    parent_plot_id: Optional[int] = None
    is_completed: Optional[int] = None


class PlotNodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    plot_type: str
    importance: str
    chapter_id: Optional[int] = None
    related_characters: Optional[str] = None
    related_locations: Optional[str] = None
    related_world_settings: Optional[str] = None
    conflict_points: Optional[str] = None
    theme_tags: Optional[str] = None
    sequence_number: int
    parent_plot_id: Optional[int] = None
    is_completed: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class PlotNodeListResponse(BaseModel):
    plot_nodes: List[PlotNodeResponse]
    total: int
