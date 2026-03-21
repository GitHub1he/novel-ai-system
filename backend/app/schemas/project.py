from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List, Union
from app.models.project import ProjectStatus
import json


class ProjectBase(BaseModel):
    title: str
    author: str
    genre: Union[str, List[str]]  # 支持字符串或字符串列表
    summary: Optional[str] = None
    target_readers: Optional[str] = None
    default_pov: Optional[str] = None
    style: Optional[str] = None
    target_words_per_chapter: int = 2000

    @field_validator('title', 'author')
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('不能为空')
        return v.strip()

    @field_validator('genre', mode='before')
    @classmethod
    def validate_genre(cls, v: Union[str, List[str], None]) -> str:
        # 处理 None 值
        if v is None:
            raise ValueError('类型不能为空')

        # 如果是列表，转换为 JSON 字符串
        if isinstance(v, list):
            if not v or len(v) == 0:
                raise ValueError('类型不能为空')
            # 去重并过滤空值
            genres = [g.strip() for g in v if g and g.strip()]
            if not genres:
                raise ValueError('类型不能为空')
            return json.dumps(list(set(genres)), ensure_ascii=False)

        # 如果已经是字符串，直接返回（前端会负责解析）
        if isinstance(v, str):
            if not v.strip():
                raise ValueError('类型不能为空')
            return v

        raise ValueError('类型格式不正确')


class ProjectCreate(ProjectBase):
    tags: Optional[str] = None
    background_template: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[str] = None
    summary: Optional[str] = None
    target_readers: Optional[str] = None
    status: Optional[ProjectStatus] = None
    default_pov: Optional[str] = None
    style: Optional[str] = None
    style_keywords: Optional[str] = None
    language_style: Optional[str] = None
    sensory_focus: Optional[str] = None
    style_intensity: Optional[int] = None
    target_words_per_chapter: Optional[int] = None
    background_template: Optional[str] = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    author: str
    genre: str  # 保持为字符串（JSON 格式）
    summary: Optional[str] = None
    target_readers: Optional[str] = None
    status: str  # 改为字符串，避免枚举验证问题
    default_pov: Optional[str] = None
    style: Optional[str] = None
    target_words_per_chapter: int
    tags: Optional[str] = None
    background_template: Optional[str] = None
    total_words: int
    total_chapters: int
    completion_rate: int
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
