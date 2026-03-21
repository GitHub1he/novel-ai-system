from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class GenerationMode(str, Enum):
    """生成模式"""
    SIMPLE = "simple"
    STANDARD = "standard"
    ADVANCED = "advanced"


class TransitionType(str, Enum):
    """衔接方式"""
    IMMEDIATE = "immediate"
    TIME_SKIP = "time_skip"
    LOCATION_CHANGE = "location_change"
    SUMMARY = "summary"


class FirstChapterMode(BaseModel):
    """首章生成模式参数"""
    opening_scene: str = Field(..., description="开篇场景描述")
    key_elements: List[str] = Field(default_factory=list, description="核心要素列表")
    tone: Optional[str] = Field(None, description="开篇基调（如：悬疑、轻松、史诗）")


class ContinueMode(BaseModel):
    """续写模式参数"""
    previous_chapter_id: int = Field(..., description="上一章ID")
    transition: str = Field(default="immediate", description="衔接方式")
    plot_direction: str = Field(..., description="本章情节方向")
    conflict_point: Optional[str] = Field(None, description="核心冲突点")


class SuggestedCharacter(BaseModel):
    """AI推荐的人物"""
    id: int
    name: str
    role: str
    reason: str = Field(..., description="推荐理由")


class SuggestedWorldSetting(BaseModel):
    """AI推荐的世界观设定"""
    id: int
    name: str
    type: str
    reason: str = Field(..., description="推荐理由")


class SuggestedPlotNode(BaseModel):
    """AI推荐的情节节点"""
    id: int
    name: str
    type: str
    reason: str = Field(..., description="推荐理由")


class ContextAnalysisResponse(BaseModel):
    """上下文分析响应"""
    suggested_characters: List[SuggestedCharacter] = Field(default_factory=list)
    suggested_world_settings: List[SuggestedWorldSetting] = Field(default_factory=list)
    suggested_plot_nodes: List[SuggestedPlotNode] = Field(default_factory=list)
    summary: str = Field(..., description="分析摘要")


class ChapterGenerateRequest(BaseModel):
    """统一生成请求"""
    mode: GenerationMode = Field(default=GenerationMode.STANDARD)
    project_id: int
    chapter_number: int
    first_chapter_mode: Optional[FirstChapterMode] = None
    continue_mode: Optional[ContinueMode] = None
    suggested_context: Optional[dict] = Field(
        default=None,
        description="AI分析的上下文建议，包含characters, world_settings, plot_nodes"
    )
    featured_characters: Optional[List[int]] = Field(default_factory=list, description="登场人物ID列表")
    related_world_settings: Optional[List[int]] = Field(default_factory=list, description="相关世界观设定ID列表")
    related_plot_nodes: Optional[List[int]] = Field(default_factory=list, description="相关情节节点ID列表")
    word_count: int = Field(default=2000, ge=500, le=10000, description="目标字数")
    versions: int = Field(default=3, ge=1, le=5, description="生成版本数量")
    style_intensity: Optional[int] = Field(default=70, ge=0, le=100, description="风格强度")
    pov_character_id: Optional[int] = Field(None, description="叙事视角人物ID")
    temperature: Optional[float] = Field(default=0.8, ge=0.1, le=1.5, description="AI创造性参数")


class GeneratedVersion(BaseModel):
    """生成的版本信息"""
    version_id: str
    content: str
    word_count: int
    summary: str


class ContextUsed(BaseModel):
    """使用的上下文信息"""
    previous_chapter: Optional[dict] = None
    characters: List[str] = Field(default_factory=list)
    world_settings: List[str] = Field(default_factory=list)
    plot_nodes: List[str] = Field(default_factory=list)


class ChapterGenerateResponse(BaseModel):
    """统一生成响应"""
    code: int = Field(default=200)
    message: str = Field(default="生成成功")
    data: dict = Field(..., description="包含chapter_id, versions, context_used")


class SelectVersionRequest(BaseModel):
    """选择版本请求"""
    version_id: str = Field(..., description="要使用的版本ID")
    edited_content: Optional[str] = Field(None, description="用户编辑后的内容（可选）")


class ExtractEntitiesResponse(BaseModel):
    """实体提取响应（第二阶段）"""
    code: int = Field(default=200)
    data: dict = Field(..., description="提取的实体信息")
