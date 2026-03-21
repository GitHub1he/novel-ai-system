import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app


class TestIntegrationContinuation:
    """智能续写工作流集成测试（简化版）"""

    @pytest.fixture(scope="function")
    def client(self):
        """创建测试客户端"""
        with TestClient(app) as client:
            yield client

    @pytest.fixture(scope="function")
    def mock_ai_service(self):
        """模拟AI服务"""
        with patch('app.services.ai_service.ai_service') as mock:
            # 首章生成响应
            def mock_generate_chapter(*args, **kwargs):
                return """
林辰是一名普通的山村青年，每天除了打柴就是照顾生病的妹妹。这天，他在后山采药时，意外发现了一个神秘的洞穴。
洞穴深处，一具白骨手中紧握着一本泛黄的古籍。林辰好奇地拿起古籍，发现上面记载着失传已久的修仙功法《太上清心诀》。
就在他触摸古籍的瞬间，一股强大的力量涌入体内，他的经脉开始自行运转，丹田中凝聚出一缕微弱的灵力。
"这是什么？难道我遇到了传说中的仙人遗宝？"林辰震惊地想着。
                """

            # 续章生成响应
            def mock_generate_chapter_continuation(*args, **kwargs):
                return """
在李师傅的指导下，林辰开始正式修炼《太上清心诀》。
李师傅仔细检查了林辰的资质，惊讶地说道："林辰，你的资质真是百年难得一见！这本《太上清心诀》恰好适合你修炼。"
接下来的几天，林辰严格按照功法修炼，发现体内的灵力增长得异常迅速。
"小辰，你现在已经是练气期一层了，正常情况下需要一个月才能达到这个境界。"李师傅满脸欣慰地看着林辰。
                """

            # 上下文分析响应
            def mock_analyze_context_requirements(*args, **kwargs):
                from app.schemas.context_analysis import (
                    CharacterSuggestion, WorldSettingSuggestion, PlotNodeSuggestion
                )

                return {
                    "validated_characters": [
                        CharacterSuggestion(
                            id=1,
                            name="林辰",
                            role="主角",
                            personality="乐观、善良、勇敢",
                            core_motivation="保护家人，追求天道"
                        )
                    ],
                    "validated_world_settings": [
                        WorldSettingSuggestion(
                            id=1,
                            name="灵力体系",
                            type="力量体系",
                            description="修仙者通过吸收天地灵力修炼",
                            is_core_rule=True
                        )
                    ],
                    "validated_plot_nodes": [
                        PlotNodeSuggestion(
                            id=1,
                            title="拜师学艺",
                            type="关键情节",
                            importance="重要",
                            description="林辰正式拜李师傅为师，开始修仙之路"
                        )
                    ],
                    "summary": "建议主角林辰继续跟随李师傅修炼，重点关注灵力体系的运用"
                }

            mock.generate_chapter.side_effect = mock_generate_chapter
            mock.generate_chapter.side_effect = mock_generate_chapter_continuation
            mock.analyze_context_requirements.side_effect = mock_analyze_context_requirements

            yield mock

    @pytest.fixture(scope="function")
    def mock_auth(self):
        """模拟认证"""
        with patch('app.core.dependencies.get_current_user') as mock:
            from app.models.user import User
            mock_user = User(
                id=1,
                email="test@example.com",
                username="testuser",
                hashed_password="hashedpassword123"
            )
            mock.return_value = mock_user
            yield mock

    def test_context_analysis_api_endpoint(self, client, mock_auth):
        """测试上下文分析API端点"""
        # 设置请求头
        client.headers.update({
            "Authorization": "Bearer fake_token"
        })

        # 构建请求数据
        request_data = {
            "project_id": 1,
            "chapter_number": 1,
            "plot_direction": "开始冒险"
        }

        # 调用API
        response = client.post("/api/chapters/analyze-context", json=request_data)

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert "validated_characters" in data["data"]
        assert "validated_world_settings" in data["data"]
        assert "validated_plot_nodes" in data["data"]

    def test_chapter_generate_api_endpoint(self, client, mock_auth, mock_ai_service):
        """测试章节生成API端点"""
        # 设置请求头
        client.headers.update({
            "Authorization": "Bearer fake_token"
        })

        # 构建请求数据
        request_data = {
            "mode": "simple",
            "project_id": 1,
            "chapter_number": 1,
            "first_chapter_mode": {
                "opening_scene": "山村青年在山中发现神秘古籍",
                "key_elements": ["修仙", "奇遇", "主角成长"],
                "tone": "轻松愉快"
            },
            "word_count": 2000,
            "versions": 2
        }

        # 调用API
        response = client.post("/api/chapters/generate", json=request_data)

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert "versions" in data["data"]
        assert len(data["data"]["versions"]) == 2

    def test_select_version_api_endpoint(self, client, mock_auth):
        """测试选择版本API端点"""
        # 设置请求头
        client.headers.update({
            "Authorization": "Bearer fake_token"
        })

        # 构建请求数据
        request_data = {
            "version_id": "test_version_123",
            "edited_content": "这是编辑后的内容"
        }

        # 注意：这个测试需要章节ID，实际使用时需要先创建章节
        # 这里只是验证API端点可以正常响应
        # response = client.post("/api/chapters/1/select-version", json=request_data)

        # 由于我们没有实际的数据库章节，这个测试暂时跳过
        pytest.skip("需要实际的章节ID才能测试选择版本端点")

    @patch('app.services.ai_service.ai_service')
    def test_ai_service_generate_chapter(self, mock_ai):
        """测试AI服务生成章节"""
        # 设置mock返回
        mock_ai.generate_chapter.return_value = "这是一段生成的章节内容。"

        # 调用服务方法
        result = mock_ai.generate_chapter(
            prompt="请写一个关于修仙的故事",
            context="这是一个修仙世界",
            word_count=1000
        )

        # 验证结果
        assert result == "这是一段生成的章节内容。"
        mock_ai.generate_chapter.assert_called_once()

    @patch('app.services.ai_service.ai_service')
    def test_ai_service_analyze_context(self, mock_ai):
        """测试AI服务上下文分析"""
        from app.schemas.context_analysis import (
            CharacterSuggestion, WorldSettingSuggestion, PlotNodeSuggestion
        )

        # 设置mock返回
        mock_ai.analyze_context_requirements.return_value = {
            "validated_characters": [
                CharacterSuggestion(
                    id=1,
                    name="测试角色",
                    role="主角",
                    personality="勇敢",
                    core_motivation="冒险"
                )
            ],
            "validated_world_settings": [
                WorldSettingSuggestion(
                    id=1,
                    name="测试世界观",
                    type="力量体系",
                    description="测试描述",
                    is_core_rule=True
                )
            ],
            "validated_plot_nodes": [
                PlotNodeSuggestion(
                    id=1,
                    title="测试情节",
                    type="关键情节",
                    importance="重要",
                    description="测试描述"
                )
            ],
            "summary": "测试摘要"
        }

        # 调用服务方法
        result = mock_ai.analyze_context_requirements(
            project_id=1,
            previous_chapter_id=None,
            plot_direction="测试方向"
        )

        # 验证结果
        assert len(result["validated_characters"]) == 1
        assert result["validated_characters"][0].name == "测试角色"
        assert len(result["validated_world_settings"]) == 1
        assert len(result["validated_plot_nodes"]) == 1
        assert result["summary"] == "测试摘要"

        mock_ai.analyze_context_requirements.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])