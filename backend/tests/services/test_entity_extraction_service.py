import pytest
from unittest.mock import Mock, MagicMock
from app.services.entity_extraction_service import EntityExtractionService
from app.models.character import Character
from app.models.world_setting import WorldSetting

# Tests for _is_similar_name (existing tests)
def test_is_similar_name_exact_match():
    """测试完全相同的名称"""
    service = EntityExtractionService()
    assert service._is_similar_name("张三", "张三") == True

def test_is_similar_name_high_similarity():
    """测试高相似度名称"""
    service = EntityExtractionService()
    # "张三" vs "张小三" 相似度约 0.8 >= 0.7，应该相似
    assert service._is_similar_name("张三", "张小三") == True
    # "剑派" vs "剑派" 相似度 1.0 >= 0.7，应该相似
    assert service._is_similar_name("剑派", "剑派") == True

def test_is_similar_name_custom_threshold():
    """测试自定义阈值"""
    service = EntityExtractionService()
    # 使用更低的阈值 0.6
    assert service._is_similar_name("张三", "张小三", threshold=0.6) == True

def test_is_similar_name_empty_strings():
    """测试空字符串"""
    service = EntityExtractionService()
    assert service._is_similar_name("", "") == True


# Tests for _deduplicate_characters (Task 4)
def test_deduplicate_characters_removes_duplicates():
    """测试移除重复人物"""
    service = EntityExtractionService()
    existing = [Character(id=1, name="张三", project_id=1)]
    detected = [
        {"name": "张三", "age": 25},  # 重复
        {"name": "李四", "age": 30},  # 新人物
    ]
    result = service._deduplicate_characters(detected, existing)
    assert len(result) == 1
    assert result[0]["name"] == "李四"

def test_deduplicate_characters_handles_empty_lists():
    """测试空列表"""
    service = EntityExtractionService()
    result = service._deduplicate_characters([], [])
    assert result == []

def test_deduplicate_characters_handles_similar_names():
    """测试相似名称"""
    service = EntityExtractionService()
    existing = [Character(id=1, name="张三", project_id=1)]
    detected = [
        {"name": "张小三", "age": 25},  # 相似名称，应该被过滤
        {"name": "李四", "age": 30},
    ]
    result = service._deduplicate_characters(detected, existing)
    assert len(result) == 1
    assert result[0]["name"] == "李四"

def test_deduplicate_characters_skips_empty_names():
    """测试跳过空名称"""
    service = EntityExtractionService()
    existing = []
    detected = [
        {"name": "", "age": 25},  # 空名称
        {"name": "李四", "age": 30},
    ]
    result = service._deduplicate_characters(detected, existing)
    assert len(result) == 1
    assert result[0]["name"] == "李四"


# Tests for _deduplicate_world_settings (Task 5)
def test_deduplicate_world_settings():
    """测试世界观设定去重"""
    service = EntityExtractionService()
    existing = [WorldSetting(id=1, name="青云剑派", project_id=1, setting_type="faction")]
    detected = [
        {"name": "青云剑派", "setting_type": "faction"},  # 重复
        {"name": "华山派", "setting_type": "faction"},  # 新设定
    ]
    result = service._deduplicate_world_settings(detected, existing)
    assert len(result) == 1
    assert result[0]["name"] == "华山派"

def test_deduplicate_world_settings_empty_lists():
    """测试空列表"""
    service = EntityExtractionService()
    result = service._deduplicate_world_settings([], [])
    assert result == []

def test_deduplicate_world_settings_similar_names():
    """测试相似名称"""
    service = EntityExtractionService()
    existing = [WorldSetting(id=1, name="青云剑派", project_id=1, setting_type="faction")]
    detected = [
        {"name": "青云派", "setting_type": "faction"},  # 相似名称
        {"name": "华山派", "setting_type": "faction"},
    ]
    result = service._deduplicate_world_settings(detected, existing)
    assert len(result) == 1
    assert result[0]["name"] == "华山派"


# Tests for _detect_characters (Task 6)
def test_detect_characters_calls_ai():
    """测试 AI 检测人物调用"""
    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"characters": [{"name": "张三", "age": 25}]}'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    existing_chars = []
    result = service._detect_characters("章节内容", existing_chars)

    assert len(result) == 1
    assert result[0]["name"] == "张三"
    assert result[0]["age"] == 25

def test_detect_characters_with_markdown_json():
    """测试处理 markdown JSON 格式"""
    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='```json\n{"characters": [{"name": "李四"}]}\n```'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    result = service._detect_characters("内容", [])
    assert len(result) == 1
    assert result[0]["name"] == "李四"

def test_detect_characters_uninitialized_ai():
    """测试 AI 服务未初始化"""
    service = EntityExtractionService(ai_service=None)
    result = service._detect_characters("内容", [])
    assert result == []

def test_detect_characters_json_decode_error():
    """测试 JSON 解析失败"""
    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='not valid json'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    result = service._detect_characters("内容", [])
    assert result == []


# Tests for _detect_world_settings (Task 7)
def test_detect_world_settings_calls_ai():
    """测试 AI 检测世界观设定调用"""
    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"world_settings": [{"name": "青云剑派", "setting_type": "faction"}]}'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    existing_settings = []
    result = service._detect_world_settings("章节内容", existing_settings)

    assert len(result) == 1
    assert result[0]["name"] == "青云剑派"
    assert result[0]["setting_type"] == "faction"

def test_detect_world_settings_with_markdown():
    """测试处理 markdown 格式"""
    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='```\n{"world_settings": [{"name": "华山派"}]}\n```'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    result = service._detect_world_settings("内容", [])
    assert len(result) == 1
    assert result[0]["name"] == "华山派"

def test_detect_world_settings_uninitialized_ai():
    """测试 AI 服务未初始化"""
    service = EntityExtractionService(ai_service=None)
    result = service._detect_world_settings("内容", [])
    assert result == []

def test_detect_world_settings_json_error():
    """测试 JSON 解析失败"""
    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='invalid json'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    result = service._detect_world_settings("内容", [])
    assert result == []


# Tests for extract_characters (Task 8) - Integration tests
def test_extract_characters_to_database(db):
    """测试提取人物到数据库"""
    from app.models.project import Project
    from app.models.user import User
    import uuid

    # Create a test user first with unique email
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"test_{unique_id}@example.com",
        username=f"testuser_{unique_id}",
        hashed_password="hash"
    )
    db.add(user)
    db.flush()

    project = Project(title="测试项目", user_id=user.id, author="测试作者", genre="测试类型")
    db.add(project)
    db.flush()

    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"characters": [{"name": "张三", "age": 25, "role": "supporting"}]}'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    result = service.extract_characters(db=db, project_id=project.id, content="章节内容")

    assert result["added"] == 1
    assert result["skipped"] == 0

    characters = db.query(Character).filter(Character.project_id == project.id).all()
    assert len(characters) == 1
    assert characters[0].name == "张三"
    assert characters[0].age == 25

def test_extract_characters_empty_content():
    """测试空内容"""
    service = EntityExtractionService(ai_service=Mock())
    result = service.extract_characters(db=None, project_id=1, content="")
    # Should handle empty content gracefully
    assert result == {"added": 0, "skipped": 0}

def test_extract_characters_with_duplicates(db):
    """测试处理重复人物"""
    from app.models.project import Project
    from app.models.user import User
    import uuid

    # Create a test user first with unique email
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"test_{unique_id}@example.com",
        username=f"testuser_{unique_id}",
        hashed_password="hash"
    )
    db.add(user)
    db.flush()

    project = Project(title="测试项目", user_id=user.id, author="测试作者", genre="测试类型")
    db.add(project)
    db.flush()

    # Create existing character
    existing_char = Character(name="张三", project_id=project.id)
    db.add(existing_char)
    db.flush()

    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"characters": [{"name": "张三", "age": 25}, {"name": "李四", "age": 30}]}'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    result = service.extract_characters(db=db, project_id=project.id, content="内容")

    assert result["added"] == 1  # Only 李四
    assert result["skipped"] == 1  # 张三 was skipped

    characters = db.query(Character).filter(Character.project_id == project.id).all()
    assert len(characters) == 2  # 张三 (existing) + 李四 (new)

def test_extract_characters_no_detection(db):
    """测试 AI 未检测到人物"""
    from app.models.project import Project
    from app.models.user import User
    import uuid

    # Create a test user first with unique email
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"test_{unique_id}@example.com",
        username=f"testuser_{unique_id}",
        hashed_password="hash"
    )
    db.add(user)
    db.flush()

    project = Project(title="测试项目", user_id=user.id, author="测试作者", genre="测试类型")
    db.add(project)
    db.flush()

    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"characters": []}'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    result = service.extract_characters(db=db, project_id=project.id, content="内容")

    assert result["added"] == 0
    assert result["skipped"] == 0


# Tests for extract_world_settings (Task 9) - Integration tests
def test_extract_world_settings_to_database(db):
    """测试提取世界观设定到数据库"""
    from app.models.project import Project
    from app.models.user import User
    import uuid

    # Create a test user first with unique email
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"test_{unique_id}@example.com",
        username=f"testuser_{unique_id}",
        hashed_password="hash"
    )
    db.add(user)
    db.flush()

    project = Project(title="测试项目", user_id=user.id, author="测试作者", genre="测试类型")
    db.add(project)
    db.flush()

    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"world_settings": [{"name": "青云剑派", "setting_type": "faction"}]}'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    result = service.extract_world_settings(db=db, project_id=project.id, content="章节内容")

    assert result["added"] == 1
    assert result["skipped"] == 0

    settings = db.query(WorldSetting).filter(WorldSetting.project_id == project.id).all()
    assert len(settings) == 1
    assert settings[0].name == "青云剑派"
    assert settings[0].setting_type == "faction"

def test_extract_world_settings_empty_content():
    """测试空内容"""
    service = EntityExtractionService(ai_service=Mock())
    result = service.extract_world_settings(db=None, project_id=1, content="")
    # Should handle empty content gracefully
    assert result == {"added": 0, "skipped": 0}

def test_extract_world_settings_with_duplicates(db):
    """测试处理重复设定"""
    from app.models.project import Project
    from app.models.user import User
    import uuid

    # Create a test user first with unique email
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"test_{unique_id}@example.com",
        username=f"testuser_{unique_id}",
        hashed_password="hash"
    )
    db.add(user)
    db.flush()

    project = Project(title="测试项目", user_id=user.id, author="测试作者", genre="测试类型")
    db.add(project)
    db.flush()

    # Create existing setting
    existing_setting = WorldSetting(name="青云剑派", project_id=project.id, setting_type="faction")
    db.add(existing_setting)
    db.flush()

    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"world_settings": [{"name": "青云剑派", "setting_type": "faction"}, {"name": "华山派", "setting_type": "faction"}]}'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    result = service.extract_world_settings(db=db, project_id=project.id, content="内容")

    assert result["added"] == 1  # Only 华山派
    assert result["skipped"] == 1  # 青云剑派 was skipped

    settings = db.query(WorldSetting).filter(WorldSetting.project_id == project.id).all()
    assert len(settings) == 2  # 青云剑派 (existing) + 华山派 (new)

def test_extract_world_settings_no_detection(db):
    """测试 AI 未检测到设定"""
    from app.models.project import Project
    from app.models.user import User
    import uuid

    # Create a test user first with unique email
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"test_{unique_id}@example.com",
        username=f"testuser_{unique_id}",
        hashed_password="hash"
    )
    db.add(user)
    db.flush()

    project = Project(title="测试项目", user_id=user.id, author="测试作者", genre="测试类型")
    db.add(project)
    db.flush()

    mock_ai_service = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"world_settings": []}'))]
    mock_ai_service.client.chat.completions.create.return_value = mock_response

    service = EntityExtractionService(ai_service=mock_ai_service)
    result = service.extract_world_settings(db=db, project_id=project.id, content="内容")

    assert result["added"] == 0
    assert result["skipped"] == 0