from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    title: str
    author: str
    genre: str
    summary: Optional[str] = None
    target_readers: Optional[str] = None
    default_pov: Optional[str] = None
    style: Optional[str] = None
    target_words_per_chapter: int = 2000


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
    target_words_per_chapter: Optional[int] = None
    background_template: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    tags: Optional[str] = None
    background_template: Optional[str] = None
    status: ProjectStatus
    total_words: int
    total_chapters: int
    completion_rate: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
