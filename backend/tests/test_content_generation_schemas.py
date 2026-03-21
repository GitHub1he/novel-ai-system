"""
测试内容生成Schema的序列化和反序列化

该测试模块验证：
- ContentGenerationRequest的验证逻辑
- VersionSelectionRequest的验证逻辑
- 所有Response模型的序列化
- 边界条件和错误处理
"""
import pytest
from datetime import datetime
from decimal import Decimal
from app.schemas.content_generation import (
    ContentGenerationRequest,
    VersionSelectionRequest,
    ContentGenerationDraftResponse,
    ContentGenerationBatchResponse,
    DraftListResponse,
    DraftComparisonResponse,
)


class TestContentGenerationRequest:
    """测试内容生成请求模型"""

    def test_valid_minimal_request(self):
        """测试最小有效请求"""
        request = ContentGenerationRequest(chapter_id=1)
        assert request.chapter_id == 1
        assert request.num_versions == 1  # 默认值
        assert request.generation_mode == "standard"  # 默认值
        assert request.temperature == 0.7  # 默认值
        assert request.override_context is False  # 默认值
        assert request.custom_context is None  # 默认值

    def test_valid_full_request(self):
        """测试完整参数请求"""
        request = ContentGenerationRequest(
            chapter_id=5,
            num_versions=3,
            generation_mode="advanced",
            temperature=0.85,
            override_context=True,
            custom_context={"characters": [1, 2]}
        )
        assert request.chapter_id == 5
        assert request.num_versions == 3
        assert request.generation_mode == "advanced"
        assert request.temperature == 0.85
        assert request.override_context is True
        assert request.custom_context == {"characters": [1, 2]}

    def test_invalid_chapter_id_zero(self):
        """测试无效的章节ID（0）"""
        with pytest.raises(ValueError) as exc_info:
            ContentGenerationRequest(chapter_id=0)
        assert "greater than 0" in str(exc_info.value)

    def test_invalid_chapter_id_negative(self):
        """测试无效的章节ID（负数）"""
        with pytest.raises(ValueError) as exc_info:
            ContentGenerationRequest(chapter_id=-1)
        assert "greater than 0" in str(exc_info.value)

    def test_valid_num_versions_boundaries(self):
        """测试num_versions的边界值"""
        # 最小值
        request1 = ContentGenerationRequest(chapter_id=1, num_versions=1)
        assert request1.num_versions == 1

        # 最大值
        request2 = ContentGenerationRequest(chapter_id=1, num_versions=5)
        assert request2.num_versions == 5

    def test_invalid_num_versions_too_small(self):
        """测试num_versions过小"""
        with pytest.raises(ValueError) as exc_info:
            ContentGenerationRequest(chapter_id=1, num_versions=0)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_invalid_num_versions_too_large(self):
        """测试num_versions过大"""
        with pytest.raises(ValueError) as exc_info:
            ContentGenerationRequest(chapter_id=1, num_versions=6)
        assert "less than or equal to 5" in str(exc_info.value)

    def test_valid_generation_modes(self):
        """测试所有有效的生成模式"""
        for mode in ["simple", "standard", "advanced"]:
            request = ContentGenerationRequest(
                chapter_id=1,
                generation_mode=mode
            )
            assert request.generation_mode == mode

    def test_invalid_generation_mode(self):
        """测试无效的生成模式"""
        with pytest.raises(ValueError) as exc_info:
            ContentGenerationRequest(chapter_id=1, generation_mode="invalid")
        assert "生成模式必须是以下之一" in str(exc_info.value)

    def test_valid_temperature_boundaries(self):
        """测试temperature的边界值"""
        # 最小值
        request1 = ContentGenerationRequest(chapter_id=1, temperature=0.0)
        assert request1.temperature == 0.0

        # 最大值
        request2 = ContentGenerationRequest(chapter_id=1, temperature=1.0)
        assert request2.temperature == 1.0

        # 中间值
        request3 = ContentGenerationRequest(chapter_id=1, temperature=0.5)
        assert request3.temperature == 0.5

    def test_invalid_temperature_too_small(self):
        """测试temperature过小"""
        with pytest.raises(ValueError) as exc_info:
            ContentGenerationRequest(chapter_id=1, temperature=-0.1)
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_invalid_temperature_too_large(self):
        """测试temperature过大"""
        with pytest.raises(ValueError) as exc_info:
            ContentGenerationRequest(chapter_id=1, temperature=1.1)
        assert "less than or equal to 1" in str(exc_info.value)

    def test_temperature_rounding(self):
        """测试temperature精度舍入"""
        request = ContentGenerationRequest(chapter_id=1, temperature=0.856)
        assert request.temperature == 0.86

    def test_custom_context_without_override(self):
        """测试在override_context=False时设置custom_context"""
        with pytest.raises(ValueError) as exc_info:
            ContentGenerationRequest(
                chapter_id=1,
                override_context=False,
                custom_context={"test": "value"}
            )
        assert "override_context设为True" in str(exc_info.value)

    def test_custom_context_with_override(self):
        """测试在override_context=True时设置custom_context"""
        request = ContentGenerationRequest(
            chapter_id=1,
            override_context=True,
            custom_context={"characters": [1, 2, 3]}
        )
        assert request.custom_context == {"characters": [1, 2, 3]}

    def test_none_generation_mode(self):
        """测试generation_mode可以为None"""
        request = ContentGenerationRequest(
            chapter_id=1,
            generation_mode=None
        )
        assert request.generation_mode is None

    def test_none_temperature(self):
        """测试temperature可以为None"""
        request = ContentGenerationRequest(
            chapter_id=1,
            temperature=None
        )
        assert request.temperature is None


class TestVersionSelectionRequest:
    """测试版本选择请求模型"""

    def test_valid_request(self):
        """测试有效请求"""
        request = VersionSelectionRequest(draft_id=5)
        assert request.draft_id == 5
        assert request.apply_to_chapter is True  # 默认值

    def test_valid_request_with_apply_false(self):
        """测试apply_to_chapter为False"""
        request = VersionSelectionRequest(
            draft_id=10,
            apply_to_chapter=False
        )
        assert request.draft_id == 10
        assert request.apply_to_chapter is False

    def test_invalid_draft_id_zero(self):
        """测试无效的draft_id（0）"""
        with pytest.raises(ValueError) as exc_info:
            VersionSelectionRequest(draft_id=0)
        assert "greater than 0" in str(exc_info.value)

    def test_invalid_draft_id_negative(self):
        """测试无效的draft_id（负数）"""
        with pytest.raises(ValueError) as exc_info:
            VersionSelectionRequest(draft_id=-1)
        assert "greater than 0" in str(exc_info.value)


class TestContentGenerationDraftResponse:
    """测试草稿响应模型"""

    def test_valid_response(self):
        """测试有效响应"""
        now = datetime.now()
        response = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="这是生成的内容",
            word_count=8,
            summary="摘要",
            is_selected=False,
            generation_mode="advanced",
            temperature=Decimal("0.85"),
            created_at=now
        )
        assert response.id == 1
        assert response.chapter_id == 5
        assert response.version_id == "v1"
        assert response.content == "这是生成的内容"
        assert response.word_count == 8
        assert response.summary == "摘要"
        assert response.is_selected is False
        assert response.generation_mode == "advanced"
        assert response.temperature == Decimal("0.85")
        assert response.created_at == now

    def test_response_with_optional_fields_none(self):
        """测试可选字段为None"""
        now = datetime.now()
        response = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="内容",
            word_count=2,
            created_at=now
        )
        assert response.summary is None
        assert response.is_selected is False  # 默认值
        assert response.generation_mode is None
        assert response.temperature is None

    def test_response_serialization(self):
        """测试响应序列化"""
        now = datetime.now()
        response = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="内容",
            word_count=2,
            created_at=now
        )
        # 转换为字典（模拟JSON序列化）
        data = response.model_dump()
        assert data["id"] == 1
        assert data["chapter_id"] == 5
        assert data["version_id"] == "v1"
        assert data["content"] == "内容"
        assert data["word_count"] == 2
        assert data["created_at"] == now


class TestContentGenerationBatchResponse:
    """测试批量生成响应模型"""

    def test_valid_response(self):
        """测试有效响应"""
        now = datetime.now()
        draft = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="内容",
            word_count=2,
            created_at=now
        )
        response = ContentGenerationBatchResponse(
            task_id="task_123",
            chapter_id=5,
            total_versions=3,
            completed_versions=1,
            status="in_progress",
            drafts=[draft],
            created_at=now
        )
        assert response.task_id == "task_123"
        assert response.chapter_id == 5
        assert response.total_versions == 3
        assert response.completed_versions == 1
        assert response.status == "in_progress"
        assert len(response.drafts) == 1
        assert response.error is None

    def test_response_with_error(self):
        """测试包含错误的响应"""
        now = datetime.now()
        response = ContentGenerationBatchResponse(
            task_id="task_456",
            chapter_id=5,
            total_versions=3,
            completed_versions=0,
            status="failed",
            error="API调用失败",
            created_at=now
        )
        assert response.status == "failed"
        assert response.error == "API调用失败"
        assert len(response.drafts) == 0

    def test_response_empty_drafts_list(self):
        """测试空草稿列表"""
        now = datetime.now()
        response = ContentGenerationBatchResponse(
            task_id="task_789",
            chapter_id=5,
            total_versions=2,
            completed_versions=0,
            status="pending",
            created_at=now
        )
        assert len(response.drafts) == 0
        assert response.completed_versions == 0


class TestDraftListResponse:
    """测试草稿列表响应模型"""

    def test_valid_response(self):
        """测试有效响应"""
        now = datetime.now()
        draft1 = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="内容1",
            word_count=2,
            is_selected=True,
            created_at=now
        )
        draft2 = ContentGenerationDraftResponse(
            id=2,
            chapter_id=5,
            version_id="v2",
            content="内容2",
            word_count=2,
            is_selected=False,
            created_at=now
        )
        response = DraftListResponse(
            chapter_id=5,
            drafts=[draft1, draft2],
            total=2,
            selected_draft_id=1
        )
        assert response.chapter_id == 5
        assert len(response.drafts) == 2
        assert response.total == 2
        assert response.selected_draft_id == 1

    def test_response_without_selection(self):
        """测试没有选中草稿的响应"""
        now = datetime.now()
        draft = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="内容",
            word_count=2,
            is_selected=False,
            created_at=now
        )
        response = DraftListResponse(
            chapter_id=5,
            drafts=[draft],
            total=1
        )
        assert response.selected_draft_id is None

    def test_response_empty_list(self):
        """测试空列表响应"""
        response = DraftListResponse(
            chapter_id=5,
            drafts=[],
            total=0
        )
        assert len(response.drafts) == 0
        assert response.total == 0


class TestDraftComparisonResponse:
    """测试草稿对比响应模型"""

    def test_valid_response(self):
        """测试有效响应"""
        now = datetime.now()
        draft1 = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="内容1",
            word_count=2,
            created_at=now
        )
        draft2 = ContentGenerationDraftResponse(
            id=2,
            chapter_id=5,
            version_id="v2",
            content="内容2",
            word_count=2,
            created_at=now
        )
        response = DraftComparisonResponse(
            chapter_id=5,
            drafts=[draft1, draft2],
            comparison="v1更注重情感，v2更注重情节"
        )
        assert response.chapter_id == 5
        assert len(response.drafts) == 2
        assert response.comparison == "v1更注重情感，v2更注重情节"

    def test_response_without_comparison(self):
        """测试没有对比摘要的响应"""
        now = datetime.now()
        draft = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="内容",
            word_count=2,
            created_at=now
        )
        response = DraftComparisonResponse(
            chapter_id=5,
            drafts=[draft]
        )
        assert response.comparison is None


class TestSchemaIntegration:
    """测试Schema集成和序列化"""

    def test_request_to_dict(self):
        """测试请求转换为字典"""
        request = ContentGenerationRequest(
            chapter_id=5,
            num_versions=3,
            generation_mode="advanced",
            temperature=0.85
        )
        data = request.model_dump()
        assert data["chapter_id"] == 5
        assert data["num_versions"] == 3
        assert data["generation_mode"] == "advanced"
        assert data["temperature"] == 0.85

    def test_response_to_json(self):
        """测试响应JSON序列化"""
        now = datetime.now()
        draft = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="内容",
            word_count=2,
            created_at=now
        )
        # model_dump_json会处理datetime等类型
        json_str = draft.model_dump_json()
        assert '"id":1' in json_str
        assert '"chapter_id":5' in json_str
        assert '"version_id":"v1"' in json_str

    def test_nested_response_serialization(self):
        """测试嵌套响应序列化"""
        now = datetime.now()
        draft = ContentGenerationDraftResponse(
            id=1,
            chapter_id=5,
            version_id="v1",
            content="内容",
            word_count=2,
            created_at=now
        )
        batch_response = ContentGenerationBatchResponse(
            task_id="task_123",
            chapter_id=5,
            total_versions=1,
            completed_versions=1,
            status="completed",
            drafts=[draft],
            created_at=now
        )
        data = batch_response.model_dump()
        assert len(data["drafts"]) == 1
        assert data["drafts"][0]["id"] == 1
        assert data["drafts"][0]["version_id"] == "v1"
