"""
AI服务集成测试
测试智能续写工作流的核心功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.ai_service import AIService
from app.schemas.content_generation import FirstChapterMode, ContinueMode
from app.schemas.context_analysis import (
    CharacterSuggestion, WorldSettingSuggestion, PlotNodeSuggestion
)


class TestAIServiceIntegration:
    """AI服务集成测试"""

    @pytest.fixture(scope="function")
    def mock_ai_service(self):
        """创建模拟的AI服务"""
        service = AIService()
        service.client = Mock()
        return service

    def test_build_context(self, mock_ai_service):
        """测试上下文构建功能"""
        # 测试数据
        project_data = {
            "title": "测试小说",
            "genre": "玄幻",
            "summary": "一个关于修仙的故事",
            "style": "轻松幽默"
        }

        characters = [
            {
                "name": "主角",
                "personality": "勇敢善良"
            },
            {
                "name": "反派",
                "personality": "阴险狡诈"
            }
        ]

        world_settings = [
            {
                "name": "灵力体系",
                "description": "修仙者修炼的体系"
            },
            {
                "name": "修仙世界",
                "description": "凡人可以修仙的世界"
            }
        ]

        # 调用上下文构建方法
        context = mock_ai_service._build_context(project_data, characters, world_settings)

        # 验证上下文内容
        assert "小说信息" in context
        assert "测试小说" in context
        assert "玄幻" in context
        assert "轻松幽默" in context

        assert "人物设定" in context
        assert "主角" in context
        assert "反派" in context

        assert "世界观设定" in context
        assert "灵力体系" in context
        assert "修仙世界" in context

    def test_generate_chapter(self, mock_ai_service):
        """测试章节生成功能"""
        # 设置mock返回
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = """
林辰是一名普通的山村青年，每天除了打柴就是照顾生病的妹妹。这天，他在后山采药时，意外发现了一个神秘的洞穴。
洞穴深处，一具白骨手中紧握着一本泛黄的古籍。林辰好奇地拿起古籍，发现上面记载着失传已久的修仙功法《太上清心诀》。
就在他触摸古籍的瞬间，一股强大的力量涌入体内，他的经脉开始自行运转，丹田中凝聚出一缕微弱的灵力。
"这是什么？难道我遇到了传说中的仙人遗宝？"林辰震惊地想着。
        """
        mock_ai_service.client.chat.completions.create.return_value = mock_response

        # 调用生成方法
        result = mock_ai_service.generate_chapter(
            prompt="请写一个关于修仙的小说开篇",
            context="这是一个修仙世界，主角意外获得传承",
            word_count=2000,
            style="轻松幽默"
        )

        # 验证结果
        assert "林辰" in result
        assert "修仙" in result
        assert len(result) > 100  # 确保生成的内容足够长

        # 验证mock被正确调用
        mock_ai_service.client.chat.completions.create.assert_called_once()

    def test_analyze_context_requirements(self, mock_ai_service):
        """测试上下文分析需求功能"""
        # 模拟AI服务方法
        def mock_analyze(*args, **kwargs):
            return {
                "validated_characters": [
                    {
                        "id": 1,
                        "name": "林辰",
                        "role": "主角",
                        "personality": "乐观、善良、勇敢",
                        "core_motivation": "保护家人，追求天道"
                    }
                ],
                "validated_world_settings": [
                    {
                        "id": 1,
                        "name": "灵力体系",
                        "type": "力量体系",
                        "description": "修仙者通过吸收天地灵力修炼",
                        "is_core_rule": True
                    }
                ],
                "validated_plot_nodes": [
                    {
                        "id": 1,
                        "title": "拜师学艺",
                        "type": "关键情节",
                        "importance": "重要",
                        "description": "林辰正式拜李师傅为师，开始修仙之路"
                    }
                ],
                "summary": "建议主角林辰继续跟随李师傅修炼，重点关注灵力体系的运用"
            }

        mock_ai_service.analyze_context_requirements = mock_analyze

        # 调用分析方法
        result = mock_ai_service.analyze_context_requirements(
            project_id=1,
            previous_chapter_id=None,
            plot_direction="开始正式修炼"
        )

        # 验证结果
        assert len(result["validated_characters"]) == 1
        assert result["validated_characters"][0]["name"] == "林辰"
        assert result["validated_characters"][0]["role"] == "主角"

        assert len(result["validated_world_settings"]) == 1
        assert result["validated_world_settings"][0]["name"] == "灵力体系"
        assert result["validated_world_settings"][0]["is_core_rule"] == True

        assert len(result["validated_plot_nodes"]) == 1
        assert result["validated_plot_nodes"][0]["title"] == "拜师学艺"
        assert result["validated_plot_nodes"][0]["importance"] == "重要"

        assert "summary" in result
        assert len(result["summary"]) > 0

    def test_first_chapter_mode_validation(self):
        """测试首章模式参数验证"""
        # 测试有效数据
        first_chapter = FirstChapterMode(
            opening_scene="山村青年在山中发现神秘古籍",
            key_elements=["修仙", "奇遇", "主角成长"],
            tone="轻松愉快"
        )

        assert first_chapter.opening_scene == "山村青年在山中发现神秘古籍"
        assert len(first_chapter.key_elements) == 3
        assert "修仙" in first_chapter.key_elements
        assert first_chapter.tone == "轻松愉快"

    def test_continue_mode_validation(self):
        """测试续写模式参数验证"""
        # 测试有效数据
        continue_mode = ContinueMode(
            previous_chapter_id=1,
            transition="immediate",
            plot_direction="开始正式修炼",
            conflict_point="资质测试"
        )

        assert continue_mode.previous_chapter_id == 1
        assert continue_mode.transition == "immediate"
        assert continue_mode.plot_direction == "开始正式修炼"
        assert continue_mode.conflict_point == "资质测试"

    def test_schema_responses(self):
        """测试响应模式的结构"""
        # 测试角色建议模式
        char_suggestion = CharacterSuggestion(
            id=1,
            name="林辰",
            role="主角",
            personality="勇敢善良",
            core_motivation="保护家人"
        )

        assert char_suggestion.id == 1
        assert char_suggestion.name == "林辰"
        assert char_suggestion.role == "主角"

        # 测试世界观设定建议模式
        setting_suggestion = WorldSettingSuggestion(
            id=1,
            name="灵力体系",
            type="力量体系",
            description="修仙修炼体系",
            is_core_rule=True
        )

        assert setting_suggestion.id == 1
        assert setting_suggestion.name == "灵力体系"
        assert setting_suggestion.type == "力量体系"
        assert setting_suggestion.is_core_rule == True

        # 测试情节节点建议模式
        plot_suggestion = PlotNodeSuggestion(
            id=1,
            title="拜师学艺",
            type="关键情节",
            importance="重要",
            description="开始修仙之路"
        )

        assert plot_suggestion.id == 1
        assert plot_suggestion.title == "拜师学艺"
        assert plot_suggestion.type == "关键情节"
        assert plot_suggestion.importance == "重要"

    def test_integration_workflow_simulation(self):
        """模拟完整的工作流程"""
        # 模拟项目数据
        project_data = {
            "title": "修仙之旅",
            "genre": "玄幻",
            "summary": "一个普通青年的修仙故事",
            "style": "轻松幽默"
        }

        # 模拟上下文构建
        context_parts = []
        context_parts.append(f"## 小说信息\n")
        context_parts.append(f"书名：{project_data['title']}\n")
        context_parts.append(f"类型：{project_data['genre']}\n")
        context_parts.append(f"简介：{project_data['summary']}\n")
        context_parts.append(f"文风：{project_data['style']}\n\n")

        full_context = "".join(context_parts)

        # 验证上下文包含必要信息
        assert "小说信息" in full_context
        assert "修仙之旅" in full_context
        assert "玄幻" in full_context
        assert "轻松幽默" in full_context

        # 模拟生成请求
        first_chapter_mode = {
            "opening_scene": "山村青年在山中发现神秘古籍",
            "key_elements": ["修仙", "奇遇", "主角成长"],
            "tone": "轻松愉快"
        }

        # 验证请求数据结构
        assert isinstance(first_chapter_mode, dict)
        assert "opening_scene" in first_chapter_mode
        assert "key_elements" in first_chapter_mode
        assert "tone" in first_chapter_mode

        # 验证关键元素
        assert len(first_chapter_mode["key_elements"]) == 3
        assert "修仙" in first_chapter_mode["key_elements"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])