"""
测试内容生成Schema的序列化和反序列化

该测试模块验证：
- FirstChapterMode与ChapterGenerateRequest的集成
- ContinueMode与ChapterGenerateRequest的集成
- word_count字段验证（500-10000范围）
- project_id和chapter_number字段验证（必须大于0）
- ContinueMode.previous_chapter_id字段验证（必须大于0）
- ContinueMode.transition字段类型验证（必须为TransitionType枚举）
- first_chapter_mode和continue_mode互斥验证
- style_intensity、temperature、versions字段边界值验证
"""
import pytest
from app.schemas.content_generation import (
    GenerationMode,
    TransitionType,
    FirstChapterMode,
    ContinueMode,
    ChapterGenerateRequest,
)


class TestFirstChapterRequest:
    """测试首章生成请求"""

    def test_first_chapter_request(self):
        """测试FirstChapterMode与ChapterGenerateRequest"""
        first_chapter_mode = FirstChapterMode(
            opening_scene="一个暴风雨之夜，古堡的钟声敲响",
            key_elements=["悬疑", "神秘", "古老的秘密"],
            tone="悬疑"
        )

        request = ChapterGenerateRequest(
            mode=GenerationMode.STANDARD,
            project_id=1,
            chapter_number=1,
            first_chapter_mode=first_chapter_mode,
            word_count=2000,
            versions=3
        )

        # 验证基本字段
        assert request.mode == GenerationMode.STANDARD
        assert request.project_id == 1
        assert request.chapter_number == 1
        assert request.word_count == 2000
        assert request.versions == 3

        # 验证首章模式字段
        assert request.first_chapter_mode is not None
        assert request.first_chapter_mode.opening_scene == "一个暴风雨之夜，古堡的钟声敲响"
        assert request.first_chapter_mode.key_elements == ["悬疑", "神秘", "古老的秘密"]
        assert request.first_chapter_mode.tone == "悬疑"

        # 验证continue_mode为None
        assert request.continue_mode is None


class TestContinueChapterRequest:
    """测试续写章节请求"""

    def test_continue_chapter_request(self):
        """测试ContinueMode与ChapterGenerateRequest"""
        continue_mode = ContinueMode(
            previous_chapter_id=5,
            transition=TransitionType.TIME_SKIP,
            plot_direction="主角发现了一个重要线索",
            conflict_point="真相与谎言的冲突"
        )

        request = ChapterGenerateRequest(
            mode=GenerationMode.ADVANCED,
            project_id=2,
            chapter_number=6,
            continue_mode=continue_mode,
            word_count=2500,
            versions=2,
            featured_characters=[1, 2, 3],
            pov_character_id=1
        )

        # 验证基本字段
        assert request.mode == GenerationMode.ADVANCED
        assert request.project_id == 2
        assert request.chapter_number == 6
        assert request.word_count == 2500
        assert request.versions == 2

        # 验证续写模式字段
        assert request.continue_mode is not None
        assert request.continue_mode.previous_chapter_id == 5
        assert request.continue_mode.transition == TransitionType.TIME_SKIP
        assert request.continue_mode.plot_direction == "主角发现了一个重要线索"
        assert request.continue_mode.conflict_point == "真相与谎言的冲突"

        # 验证其他可选字段
        assert request.featured_characters == [1, 2, 3]
        assert request.pov_character_id == 1

        # 验证first_chapter_mode为None
        assert request.first_chapter_mode is None


class TestWordCountValidation:
    """测试字数验证"""

    def test_word_count_validation_minimum_boundary(self):
        """测试word_count最小边界值（500）"""
        request = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            word_count=500  # 最小有效值
        )
        assert request.word_count == 500

    def test_word_count_validation_maximum_boundary(self):
        """测试word_count最大边界值（10000）"""
        request = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            word_count=10000  # 最大有效值
        )
        assert request.word_count == 10000

    def test_word_count_validation_too_small(self):
        """测试word_count小于500时验证失败"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=1,
                chapter_number=1,
                word_count=499  # 小于最小值
            )
        assert "greater than or equal to 500" in str(exc_info.value)

    def test_word_count_validation_too_large(self):
        """测试word_count大于10000时验证失败"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=1,
                chapter_number=1,
                word_count=10001  # 大于最大值
            )
        assert "less than or equal to 10000" in str(exc_info.value)

    def test_word_count_default_value(self):
        """测试word_count默认值为2000"""
        request = ChapterGenerateRequest(
            mode=GenerationMode.STANDARD,
            project_id=1,
            chapter_number=1
        )
        assert request.word_count == 2000


class TestOtherValidations:
    """测试其他字段验证"""

    def test_versions_validation(self):
        """测试versions字段验证（1-5范围）"""
        # 最小值
        request1 = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            versions=1
        )
        assert request1.versions == 1

        # 最大值
        request2 = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            versions=5
        )
        assert request2.versions == 5

        # 默认值
        request3 = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1
        )
        assert request3.versions == 3

    def test_style_intensity_validation(self):
        """测试style_intensity字段验证（0-100范围）"""
        request = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            style_intensity=85
        )
        assert request.style_intensity == 85

    def test_temperature_validation(self):
        """测试temperature字段验证（0.1-1.5范围）"""
        request = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            temperature=1.2
        )
        assert request.temperature == 1.2

    def test_optional_lists_default_to_empty(self):
        """测试可选列表字段默认为空列表"""
        request = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1
        )
        assert request.featured_characters == []
        assert request.related_world_settings == []
        assert request.related_plot_nodes == []

    def test_full_request_with_all_fields(self):
        """测试包含所有字段的完整请求"""
        first_chapter_mode = FirstChapterMode(
            opening_scene="故事开始",
            key_elements=["要素1", "要素2"],
            tone="史诗"
        )

        request = ChapterGenerateRequest(
            mode=GenerationMode.ADVANCED,
            project_id=1,
            chapter_number=1,
            first_chapter_mode=first_chapter_mode,
            suggested_context={
                "characters": [1, 2],
                "world_settings": [3],
                "plot_nodes": [4, 5]
            },
            featured_characters=[1, 2, 3],
            related_world_settings=[10, 20],
            related_plot_nodes=[30, 40, 50],
            word_count=3000,
            versions=3,
            style_intensity=80,
            pov_character_id=1,
            temperature=0.9
        )

        assert request.mode == GenerationMode.ADVANCED
        assert request.project_id == 1
        assert request.chapter_number == 1
        assert request.word_count == 3000
        assert request.versions == 3
        assert request.style_intensity == 80
        assert request.pov_character_id == 1
        assert request.temperature == 0.9
        assert len(request.featured_characters) == 3
        assert len(request.related_world_settings) == 2
        assert len(request.related_plot_nodes) == 3


class TestProjectAndChapterNumberValidation:
    """测试project_id和chapter_number字段验证"""

    def test_project_id_must_be_positive(self):
        """测试project_id必须大于0"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=0,  # 无效值
                chapter_number=1
            )
        assert "greater than 0" in str(exc_info.value)

    def test_project_id_cannot_be_negative(self):
        """测试project_id不能为负数"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=-1,  # 负数
                chapter_number=1
            )
        assert "greater than 0" in str(exc_info.value)

    def test_chapter_number_must_be_positive(self):
        """测试chapter_number必须大于0"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=1,
                chapter_number=0  # 无效值
            )
        assert "greater than 0" in str(exc_info.value)

    def test_chapter_number_cannot_be_negative(self):
        """测试chapter_number不能为负数"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=1,
                chapter_number=-1  # 负数
            )
        assert "greater than 0" in str(exc_info.value)

    def test_positive_project_and_chapter_numbers(self):
        """测试有效的project_id和chapter_number"""
        request = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1
        )
        assert request.project_id == 1
        assert request.chapter_number == 1


class TestContinueModeValidation:
    """测试ContinueMode字段验证"""

    def test_previous_chapter_id_must_be_positive(self):
        """测试previous_chapter_id必须大于0"""
        with pytest.raises(ValueError) as exc_info:
            ContinueMode(
                previous_chapter_id=0,  # 无效值
                transition=TransitionType.IMMEDIATE,
                plot_direction="情节方向"
            )
        assert "greater than 0" in str(exc_info.value)

    def test_previous_chapter_id_cannot_be_negative(self):
        """测试previous_chapter_id不能为负数"""
        with pytest.raises(ValueError) as exc_info:
            ContinueMode(
                previous_chapter_id=-5,  # 负数
                transition=TransitionType.IMMEDIATE,
                plot_direction="情节方向"
            )
        assert "greater than 0" in str(exc_info.value)

    def test_transition_type_validation(self):
        """测试transition字段类型验证（必须是TransitionType枚举）"""
        continue_mode = ContinueMode(
            previous_chapter_id=1,
            transition=TransitionType.LOCATION_CHANGE,  # 使用枚举值
            plot_direction="情节方向"
        )
        assert continue_mode.transition == TransitionType.LOCATION_CHANGE

    def test_transition_default_value(self):
        """测试transition默认值为IMMEDIATE"""
        continue_mode = ContinueMode(
            previous_chapter_id=1,
            plot_direction="情节方向"
        )
        assert continue_mode.transition == TransitionType.IMMEDIATE

    def test_all_transition_types(self):
        """测试所有TransitionType枚举值"""
        transition_types = [
            TransitionType.IMMEDIATE,
            TransitionType.TIME_SKIP,
            TransitionType.LOCATION_CHANGE,
            TransitionType.SUMMARY
        ]

        for trans_type in transition_types:
            continue_mode = ContinueMode(
                previous_chapter_id=1,
                transition=trans_type,
                plot_direction="情节方向"
            )
            assert continue_mode.transition == trans_type


class TestMutualExclusivityValidation:
    """测试first_chapter_mode和continue_mode互斥验证"""

    def test_cannot_set_both_modes(self):
        """测试不能同时设置first_chapter_mode和continue_mode"""
        first_chapter_mode = FirstChapterMode(
            opening_scene="开篇场景",
            key_elements=["要素1"]
        )
        continue_mode = ContinueMode(
            previous_chapter_id=1,
            transition=TransitionType.IMMEDIATE,
            plot_direction="情节方向"
        )

        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.STANDARD,
                project_id=1,
                chapter_number=1,
                first_chapter_mode=first_chapter_mode,
                continue_mode=continue_mode  # 同时设置两个模式
            )
        assert "不能同时设置first_chapter_mode和continue_mode" in str(exc_info.value)

    def test_can_set_first_chapter_mode_only(self):
        """测试可以只设置first_chapter_mode"""
        first_chapter_mode = FirstChapterMode(
            opening_scene="开篇场景",
            key_elements=["要素1"]
        )

        request = ChapterGenerateRequest(
            mode=GenerationMode.STANDARD,
            project_id=1,
            chapter_number=1,
            first_chapter_mode=first_chapter_mode
        )
        assert request.first_chapter_mode is not None
        assert request.continue_mode is None

    def test_can_set_continue_mode_only(self):
        """测试可以只设置continue_mode"""
        continue_mode = ContinueMode(
            previous_chapter_id=1,
            transition=TransitionType.IMMEDIATE,
            plot_direction="情节方向"
        )

        request = ChapterGenerateRequest(
            mode=GenerationMode.STANDARD,
            project_id=1,
            chapter_number=1,
            continue_mode=continue_mode
        )
        assert request.continue_mode is not None
        assert request.first_chapter_mode is None

    def test_can_set_neither_mode(self):
        """测试可以两个模式都不设置"""
        request = ChapterGenerateRequest(
            mode=GenerationMode.STANDARD,
            project_id=1,
            chapter_number=1
        )
        assert request.first_chapter_mode is None
        assert request.continue_mode is None


class TestFieldBoundaryValidations:
    """测试字段边界值验证"""

    def test_style_intensity_below_minimum(self):
        """测试style_intensity小于最小值-1时验证失败"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=1,
                chapter_number=1,
                style_intensity=-1  # 小于0
            )
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_style_intensity_above_maximum(self):
        """测试style_intensity大于最大值100时验证失败"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=1,
                chapter_number=1,
                style_intensity=101  # 大于100
            )
        assert "less than or equal to 100" in str(exc_info.value)

    def test_style_intensity_boundary_values(self):
        """测试style_intensity边界值0和100"""
        # 最小值
        request1 = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            style_intensity=0
        )
        assert request1.style_intensity == 0

        # 最大值
        request2 = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            style_intensity=100
        )
        assert request2.style_intensity == 100

    def test_temperature_below_minimum(self):
        """测试temperature小于最小值0.1时验证失败"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=1,
                chapter_number=1,
                temperature=0.0  # 小于0.1
            )
        assert "greater than or equal to 0.1" in str(exc_info.value)

    def test_temperature_above_maximum(self):
        """测试temperature大于最大值1.5时验证失败"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=1,
                chapter_number=1,
                temperature=1.6  # 大于1.5
            )
        assert "less than or equal to 1.5" in str(exc_info.value)

    def test_temperature_boundary_values(self):
        """测试temperature边界值0.1和1.5"""
        # 最小值
        request1 = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            temperature=0.1
        )
        assert request1.temperature == 0.1

        # 最大值
        request2 = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            temperature=1.5
        )
        assert request2.temperature == 1.5

    def test_versions_below_minimum(self):
        """测试versions小于最小值1时验证失败"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=1,
                chapter_number=1,
                versions=0  # 小于1
            )
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_versions_above_maximum(self):
        """测试versions大于最大值5时验证失败"""
        with pytest.raises(ValueError) as exc_info:
            ChapterGenerateRequest(
                mode=GenerationMode.SIMPLE,
                project_id=1,
                chapter_number=1,
                versions=6  # 大于5
            )
        assert "less than or equal to 5" in str(exc_info.value)

    def test_versions_boundary_values(self):
        """测试versions边界值1和5"""
        # 最小值
        request1 = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            versions=1
        )
        assert request1.versions == 1

        # 最大值
        request2 = ChapterGenerateRequest(
            mode=GenerationMode.SIMPLE,
            project_id=1,
            chapter_number=1,
            versions=5
        )
        assert request2.versions == 5
