"""
内容生成请求和响应Schema

该模块定义了内容生成相关的所有Pydantic模型，包括：
- 内容生成请求
- 版本选择请求
- 草稿响应
- 批量操作响应
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class ContentGenerationRequest(BaseModel):
    """
    内容生成请求模型

    用于请求AI生成章节内容，支持可选参数配置生成行为。

    Attributes:
        chapter_id: 章节ID（必填）
        num_versions: 生成版本数量，默认1，最多5个版本
        generation_mode: 生成模式（simple/standard/advanced）
        temperature: 温度参数，控制创造性，范围0.0-1.0
        override_context: 是否覆盖默认上下文（自定义角色、世界观等）
        custom_context: 自定义上下文（当override_context=True时使用）

    Example:
        ```python
        request = ContentGenerationRequest(
            chapter_id=1,
            num_versions=3,
            generation_mode="advanced",
            temperature=0.85
        )
        ```
    """
    chapter_id: int = Field(..., description="章节ID", gt=0)
    num_versions: int = Field(default=1, ge=1, le=5, description="生成版本数量")
    generation_mode: Optional[str] = Field(
        default="standard",
        description="生成模式: simple(简单), standard(标准), advanced(高级)"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="温度参数，控制创造性，0.0-1.0"
    )
    override_context: bool = Field(default=False, description="是否覆盖默认上下文")
    custom_context: Optional[dict] = Field(default=None, description="自定义上下文")

    @field_validator('generation_mode')
    @classmethod
    def validate_generation_mode(cls, v: Optional[str]) -> Optional[str]:
        """验证生成模式是否合法"""
        if v is None:
            return v
        valid_modes = ["simple", "standard", "advanced"]
        if v not in valid_modes:
            raise ValueError(f'生成模式必须是以下之一: {", ".join(valid_modes)}')
        return v

    @field_validator('custom_context')
    @classmethod
    def validate_custom_context(cls, v: Optional[dict], info) -> Optional[dict]:
        """验证自定义上下文"""
        if v is not None and not info.data.get('override_context', False):
            raise ValueError('设置custom_context需要将override_context设为True')
        return v

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        """验证温度参数精度"""
        if v is not None:
            # 保留两位小数
            return round(v, 2)
        return v


class VersionSelectionRequest(BaseModel):
    """
    版本选择请求模型

    用于用户选择要发布的草稿版本。

    Attributes:
        draft_id: 草稿ID（必填）
        apply_to_chapter: 是否将选中的草稿应用到章节内容（默认True）

    Example:
        ```python
        request = VersionSelectionRequest(
            draft_id=5,
            apply_to_chapter=True
        )
        ```
    """
    draft_id: int = Field(..., description="草稿ID", gt=0)
    apply_to_chapter: bool = Field(default=True, description="是否应用到章节内容")


class ContentGenerationDraftResponse(BaseModel):
    """
    内容生成草稿响应模型

    用于返回单个草稿的详细信息。

    Attributes:
        id: 草稿ID
        chapter_id: 所属章节ID
        version_id: 版本标识（如v1, v2）
        content: 生成的完整内容
        word_count: 字数统计
        summary: 版本摘要
        is_selected: 是否被用户选中
        generation_mode: 生成模式
        temperature: 温度参数
        created_at: 创建时间

    Example:
        ```python
        response = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="这是生成的内容...",
            word_count=1500,
            summary="这是摘要",
            is_selected=False,
            generation_mode="advanced",
            temperature=0.85,
            created_at=datetime.now()
        )
        ```
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_id: int
    version_id: str
    content: str
    word_count: int
    summary: Optional[str] = None
    is_selected: bool = False
    generation_mode: Optional[str] = None
    temperature: Optional[Decimal] = None
    created_at: datetime


class ContentGenerationBatchResponse(BaseModel):
    """
    批量生成响应模型

    用于返回批量生成任务的结果。

    Attributes:
        task_id: 任务ID
        chapter_id: 章节ID
        total_versions: 总版本数
        completed_versions: 已完成版本数
        status: 任务状态（pending/in_progress/completed/failed）
        drafts: 已生成的草稿列表
        error: 错误信息（如果失败）
        created_at: 任务创建时间

    Example:
        ```python
        response = ContentGenerationBatchResponse(
            task_id="task_123",
            chapter_id=5,
            total_versions=3,
            completed_versions=2,
            status="in_progress",
            drafts=[draft1, draft2],
            created_at=datetime.now()
        )
        ```
    """
    task_id: str
    chapter_id: int
    total_versions: int
    completed_versions: int
    status: str
    drafts: List[ContentGenerationDraftResponse] = Field(default_factory=list)
    error: Optional[str] = None
    created_at: datetime


class DraftListResponse(BaseModel):
    """
    草稿列表响应模型

    用于返回某个章节的所有草稿版本。

    Attributes:
        chapter_id: 章节ID
        drafts: 草稿列表
        total: 草稿总数
        selected_draft_id: 当前选中的草稿ID（如果有）

    Example:
        ```python
        response = DraftListResponse(
            chapter_id=5,
            drafts=[draft1, draft2, draft3],
            total=3,
            selected_draft_id=2
        )
        ```
    """
    chapter_id: int
    drafts: List[ContentGenerationDraftResponse]
    total: int
    selected_draft_id: Optional[int] = None


class DraftComparisonResponse(BaseModel):
    """
    草稿对比响应模型

    用于返回多个草稿的对比信息，帮助用户选择。

    Attributes:
        chapter_id: 章节ID
        drafts: 草稿列表（包含摘要和统计信息）
        comparison: 对比摘要（突出各版本差异）

    Example:
        ```python
        response = DraftComparisonResponse(
            chapter_id=5,
            drafts=[draft1, draft2],
            comparison="v1更注重情感描写，v2情节推进更快"
        )
        ```
    """
    chapter_id: int
    drafts: List[ContentGenerationDraftResponse]
    comparison: Optional[str] = None
