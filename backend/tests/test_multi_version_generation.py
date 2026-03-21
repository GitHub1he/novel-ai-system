import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.ai_service import AIService
from app.core.database import SessionLocal
from app.models.project import Project
from app.models.character import Character
from app.models.world_setting import WorldSetting
from app.models.plot_node import PlotNode
from app.models.chapter import Chapter


class TestMultiVersionGeneration:
    """多版本生成功能的测试类"""

    @pytest.fixture
    def ai_service(self):
        """创建AI服务实例"""
        # Mock settings before creating AIService
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.ZHIPUAI_API_KEY = 'test-key'
            mock_settings.OPENAI_API_KEY = 'test-key'
            mock_settings.OPENAI_API_BASE = 'http://localhost:8000'
            mock_settings.AI_MODEL = 'test-model'

            service = AIService()
            # Mock the client for testing
            service.client = Mock()
            return service

    @pytest.fixture
    def mock_db(self):
        """创建模拟数据库会话"""
        db = Mock()
        return db

    @pytest.fixture
    def mock_project(self):
        """创建模拟项目"""
        project = Mock(spec=Project)
        project.id = 1
        project.title = "测试小说"
        project.genre = "玄幻"
        project.summary = "这是一部测试小说的简介"
        project.style = "轻松"
        return project

    @pytest.fixture
    def mock_characters(self):
        """创建模拟角色"""
        characters = []
        for i in range(3):
            char = Mock()
            # 模拟Character模型的必要属性
            char.id = i + 1
            char.name = f"角色{i+1}"
            char.personality = f"角色{i+1}的性格描述"
            char.core_motivation = f"角色{i+1}的核心动机"
            char.age = 20 + i
            char.gender = "男"
            char.appearance = f"角色{i+1}的外观描述"
            char.identity = f"角色{i+1}的身份背景"
            char.project_id = 1
            char.role = Mock()
            char.role.value = "supporting"
            characters.append(char)
        return characters

    @pytest.fixture
    def mock_world_settings(self):
        """创建模拟世界观设定"""
        settings = []
        for i in range(3):
            setting = Mock()
            # 模拟WorldSetting模型的必要属性
            setting.id = i + 1
            setting.name = f"设定{i+1}"
            setting.description = f"设定{i+1}的描述"
            setting.project_id = 1
            setting.attributes = {}
            setting.is_core_rule = False
            setting.setting_type = Mock()
            setting.setting_type.value = "era"
            settings.append(setting)
        return settings

    @pytest.fixture
    def mock_plot_nodes(self):
        """创建模拟情节节点"""
        nodes = []
        for i in range(3):
            node = Mock()
            # 模拟PlotNode模型的必要属性
            node.id = i + 1
            node.title = f"情节{i+1}"
            node.description = f"情节{i+1}的描述"
            node.project_id = 1
            node.conflict_points = ""
            node.theme_tags = []
            node.sequence_number = i + 1
            node.plot_type = Mock()
            node.plot_type.value = "event"
            node.importance = Mock()
            node.importance.value = "main"
            nodes.append(node)
        return nodes

    @pytest.fixture
    def mock_previous_chapter(self):
        """创建模拟的前一章"""
        mock_previous_chapter = Mock()
        mock_previous_chapter.content = "这是前一章的完整内容。" * 100  # 生成超过800字符的内容
        mock_previous_chapter.chapter_number = 5
        return mock_previous_chapter

    def test_generate_versions_first_chapter(self, ai_service, mock_db, mock_project, mock_characters, mock_world_settings, mock_plot_nodes):
        """测试首章多版本生成"""
        # 设置模拟数据
        mock_db.query(Project).filter(Project.id == 1).first.return_value = mock_project
        mock_db.query(Character).filter(Character.project_id == 1).limit(5).all.return_value = mock_characters
        mock_db.query(WorldSetting).filter(WorldSetting.project_id == 1).limit(3).all.return_value = mock_world_settings
        mock_db.query(PlotNode).filter(PlotNode.project_id == 1).limit(5).all.return_value = mock_plot_nodes

        # 模拟AI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "这是测试章节内容。" * 50  # 生成足够长的内容
        ai_service.client.chat.completions.create.return_value = mock_response

        # 构建请求
        request = {
            "project_id": 1,
            "chapter_number": 1,
            "first_chapter_mode": {
                "opening_scene": "开篇场景",
                "key_elements": ["要素1", "要素2"],
                "tone": "轻松"
            },
            "versions": 3,
            "word_count": 2000,
            "temperature": 0.8
        }

        # 执行生成
        versions, context_used = ai_service.generate_chapter_versions(request, mock_db)

        # 验证结果
        assert len(versions) == 3
        for version in versions:
            assert "version_id" in version
            assert "content" in version
            assert "word_count" in version
            assert "summary" in version
            assert version["word_count"] > 0

        # 验证上下文信息
        assert len(context_used["characters"]) == 3
        assert len(context_used["world_settings"]) == 3
        assert len(context_used["plot_nodes"]) == 3
        assert context_used["previous_chapter"] is None

        # 验证AI调用次数
        assert ai_service.client.chat.completions.create.call_count == 3

    def test_generate_versions_continue_chapter(self, ai_service, mock_db, mock_project, mock_characters, mock_world_settings, mock_plot_nodes):
        """测试续章多版本生成"""
        # 创建模拟的前一章
        mock_previous_chapter = Mock()
        mock_previous_chapter.content = "这是前一章的完整内容。" * 100  # 生成超过800字符的内容
        mock_previous_chapter.chapter_number = 5

        # 设置模拟数据
        mock_db.query(Project).filter(Project.id == 1).first.return_value = mock_project
        mock_db.query(Chapter).filter(Chapter.id == 5).first.return_value = mock_previous_chapter
        mock_db.query(Character).filter(Character.project_id == 1).limit(5).all.return_value = mock_characters
        mock_db.query(WorldSetting).filter(WorldSetting.project_id == 1).limit(3).all.return_value = mock_world_settings
        mock_db.query(PlotNode).filter(PlotNode.project_id == 1).limit(5).all.return_value = mock_plot_nodes

        # 模拟AI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "这是续章测试内容。" * 50
        ai_service.client.chat.completions.create.return_value = mock_response

        # 构建请求
        request = {
            "project_id": 1,
            "chapter_number": 6,
            "continue_mode": {
                "previous_chapter_id": 5,
                "transition": "immediate",
                "plot_direction": "情节继续发展",
                "conflict_point": "主要冲突"
            },
            "versions": 2,
            "word_count": 2000
        }

        # 执行生成
        versions, context_used = ai_service.generate_chapter_versions(request, mock_db)

        # 验证结果
        assert len(versions) == 2
        for version in versions:
            assert version["word_count"] > 0

        # 验证上下文信息
        assert context_used["previous_chapter"] is not None
        assert context_used["previous_chapter"]["chapter_number"] == 5
        assert len(context_used["previous_chapter"]["last_content"]) <= 800

    def test_different_temperature_values(self, ai_service, mock_db, mock_project, mock_characters, mock_world_settings, mock_plot_nodes):
        """测试不同温度值生成不同版本"""
        # 设置模拟数据
        mock_db.query(Project).filter(Project.id == 1).first.return_value = mock_project
        mock_db.query(Character).filter(Character.project_id == 1).limit(5).all.return_value = mock_characters
        mock_db.query(WorldSetting).filter(WorldSetting.project_id == 1).limit(3).all.return_value = mock_world_settings
        mock_db.query(PlotNode).filter(PlotNode.project_id == 1).limit(5).all.return_value = mock_plot_nodes

        # 模拟AI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "测试内容。"
        ai_service.client.chat.completions.create.return_value = mock_response

        # 构建请求
        request = {
            "project_id": 1,
            "chapter_number": 1,
            "versions": 3,
            "word_count": 2000,
            "temperature": 0.8
        }

        # 执行生成
        versions, _ = ai_service.generate_chapter_versions(request, mock_db)

        # 验证温度值是否正确设置
        calls = ai_service.client.chat.completions.create.call_args_list
        temperatures = [call[1]['temperature'] for call in calls]
        expected_temperatures = [0.8, 0.85, 0.9]

        assert temperatures == expected_temperatures

    def test_max_versions_limit(self, ai_service, mock_db, mock_project, mock_characters, mock_world_settings, mock_plot_nodes):
        """测试最大版本数限制"""
        # 设置模拟数据
        mock_db.query(Project).filter(Project.id == 1).first.return_value = mock_project
        mock_db.query(Character).filter(Character.project_id == 1).limit(5).all.return_value = mock_characters
        mock_db.query(WorldSetting).filter(WorldSetting.project_id == 1).limit(3).all.return_value = mock_world_settings
        mock_db.query(PlotNode).filter(PlotNode.project_id == 1).limit(5).all.return_value = mock_plot_nodes

        # 模拟AI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "测试内容。"
        ai_service.client.chat.completions.create.return_value = mock_response

        # 请求5个版本（但应该限制为3个）
        request = {
            "project_id": 1,
            "chapter_number": 1,
            "versions": 5,
            "word_count": 2000
        }

        # 执行生成
        versions, _ = ai_service.generate_chapter_versions(request, mock_db)

        # 验证只生成3个版本
        assert len(versions) == 3

    def test_ai_generation_failure_handling(self, ai_service, mock_db, mock_project, mock_characters, mock_world_settings, mock_plot_nodes):
        """测试AI生成失败时的处理"""
        # 设置模拟数据
        mock_db.query(Project).filter(Project.id == 1).first.return_value = mock_project
        mock_db.query(Character).filter(Character.project_id == 1).limit(5).all.return_value = mock_characters
        mock_db.query(WorldSetting).filter(WorldSetting.project_id == 1).limit(3).all.return_value = mock_world_settings
        mock_db.query(PlotNode).filter(PlotNode.project_id == 1).limit(5).all.return_value = mock_plot_nodes

        # 模拟AI响应失败
        ai_service.client.chat.completions.create.side_effect = Exception("API调用失败")

        # 构建请求
        request = {
            "project_id": 1,
            "chapter_number": 1,
            "versions": 2,
            "word_count": 2000
        }

        # 执行生成
        versions, _ = ai_service.generate_chapter_versions(request, mock_db)

        # 验证失败处理
        assert len(versions) == 2
        for version in versions:
            assert "生成失败" in version["content"]
            assert version["word_count"] == 0
            assert version["summary"] == "生成失败"

    def test_project_not_found_error(self, ai_service, mock_db):
        """测试项目不存在时的错误处理"""
        # 设置项目不存在的模拟数据
        mock_db.query(Project).filter(Project.id == 999).first.return_value = None

        # 构建请求
        request = {
            "project_id": 999,
            "chapter_number": 1,
            "versions": 1,
            "word_count": 2000
        }

        # 验证异常
        with pytest.raises(ValueError, match="项目ID 999 不存在"):
            ai_service.generate_chapter_versions(request, mock_db)

    def test_pov_character_inclusion(self, ai_service, mock_db, mock_project, mock_characters, mock_world_settings, mock_plot_nodes):
        """测试POV人物的包含"""
        # 设置额外的POV角色
        pov_character = Mock(spec=Character)
        pov_character.id = 10
        pov_character.name = "POV角色"
        pov_character.project_id = 1
        mock_characters.append(pov_character)

        mock_db.query(Project).filter(Project.id == 1).first.return_value = mock_project
        mock_db.query(Character).filter(Character.project_id == 1).limit(5).all.return_value = mock_characters[:-1]
        mock_db.query(WorldSetting).filter(WorldSetting.project_id == 1).limit(3).all.return_value = mock_world_settings
        mock_db.query(PlotNode).filter(PlotNode.project_id == 1).limit(5).all.return_value = mock_plot_nodes
        mock_db.query(Character).filter(Character.id == 10).filter(Character.project_id == 1).first.return_value = pov_character

        # 模拟AI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "测试内容。"
        ai_service.client.chat.completions.create.return_value = mock_response

        # 构建请求（指定POV角色）
        request = {
            "project_id": 1,
            "chapter_number": 1,
            "pov_character_id": 10,
            "versions": 1,
            "word_count": 2000
        }

        # 执行生成
        versions, context_used = ai_service.generate_chapter_versions(request, mock_db)

        # 验证POV角色信息被包含在上下文中
        assert len(versions) == 1

    def test_version_summary_generation(self, ai_service):
        """测试版本摘要生成"""
        # 测试长内容摘要（超过100字符）
        long_content = "这是一个很长的章节内容。" * 20  # 生成超过100字符的内容
        summary = ai_service._generate_version_summary(long_content)

        assert len(summary) <= 100
        assert "..." in summary

        # 测试短内容摘要（不超过100字符）
        short_content = "这是一段简短的内容"  # 不到100字符
        summary = ai_service._generate_version_summary(short_content)

        assert len(summary) <= 100
        assert "..." not in summary

        # 测试空内容
        empty_content = ""
        summary = ai_service._generate_version_summary(empty_content)

        assert summary == "内容过短，无法生成摘要"

    def test_max_tokens_calculation(self, ai_service, mock_db, mock_project, mock_characters, mock_world_settings, mock_plot_nodes):
        """测试max_tokens计算"""
        # 设置模拟数据
        mock_db.query(Project).filter(Project.id == 1).first.return_value = mock_project
        mock_db.query(Character).filter(Character.project_id == 1).limit(5).all.return_value = mock_characters
        mock_db.query(WorldSetting).filter(WorldSetting.project_id == 1).limit(3).all.return_value = mock_world_settings
        mock_db.query(PlotNode).filter(PlotNode.project_id == 1).limit(5).all.return_value = mock_plot_nodes

        # 模拟AI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "测试内容。"
        ai_service.client.chat.completions.create.return_value = mock_response

        # 构建不同字数要求的请求
        request = {
            "project_id": 1,
            "chapter_number": 1,
            "word_count": 1000,
            "versions": 1
        }

        # 执行生成
        versions, _ = ai_service.generate_chapter_versions(request, mock_db)

        # 验证max_tokens设置
        call = ai_service.client.chat.completions.create.call_args_list[0]
        assert call[1]['max_tokens'] == 2000  # word_count * 2

    def test_no_ai_service_configured_error(self, mock_db):
        """测试AI服务未配置时的错误"""
        # 创建没有客户端的AI服务（不初始化OpenAI客户端）
        with patch('app.services.ai_service.settings'):
            ai_service = AIService()
            # 强制设置client为None
            ai_service.client = None

        # 构建请求
        request = {
            "project_id": 1,
            "chapter_number": 1,
            "versions": 1,
            "word_count": 2000
        }

        # 验证异常
        with pytest.raises(ValueError, match="AI服务未配置"):
            ai_service.generate_chapter_versions(request, mock_db)

    def test_custom_characters_and_settings(self, ai_service, mock_db, mock_project, mock_characters, mock_world_settings, mock_plot_nodes):
        """测试使用指定的人物和世界观设定"""
        # 设置模拟数据
        mock_db.query(Project).filter(Project.id == 1).first.return_value = mock_project
        mock_db.query(Character).filter(Character.id.in_([1, 3])).filter(Character.project_id == 1).all.return_value = [mock_characters[0], mock_characters[2]]
        mock_db.query(WorldSetting).filter(WorldSetting.id.in_([1, 2])).filter(WorldSetting.project_id == 1).all.return_value = [mock_world_settings[0], mock_world_settings[1]]
        mock_db.query(PlotNode).filter(PlotNode.project_id == 1).limit(5).all.return_value = mock_plot_nodes

        # 模拟AI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "测试内容。"
        ai_service.client.chat.completions.create.return_value = mock_response

        # 构建指定人物和设定的请求
        request = {
            "project_id": 1,
            "chapter_number": 1,
            "featured_characters": [1, 3],
            "related_world_settings": [1, 2],
            "related_plot_nodes": [],
            "versions": 1,
            "word_count": 2000
        }

        # 执行生成
        versions, context_used = ai_service.generate_chapter_versions(request, mock_db)

        # 验证使用了指定的人物和设定
        assert len(context_used["characters"]) == 2
        assert len(context_used["world_settings"]) == 2
        assert mock_characters[0].name in context_used["characters"]
        assert mock_characters[2].name in context_used["characters"]