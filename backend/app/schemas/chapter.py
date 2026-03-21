from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.chapter import ChapterStatus


class ChapterBase(BaseModel):
    project_id: int
    title: str
    chapter_number: int

    @field_validator('title')
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('章节标题不能为空')
        return v.strip()

    @field_validator('chapter_number')
    @classmethod
    def positive_number(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('章节号必须大于0')
        return v


class ChapterCreate(ChapterBase):
    outline: Optional[str] = None
    summary: Optional[str] = None
    volume: Optional[str] = None
    pov_character_id: Optional[int] = None


class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    outline: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[ChapterStatus] = None


class ChapterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    chapter_number: int
    title: str
    volume: Optional[str] = None
    content: Optional[str] = None
    outline: Optional[str] = None
    summary: Optional[str] = None
    pov_character_id: Optional[int] = None
    featured_characters: Optional[str] = None
    locations: Optional[str] = None
    status: str
    word_count: int
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ChapterListResponse(BaseModel):
    chapters: list[ChapterResponse]
    total: int
