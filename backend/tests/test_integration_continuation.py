import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.chapter import Chapter
from app.models.character import Character, CharacterRole
from app.models.world_setting import WorldSetting, SettingType
from app.models.plot_node import PlotNode, PlotType, PlotImportance
from app.models.content_generation_draft import ContentGenerationDraft
from main import app
from app.schemas.content_generation import GenerationMode, FirstChapterMode, ContinueMode, SelectVersionRequest, TransitionType
from app.schemas.context_analysis import ContextAnalysisRequest
import json
from datetime import datetime


class TestIntegrationContinuation:
    """智能续写工作流集成测试"""

    @pytest.fixture(scope="function")
    def test_client(self):
        """创建测试客户端"""
        Base.metadata.create_all(bind=engine)
        with TestClient(app) as client:
            yield client
        Base.metadata.drop_all(bind=engine)

    @pytest.fixture(scope="function")
    def test_user(self, db: Session):
        """创建测试用户"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123",
            is_active=1
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @pytest.fixture(scope="function")
    def auth_header(self, test_user):
        """创建认证头"""
        return {"Authorization": f"Bearer {self.get_jwt_token(test_user)}"}

    def get_jwt_token(self, user: User) -> str:
        """获取JWT令牌"""
        # 这里简化处理，实际项目中需要通过登录接口获取
        return f"fake_token_for_user_{user.id}"

    @pytest.fixture(scope="function")
    def test_project(self, db: Session, test_user):
        """创建测试项目"""
        project = Project(
            title="测试小说：修仙之旅",
            author="测试作者",
            genre='["玄幻", "修仙"]',
            summary="一个普通的青年在意外中获得修仙传承，踏上修仙之路的故事。",
            style="轻松幽默",
            target_words_per_chapter=2000,
            status=ProjectStatus.DRAFT,
            user_id=test_user.id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @pytest.fixture(scope="function")
    def test_characters(self, db: Session, test_project):
        """创建测试角色"""
        characters = [
            Character(
                project_id=test_project.id,
                name="林辰",
                role=CharacterRole.PROTAGONIST,
                personality="乐观、善良、勇敢",
                core_motivation="保护家人，追求天道",
                age=20,
                gender="男",
                character_arc="initial",
                voice_style="沉稳有力",
                sample_dialogue="我一定会变强的！"
            ),
            Character(
                project_id=test_project.id,
                name="张天",
                role=CharacterRole.ANTAGONIST,
                personality="心高气傲，狠毒残忍",
                core_motivation="掌控一切，唯我独尊",
                age=50,
                gender="男",
                character_arc="initial",
                voice_style="阴沉低沉",
                sample_dialogue="没有人能阻挡我！"
            ),
            Character(
                project_id=test_project.id,
                name="李师傅",
                role=CharacterRole.SUPPORTING,
                personality="慈祥智慧，深藏不露",
                core_motivation="传授道法，保护苍生",
                age=70,
                gender="男",
                character_arc="initial",
                voice_style="温和从容",
                sample_dialogue="孩子，修仙之路千万要小心。"
            )
        ]
        db.add_all(characters)
        db.commit()
        return characters

    @pytest.fixture(scope="function")
    def test_world_settings(self, db: Session, test_project):
        """创建测试世界观设定"""
        settings = [
            WorldSetting(
                project_id=test_project.id,
                name="修仙世界",
                setting_type=SettingType.ERA,
                description="一个凡人可以修仙成仙的世界，分为凡人界、修仙界、仙界三个层次。",
                is_core_rule=1
            ),
            WorldSetting(
                project_id=test_project.id,
                name="灵力体系",
                setting_type=SettingType.POWER,
                description="通过吸收天地灵力，修炼成为更强者的体系。分为练气、筑基、金丹、元婴、化神、合体、大乘、渡劫八大境界。",
                is_core_rule=1
            ),
            WorldSetting(
                project_id=test_project.id,
                name="天剑门",
                setting_type=SettingType.FACTION,
                description="修仙门派之一，以剑修闻名，门规森严。",
                is_core_rule=0
            )
        ]
        db.add_all(settings)
        db.commit()
        return settings

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
    async def authenticated_client(self, test_client, test_user):
        """带认证的异步客户端"""
        # 模拟认证中间件
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = test_user

            # 设置认证头
            test_client.headers.update({
                "Authorization": f"Bearer fake_token"
            })
            yield test_client

    @pytest.fixture(scope="function")
    def mock_current_user(self):
        """模拟当前用户"""
        with patch('app.core.dependencies.get_current_user') as mock:
            mock_user = User(
                id=1,
                email="test@example.com",
                username="testuser",
                hashed_password="hashedpassword123"
            )
            mock.return_value = mock_user
            yield mock

    def test_full_first_chapter_flow(self, db: Session, authenticated_client, test_user, test_project,
                                   test_characters, test_world_settings, mock_ai_service):
        """测试完整的第一章生成流程"""
        # 步骤1：创建项目（已存在）

        # 步骤2：创建角色（已存在）

        # 步骤3：调用生成API（first_chapter_mode）
        request_data = {
            "mode": "simple",
            "project_id": test_project.id,
            "chapter_number": 1,
            "first_chapter_mode": {
                "opening_scene": "山村青年在山中发现神秘古籍",
                "key_elements": ["修仙", "奇遇", "主角成长"],
                "tone": "轻松愉快"
            },
            "word_count": 2000,
            "versions": 3
        }

        response = authenticated_client.post(
            f"/api/chapters/generate",
            json=request_data
        )

        print(f"生成第一章响应状态: {response.status_code}")
        print(f"生成第一章响应内容: {response.text}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["code"] == 200

        data = response_data["data"]
        # 实际的响应应该包含生成的版本信息
        assert "chapter_id" in data
        assert "versions" in data
        assert len(data["versions"]) == 3

        # 注意：这里的chapter_id是章节号（1），不是数据库ID
        chapter_number = data["chapter_id"]

        # 步骤4：验证草稿是否创建（通过chapter_number过滤）
        drafts = db.query(ContentGenerationDraft).filter(
            ContentGenerationDraft.chapter_number == chapter_number
        ).all()
        assert len(drafts) == 3

        # 步骤5：选择版本
        select_data = {
            "version_id": data["versions"][0]["version_id"],
            "edited_content": "这是用户编辑后的内容"
        }

        # 获取实际的章节ID（需要先创建章节）
        chapter = db.query(Chapter).filter(
            Chapter.project_id == test_project.id,
            Chapter.chapter_number == chapter_number
        ).first()

        if not chapter:
            # 如果章节不存在，需要先创建
            chapter = Chapter(
                project_id=test_project.id,
                chapter_number=chapter_number,
                title=f"第{chapter_number}章"
            )
            db.add(chapter)
            db.commit()
            db.refresh(chapter)

        select_response = authenticated_client.post(
            f"/api/chapters/{chapter.id}/select-version",
            json=select_data
        )

        assert select_response.status_code == 200
        select_data_response = select_response.json()
        assert select_data_response["code"] == 200

        # 步骤6：验证章节内容是否更新
        chapter_updated = db.query(Chapter).filter(Chapter.id == chapter.id).first()
        assert chapter_updated is not None
        assert chapter_updated.content is not None
        assert chapter_updated.word_count > 0

    def test_full_continuation_flow(self, db: Session, authenticated_client, test_user, test_project,
                                  test_characters, test_world_settings, mock_ai_service):
        """测试完整的续写流程"""
        # 步骤1：创建项目（已存在）

        # 步骤2：创建第一章（手动创建）
        chapter1 = Chapter(
            project_id=test_project.id,
            chapter_number=1,
            title="第一章：奇遇",
            content="""
林辰是一名普通的山村青年，每天除了打柴就是照顾生病的妹妹。这天，他在后山采药时，意外发现了一个神秘的洞穴。
洞穴深处，一具白骨手中紧握着一本泛黄的古籍。林辰好奇地拿起古籍，发现上面记载着失传已久的修仙功法《太上清心诀》。
就在他触摸古籍的瞬间，一股强大的力量涌入体内，他的经脉开始自行运转，丹田中凝聚出一缕微弱的灵力。
"这是什么？难道我遇到了传说中的仙人遗宝？"林辰震惊地想着。
            """,
            summary="林辰发现修仙古籍，获得传承",
            status="completed",
            word_count=158
        )
        db.add(chapter1)
        db.commit()

        # 步骤3：调用上下文分析API
        context_request = {
            "project_id": test_project.id,
            "chapter_number": 2,
            "plot_direction": "开始正式修炼",
            "previous_chapter_id": chapter1.id
        }

        context_response = authenticated_client.post(
            "/api/chapters/analyze-context",
            json=context_request
        )

        assert context_response.status_code == 200
        context_data = context_response.json()
        assert context_data["code"] == 200

        # 步骤4：调用生成API（continue_mode）
        request_data = {
            "mode": "standard",
            "project_id": test_project.id,
            "chapter_number": 2,
            "continue_mode": {
                "previous_chapter_id": chapter1.id,
                "transition": "immediate",
                "plot_direction": "开始正式修炼"
            },
            "word_count": 2000,
            "versions": 3,
            "suggested_context": context_data["data"]["validated_characters"][0]["id"]
        }

        response = authenticated_client.post(
            f"/api/chapters/generate",
            json=request_data
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["code"] == 200

        data = response_data["data"]
        chapter_number = data["chapter_id"]

        # 步骤5：验证草稿是否创建
        drafts = db.query(ContentGenerationDraft).filter(
            ContentGenerationDraft.chapter_number == chapter_number
        ).all()
        assert len(drafts) == 3

        # 步骤6：选择版本
        select_data = {
            "version_id": data["versions"][0]["version_id"]
        }

        # 获取实际的章节ID
        chapter = db.query(Chapter).filter(
            Chapter.project_id == test_project.id,
            Chapter.chapter_number == chapter_number
        ).first()

        if not chapter:
            # 如果章节不存在，需要先创建
            chapter = Chapter(
                project_id=test_project.id,
                chapter_number=chapter_number,
                title=f"第{chapter_number}章"
            )
            db.add(chapter)
            db.commit()
            db.refresh(chapter)

        select_response = authenticated_client.post(
            f"/api/chapters/{chapter.id}/select-version",
            json=select_data
        )

        assert select_response.status_code == 200

        # 步骤7：验证第二章内容
        chapter2 = db.query(Chapter).filter(Chapter.id == chapter.id).first()
        assert chapter2 is not None
        assert chapter2.content is not None
        assert chapter2.word_count > 0
        assert chapter2.chapter_number == chapter_number

    def test_context_analysis_flow(self, db: Session, authenticated_client, test_user, test_project,
                                  test_characters, test_world_settings):
        """测试上下文分析流程"""
        # 步骤1：创建项目和实体（已存在）

        # 步骤2：调用analyze-context API
        request_data = {
            "project_id": test_project.id,
            "chapter_number": 3,
            "plot_direction": "遭遇挑战",
            "previous_chapter_id": 1
        }

        response = authenticated_client.post(
            "/api/chapters/analyze-context",
            json=request_data
        )

        print(f"上下文分析响应状态: {response.status_code}")
        print(f"上下文分析响应内容: {response.text}")

        # 步骤3：验证响应
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["code"] == 200

        data = response_data["data"]

        # 步骤4：验证建议返回
        assert "validated_characters" in data
        assert "validated_world_settings" in data
        assert "validated_plot_nodes" in data

        # 步骤5：验证建议引用有效ID
        for char in data["validated_characters"]:
            assert char["id"] > 0
            assert "name" in char
            assert "role" in char
            assert "reason" in char

        for setting in data["validated_world_settings"]:
            assert setting["id"] > 0
            assert setting["type"] in ["era", "region", "rules", "culture", "power", "location", "faction", "item", "event"]
            assert setting["is_core_rule"] in [0, 1]

        for plot in data["validated_plot_nodes"]:
            assert plot["id"] > 0
            assert plot["type"] in ["关键情节", "重要转折", "背景情节", "支线情节"]
            assert plot["importance"] in ["重要", "一般", "次要"]

        # 步骤6：验证分析摘要
        assert "summary" in data
        assert len(data["summary"]) > 0

    @pytest.fixture(scope="function")
    def test_token_generator(self):
        """模拟JWT令牌生成器"""
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            def mock_user(token):
                # 简化的模拟，返回测试用户
                from app.models.user import User
                return User(
                    id=1,
                    email="test@example.com",
                    username="testuser"
                )

            mock_get_user.side_effect = mock_user
            yield mock_get_user