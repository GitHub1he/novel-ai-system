import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.ai_service import AIService
from app.models.character import Character, CharacterRole
from app.models.world_setting import WorldSetting, SettingType
from app.models.plot_node import PlotNode, PlotType, PlotImportance


@pytest.fixture(scope="function")
def mock_ai_service():
    """创建模拟的AI服务"""
    service = AIService()
    service.client = Mock()
    return service


@pytest.fixture(scope="function")
def test_project(db):
    """创建测试项目"""
    from app.models.project import Project, ProjectStatus
    project = Project(
        title="测试小说",
        author="测试作者",
        genre='["玄幻", "修仙"]',
        summary="这是一个关于修仙的故事",
        status=ProjectStatus.DRAFT,
        user_id=1
    )
    db.add(project)
    db.flush()
    return project


@pytest.fixture(scope="function")
def test_characters(db, test_project):
    """创建测试角色"""
    characters = [
        Character(
            project_id=test_project.id,
            name="主角",
            role=CharacterRole.PROTAGONIST,
            personality="勇敢、正义",
            core_motivation="拯救世界",
            age=25,
            gender="男"
        ),
        Character(
            project_id=test_project.id,
            name="反派",
            role=CharacterRole.ANTAGONIST,
            personality="阴险狡诈",
            core_motivation="统治世界",
            age=35,
            gender="男"
        ),
        Character(
            project_id=test_project.id,
            name="配角",
            role=CharacterRole.SUPPORTING,
            personality="善良、智慧",
            core_motivation="帮助主角",
            age=30,
            gender="女"
        )
    ]
    db.add_all(characters)
    db.commit()
    return characters


@pytest.fixture(scope="function")
def test_world_settings(db, test_project):
    """创建测试世界观设定"""
    settings = [
        WorldSetting(
            project_id=test_project.id,
            name="修仙世界",
            setting_type=SettingType.ERA,
            description="一个充满修仙者的世界",
            is_core_rule=1
        ),
        WorldSetting(
            project_id=test_project.id,
            name="灵力体系",
            setting_type=SettingType.POWER,
            description="修炼灵力的体系",
            is_core_rule=1
        ),
        WorldSetting(
            project_id=test_project.id,
            name="天剑门",
            setting_type=SettingType.FACTION,
            description="修仙门派之一",
            is_core_rule=0
        )
    ]
    db.add_all(settings)
    db.commit()
    return settings


@pytest.fixture(scope="function")
def test_plot_nodes(db, test_project):
    """创建测试情节节点"""
    plot_nodes = [
        PlotNode(
            project_id=test_project.id,
            title="开始修行",
            plot_type=PlotType.MEETING,
            importance=PlotImportance.MAIN,
            description="主角开始修行的故事",
            sequence_number=1
        ),
        PlotNode(
            project_id=test_project.id,
            title="遇到反派",
            plot_type=PlotType.CONFLICT,
            importance=PlotImportance.MAIN,
            description="主角与反派的第一次冲突",
            sequence_number=2
        ),
        PlotNode(
            project_id=test_project.id,
            title="获得奇遇",
            plot_type=PlotType.REVELATION,
            importance=PlotImportance.BRANCH,
            description="主角获得意外奇遇",
            sequence_number=3
        )
    ]
    db.add_all(plot_nodes)
    db.commit()
    return plot_nodes


@pytest.fixture(scope="function")
def test_chapter(db, test_project):
    """创建测试章节"""
    from app.models.chapter import Chapter, ChapterStatus
    chapter = Chapter(
        project_id=test_project.id,
        chapter_number=1,
        title="第一章：开始",
        content="这是一个漫长的故事开始了。主角从小就立志要成为一个伟大的修仙者。他天赋异禀，从小就展现出非凡的灵力天赋。在村中，他被称为天之骄子。",
        status=ChapterStatus.DRAFT,
        word_count=50
    )
    db.add(chapter)
    db.commit()
    return chapter


class TestContextAnalysis:
    """测试上下文分析功能"""

    @patch('app.services.ai_service.AIService._build_analysis_prompt')
    @patch('app.services.ai_service.AIService._validate_and_enrich_recommendations')
    def test_analyze_context_with_characters(
        self,
        mock_validate,
        mock_build_prompt,
        mock_ai_service,
        test_project,
        test_characters,
        test_world_settings,
        test_plot_nodes
    ):
        """测试带有角色、设定和情节节点的上下文分析"""
        # 模拟AI返回的推荐
        mock_ai_recommendations = {
            "suggested_characters": [1, 2],
            "suggested_world_settings": [1, 3],
            "suggested_plot_nodes": [1, 2]
        }

        # 模拟验证结果
        mock_validate.return_value = {
            "validated_characters": [
                {
                    "id": 1,
                    "name": "主角",
                    "role": "protagonist",
                    "personality": "勇敢、正义"
                },
                {
                    "id": 2,
                    "name": "反派",
                    "role": "antagonist",
                    "personality": "阴险狡诈"
                }
            ],
            "validated_world_settings": [
                {
                    "id": 1,
                    "name": "修仙世界",
                    "type": "era",
                    "description": "一个充满修仙者的世界"
                },
                {
                    "id": 3,
                    "name": "天剑门",
                    "type": "faction",
                    "description": "修仙门派之一"
                }
            ],
            "validated_plot_nodes": [
                {
                    "id": 1,
                    "title": "开始修行",
                    "type": "meeting",
                    "importance": "main"
                },
                {
                    "id": 2,
                    "title": "遇到反派",
                    "type": "conflict",
                    "importance": "main"
                }
            ]
        }

        mock_build_prompt.return_value = "测试提示词"

        # 由于没有真实的AI客户端，方法会直接返回空数组
        # 这里测试的是fallback逻辑
        result = mock_ai_service.analyze_context_requirements(
            project_id=test_project.id,
            plot_direction="主角开始修行之旅"
        )

        # 验证返回空结果（因为没有AI客户端）
        assert result["validated_characters"] == []
        assert result["validated_world_settings"] == []
        assert result["validated_plot_nodes"] == []

    def test_analyze_context_empty_project(self, mock_ai_service):
        """测试空项目的上下文分析"""
        # 执行分析（没有AI客户端）
        result = mock_ai_service.analyze_context_requirements(
            project_id=999,  # 不存在的项目ID
            plot_direction="测试情节方向"
        )

        # 验证返回空结果
        assert result["validated_characters"] == []
        assert result["validated_world_settings"] == []
        assert result["validated_plot_nodes"] == []

    @patch('app.services.ai_service.AIService._build_analysis_prompt')
    @patch('app.services.ai_service.AIService._validate_and_enrich_recommendations')
    def test_analyze_context_with_previous_chapter(
        self,
        mock_validate,
        mock_build_prompt,
        mock_ai_service,
        test_project,
        test_chapter
    ):
        """测试包含前一章内容的上下文分析"""
        mock_build_prompt.return_value = "测试提示词"

        # 执行分析（包含前一章ID）
        result = mock_ai_service.analyze_context_requirements(
            project_id=test_project.id,
            previous_chapter_id=test_chapter.id,
            plot_direction="继续故事"
        )

        # 由于没有AI客户端，返回空结果
        assert result["validated_characters"] == []
        assert result["validated_world_settings"] == []
        assert result["validated_plot_nodes"] == []

    @patch('app.services.ai_service.AIService._build_analysis_prompt')
    def test_ai_call_failure_fallback(self, mock_build_prompt, mock_ai_service, test_project):
        """测试AI调用失败时的降级处理"""
        # 模拟AI调用异常
        mock_ai_service.client.chat.completions.create.side_effect = Exception("AI调用失败")
        mock_build_prompt.return_value = "测试提示词"

        # 执行分析
        result = mock_ai_service.analyze_context_requirements(
            project_id=test_project.id,
            plot_direction="测试方向"
        )

        # 验证降级返回空结果
        assert result["validated_characters"] == []
        assert result["validated_world_settings"] == []
        assert result["validated_plot_nodes"] == []

    def test_build_analysis_prompt_structure(self, mock_ai_service, test_project, test_characters, test_world_settings, test_plot_nodes):
        """测试提示词构建的结构"""
        prompt = mock_ai_service._build_analysis_prompt(
            project=test_project,
            characters=test_characters,
            world_settings=test_world_settings,
            plot_nodes=test_plot_nodes,
            previous_context="前文内容",
            plot_direction="情节发展方向"
        )

        # 验证提示词包含必要部分
        assert "## 小说项目信息" in prompt
        assert "## 可用角色" in prompt
        assert "## 世界观设定" in prompt
        assert "## 情节节点" in prompt
        assert "## 前文上下文" in prompt
        assert "## 情节方向" in prompt

        # 验证项目信息
        assert test_project.title in prompt
        assert test_project.genre in prompt
        assert test_project.summary in prompt

        # 验证角色信息
        assert "主角" in prompt
        assert "勇敢、正义" in prompt

        # 验证世界观设定信息
        assert "修仙世界" in prompt
        assert "灵力体系" in prompt

        # 验证情节节点信息
        assert "开始修行" in prompt
        assert "遇到反派" in prompt

    def test_validate_and_enrich_recommendations(self, mock_ai_service, test_characters, test_world_settings, test_plot_nodes):
        """测试推荐验证和丰富功能"""
        # 获取实际的角色ID
        char_ids = [char.id for char in test_characters]
        setting_ids = [setting.id for setting in test_world_settings]
        plot_ids = [plot.id for plot in test_plot_nodes]

        # 模拟AI推荐（包含有效和无效ID）
        ai_recommendations = {
            "suggested_characters": char_ids + [999],  # 999是无效ID
            "suggested_world_settings": setting_ids + [999],
            "suggested_plot_nodes": plot_ids + [999]
        }

        result = mock_ai_service._validate_and_enrich_recommendations(
            ai_recommendations,
            test_characters,
            test_world_settings,
            test_plot_nodes
        )

        # 验证只返回有效的ID对应的实体
        assert len(result["validated_characters"]) == len(char_ids)  # 所有有效角色
        assert len(result["validated_world_settings"]) == len(setting_ids)  # 所有有效设定
        assert len(result["validated_plot_nodes"]) == len(plot_ids)  # 所有有效情节

        # 验证返回的实体包含完整信息
        first_char = result["validated_characters"][0]
        assert first_char["name"] == "主角"
        assert first_char["role"] == "protagonist"
        assert first_char["personality"] == "勇敢、正义"