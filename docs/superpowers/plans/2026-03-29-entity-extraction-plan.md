# AI 实体提取功能实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标:** 从章节内容中自动提取并创建人物和世界观设定，支持名称相似度去重

**架构:** 创建独立的 EntityExtractionService 处理实体提取逻辑，复用现有 AIService 进行 AI 调用，新增 API 端点供前端调用

**技术栈:** FastAPI, SQLAlchemy, Pydantic, OpenAI SDK (GLM-4), React, TypeScript, Ant Design

---

## 文件结构

### 新建文件
- `backend/app/services/entity_extraction_service.py` - 实体提取服务（核心逻辑）
- `backend/app/schemas/entity_extraction.py` - 数据验证模型
- `backend/tests/services/test_entity_extraction_service.py` - 服务单元测试
- `backend/tests/api/test_chapters_extraction.py` - API 集成测试

### 修改文件
- `backend/app/api/chapters.py` - 添加 `/extract-entities` 端点
- `backend/app/core/config.py` - 添加相似度阈值配置（可选）
- `frontend/src/services/api.ts` - 添加 API 调用方法
- `frontend/src/pages/ProjectDetail.tsx` - 添加"提取实体"按钮和事件处理

---

## Task 1: 添加相似度阈值配置

**目标:** 在配置文件中添加可调整的相似度阈值

**文件:**
- Modify: `backend/app/core/config.py:5-44`

- [ ] **Step 1: 添加配置字段**

在 `Settings` 类中添加实体提取相关配置：

```python
# 在 Settings 类中添加（约第 27 行后）
# 实体提取配置
ENTITY_SIMILARITY_THRESHOLD: float = 0.7  # 名称相似度阈值（0-1）
```

- [ ] **Step 2: 验证配置加载**

运行 Python 交互式测试：

```bash
cd backend
python -c "from app.core.config import settings; print(f'Threshold: {settings.ENTITY_SIMILARITY_THRESHOLD}')"
```

预期输出: `Threshold: 0.7`

- [ ] **Step 3: 提交**

```bash
git add backend/app/core/config.py
git commit -m "feat: add entity similarity threshold config"
```

---

## Task 2: 创建实体提取数据验证模型

**目标:** 创建 Pydantic 模型验证 AI 返回的实体数据

**文件:**
- Create: `backend/app/schemas/entity_extraction.py`
- Test: `backend/tests/schemas/test_entity_extraction.py`

- [ ] **Step 1: 编写失败的测试**

创建测试文件 `backend/tests/schemas/test_entity_extraction.py`:

```python
import pytest
from pydantic import ValidationError
from app.schemas.entity_extraction import (
    ExtractedCharacter,
    ExtractedWorldSetting,
    EntityExtractionResponse
)
from app.models.character import CharacterRole
from app.models.world_setting import SettingType

def test_extracted_character_valid():
    """测试有效的人物数据"""
    data = {
        "name": "张三",
        "age": 25,
        "gender": "男",
        "appearance": "身材高大",
        "identity": "剑客",
        "role": CharacterRole.SUPPORTING
    }
    character = ExtractedCharacter(**data)
    assert character.name == "张三"
    assert character.age == 25

def test_extracted_character_requires_name():
    """测试姓名为必填字段"""
    with pytest.raises(ValidationError):
        ExtractedCharacter(age=25)

def test_extracted_character_default_role():
    """测试默认角色为 SUPPORTING"""
    character = ExtractedCharacter(name="李四")
    assert character.role == CharacterRole.SUPPORTING

def test_extracted_world_setting_valid():
    """测试有效的世界观设定数据"""
    data = {
        "name": "青云剑派",
        "setting_type": SettingType.FACTION,
        "description": "著名的剑术门派"
    }
    setting = ExtractedWorldSetting(**data)
    assert setting.name == "青云剑派"
    assert setting.setting_type == SettingType.FACTION

def test_entity_extraction_response():
    """测试完整的提取响应"""
    data = {
        "characters": {"added": 5, "skipped": 2},
        "world_settings": {"added": 3, "skipped": 1}
    }
    response = EntityExtractionResponse(**data)
    assert response.characters["added"] == 5
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd backend
pytest tests/schemas/test_entity_extraction.py -v
```

预期: `ModuleNotFoundError: No module named 'app.schemas.entity_extraction'`

- [ ] **Step 3: 实现最小化的 Pydantic 模型**

创建 `backend/app/schemas/entity_extraction.py`:

```python
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict
from app.models.character import CharacterRole
from app.models.world_setting import SettingType


class ExtractedCharacter(BaseModel):
    """AI 提取的人物数据"""
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    appearance: Optional[str] = None
    identity: Optional[str] = None
    hometown: Optional[str] = None
    role: CharacterRole = CharacterRole.SUPPORTING  # AI 未明确指定时的默认值
    personality: Optional[str] = None
    core_motivation: Optional[str] = None
    fears: Optional[str] = None
    desires: Optional[str] = None


class ExtractedWorldSetting(BaseModel):
    """AI 提取的世界观设定数据"""
    name: str
    setting_type: SettingType
    description: Optional[str] = None
    attributes: Optional[Dict] = None
    is_core_rule: int = 0


class EntityExtractionResponse(BaseModel):
    """实体提取响应"""
    characters: Dict[str, int]  # {"added": 5, "skipped": 2}
    world_settings: Dict[str, int]
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd backend
pytest tests/schemas/test_entity_extraction.py -v
```

预期: 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add backend/app/schemas/entity_extraction.py tests/schemas/test_entity_extraction.py
git commit -m "feat: add entity extraction data validation schemas"
```

---

## Task 3: 实现名称相似度匹配函数

**目标:** 实现基于编辑距离的名称相似度判断

**文件:**
- Create: `backend/app/services/entity_extraction_service.py`
- Test: `backend/tests/services/test_entity_extraction_service.py`

- [ ] **Step 1: 编写失败的测试**

在 `backend/tests/services/test_entity_extraction_service.py` 中添加:

```python
import pytest
from app.services.entity_extraction_service import EntityExtractionService
from app.models.character import Character
from app.models.world_setting import WorldSetting

def test_is_similar_name_exact_match():
    """测试完全相同的名称"""
    service = EntityExtractionService()
    assert service._is_similar_name("张三", "张三") == True

def test_is_similar_name_high_similarity():
    """测试高相似度名称"""
    service = EntityExtractionService()
    # "张三" vs "张小三" 相似度约 0.67 < 0.7，应该不相似
    assert service._is_similar_name("张三", "张小三") == False
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
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_is_similar_name_exact_match -v
```

预期: `ModuleNotFoundError: No module named 'app.services.entity_extraction_service'`

- [ ] **Step 3: 实现最小化的服务类和相似度函数**

创建 `backend/app/services/entity_extraction_service.py`:

```python
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.character import Character
from app.models.world_setting import WorldSetting
from app.schemas.entity_extraction import (
    ExtractedCharacter,
    ExtractedWorldSetting
)
from app.services.ai_service import AIService
from app.core.config import settings
from app.core.logger import logger
from difflib import SequenceMatcher


class EntityExtractionService:
    """实体提取服务"""

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service

    def _is_similar_name(
        self,
        name1: str,
        name2: str,
        threshold: Optional[float] = None
    ) -> bool:
        """
        判断两个名称是否相似

        Args:
            name1: 第一个名称
            name2: 第二个名称
            threshold: 相似度阈值（0-1），默认使用配置文件中的值

        Returns:
            True if similar enough to be considered duplicate
        """
        if threshold is None:
            threshold = settings.ENTITY_SIMILARITY_THRESHOLD

        similarity = SequenceMatcher(None, name1, name2).ratio()
        return similarity >= threshold
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py -v
```

预期: 所有测试通过

- [ ] **Step 5: 提交**

```bash
git add backend/app/services/entity_extraction_service.py tests/services/test_entity_extraction_service.py
git commit -m "feat: implement name similarity matching function"
```

---

## Task 4: 实现人物去重方法

**目标:** 实现通过名称相似度过滤已有人物的逻辑

**文件:**
- Modify: `backend/app/services/entity_extraction_service.py`
- Test: `backend/tests/services/test_entity_extraction_service.py`

- [ ] **Step 1: 编写失败的测试**

在 `backend/tests/services/test_entity_extraction_service.py` 中添加:

```python
def test_deduplicate_characters_removes_duplicates():
    """测试去重逻辑移除重复人物"""
    service = EntityExtractionService()

    # 模拟已有人物
    existing = [
        Character(id=1, name="张三", project_id=1)
    ]

    # AI 检测到的人物（包含重复）
    detected = [
        {"name": "张三", "age": 25},  # 完全重复
        {"name": "李四", "age": 30},  # 新人物
    ]

    result = service._deduplicate_characters(detected, existing)

    assert len(result) == 1
    assert result[0]["name"] == "李四"

def test_deduplicate_characters_handles_empty_lists():
    """测试空列表处理"""
    service = EntityExtractionService()
    result = service._deduplicate_characters([], [])
    assert result == []
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_deduplicate_characters_removes_duplicates -v
```

预期: `AttributeError: 'EntityExtractionService' object has no attribute '_deduplicate_characters'`

- [ ] **Step 3: 实现去重方法**

在 `backend/app/services/entity_extraction_service.py` 中添加:

```python
    def _deduplicate_characters(
        self,
        detected: List[Dict[str, Any]],
        existing: List[Character]
    ) -> List[Dict[str, Any]]:
        """
        通过名称相似度过滤重复人物

        Args:
            detected: AI 检测到的人物列表
            existing: 数据库中已有人物列表

        Returns:
            过滤后的人物列表
        """
        unique_characters = []

        for detected_char in detected:
            detected_name = detected_char.get("name", "")
            if not detected_name:
                continue

            is_duplicate = False
            for existing_char in existing:
                if self._is_similar_name(detected_name, existing_char.name):
                    is_duplicate = True
                    logger.info(
                        f"跳过重复人物: {detected_name} "
                        f"(相似于 {existing_char.name})"
                    )
                    break

            if not is_duplicate:
                unique_characters.append(detected_char)

        return unique_characters
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_deduplicate_characters_removes_duplicates -v
```

预期: 测试通过

- [ ] **Step 5: 提交**

```bash
git add backend/app/services/entity_extraction_service.py tests/services/test_entity_extraction_service.py
git commit -m "feat: implement character deduplication logic"
```

---

## Task 5: 实现世界观设定去重方法

**目标:** 实现通过名称相似度过滤已有世界观设定的逻辑

**文件:**
- Modify: `backend/app/services/entity_extraction_service.py`
- Test: `backend/tests/services/test_entity_extraction_service.py`

- [ ] **Step 1: 编写失败的测试**

在 `backend/tests/services/test_entity_extraction_service.py` 中添加:

```python
def test_deduplicate_world_settings():
    """测试世界观设定去重"""
    service = EntityExtractionService()

    existing = [
        WorldSetting(id=1, name="青云剑派", project_id=1, setting_type="faction")
    ]

    detected = [
        {"name": "青云剑派", "setting_type": "faction"},  # 重复
        {"name": "华山派", "setting_type": "faction"},  # 新设定
    ]

    result = service._deduplicate_world_settings(detected, existing)

    assert len(result) == 1
    assert result[0]["name"] == "华山派"
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_deduplicate_world_settings -v
```

预期: `AttributeError: 'EntityExtractionService' object has no attribute '_deduplicate_world_settings'`

- [ ] **Step 3: 实现去重方法**

在 `backend/app/services/entity_extraction_service.py` 中添加:

```python
    def _deduplicate_world_settings(
        self,
        detected: List[Dict[str, Any]],
        existing: List[WorldSetting]
    ) -> List[Dict[str, Any]]:
        """
        通过名称相似度过滤重复世界观设定

        Args:
            detected: AI 检测到的设定列表
            existing: 数据库中已有设定列表

        Returns:
            过滤后的设定列表
        """
        unique_settings = []

        for detected_setting in detected:
            detected_name = detected_setting.get("name", "")
            if not detected_name:
                continue

            is_duplicate = False
            for existing_setting in existing:
                if self._is_similar_name(detected_name, existing_setting.name):
                    is_duplicate = True
                    logger.info(
                        f"跳过重复设定: {detected_name} "
                        f"(相似于 {existing_setting.name})"
                    )
                    break

            if not is_duplicate:
                unique_settings.append(detected_setting)

        return unique_settings
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_deduplicate_world_settings -v
```

预期: 测试通过

- [ ] **Step 5: 提交**

```bash
git add backend/app/services/entity_extraction_service.py tests/services/test_entity_extraction_service.py
git commit -m "feat: implement world setting deduplication logic"
```

---

## Task 6: 实现 AI 人物检测方法

**目标:** 实现调用 AI 检测章节中人物的逻辑

**文件:**
- Modify: `backend/app/services/entity_extraction_service.py`
- Test: `backend/tests/services/test_entity_extraction_service.py`

- [ ] **Step 1: 编写失败的测试（使用 mock）**

在 `backend/tests/services/test_entity_extraction_service.py` 中添加:

```python
from unittest.mock import Mock, patch

def test_detect_characters_calls_ai():
    """测试 AI 检测人物调用"""
    # Mock AI 服务
    mock_ai_service = Mock()
    mock_ai_service.client.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content='{"characters": [{"name": "张三", "age": 25}]}'))
    ]

    service = EntityExtractionService(ai_service=mock_ai_service)
    existing_chars = []

    result = service._detect_characters("章节内容", existing_chars)

    assert len(result) == 1
    assert result[0]["name"] == "张三"
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_detect_characters_calls_ai -v
```

预期: `AttributeError: 'EntityExtractionService' object has no attribute '_detect_characters'`

- [ ] **Step 3: 实现 AI 检测方法**

在 `backend/app/services/entity_extraction_service.py` 中添加:

```python
    def _detect_characters(
        self,
        content: str,
        existing_characters: List[Character]
    ) -> List[Dict[str, Any]]:
        """
        使用 AI 检测章节中的人物

        Args:
            content: 章节内容
            existing_characters: 已有人物列表（用于提示 AI）

        Returns:
            检测到的人物列表
        """
        if not self.ai_service or not self.ai_service.client:
            logger.error("AI 服务未初始化")
            return []

        # 构建已有人物名称列表
        existing_names = [char.name for char in existing_characters]
        existing_str = ", ".join(existing_names) if existing_names else "无"

        # 构建 prompt
        prompt = f"""请分析以下小说章节内容，提取出所有出现的人物。

对于每个人物，请提取以下信息：
- name: 姓名（必须）
- age: 年龄（数字）
- gender: 性别
- appearance: 外貌描述
- identity: 身份/职业
- hometown: 籍贯
- role: 角色类型（protagonist/antagonist/supporting/minor）
  注意：根据人物在故事中的作用判断类型，如果无法确定，默认使用 "supporting"
- personality: 性格特点（逗号分隔的标签）
- core_motivation: 核心动机
- fears: 恐惧的事物
- desires: 渴望的事物

章节内容：
{content}

参考已有的人物名称以避免重复（但请返回所有检测到的人物，系统会在服务端进行最终去重）：
{existing_str}

请以 JSON 格式返回，格式如下：
{{
  "characters": [
    {{
      "name": "张三",
      "age": 25,
      "gender": "男",
      "appearance": "身材高大，眉目清秀",
      "identity": "剑客",
      "role": "supporting"
    }}
  ]
}}

只返回 JSON，不要有其他内容。"""

        try:
            response = self.ai_service.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的小说人物分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            result_text = response.choices[0].message.content.strip()

            # 尝试解析 JSON
            import json
            # 移除可能的 markdown 代码块标记
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            result = json.loads(result_text)
            characters = result.get("characters", [])

            logger.info(f"AI 检测到 {len(characters)} 个人物")
            return characters

        except json.JSONDecodeError as e:
            logger.error(f"AI 返回的 JSON 解析失败: {e}, 原始内容: {result_text}")
            return []
        except Exception as e:
            logger.error(f"AI 检测人物失败: {e}")
            return []
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_detect_characters_calls_ai -v
```

预期: 测试通过

- [ ] **Step 5: 提交**

```bash
git add backend/app/services/entity_extraction_service.py tests/services/test_entity_extraction_service.py
git commit -m "feat: implement AI character detection"
```

---

## Task 7: 实现 AI 世界观设定检测方法

**目标:** 实现调用 AI 检测章节中世界观设定的逻辑

**文件:**
- Modify: `backend/app/services/entity_extraction_service.py`
- Test: `backend/tests/services/test_entity_extraction_service.py`

- [ ] **Step 1: 编写失败的测试**

在 `backend/tests/services/test_entity_extraction_service.py` 中添加:

```python
def test_detect_world_settings_calls_ai():
    """测试 AI 检测世界观设定调用"""
    mock_ai_service = Mock()
    mock_ai_service.client.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content='{"world_settings": [{"name": "青云剑派", "setting_type": "faction"}]}'))
    ]

    service = EntityExtractionService(ai_service=mock_ai_service)
    existing_settings = []

    result = service._detect_world_settings("章节内容", existing_settings)

    assert len(result) == 1
    assert result[0]["name"] == "青云剑派"
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_detect_world_settings_calls_ai -v
```

预期: `AttributeError: 'EntityExtractionService' object has no attribute '_detect_world_settings'`

- [ ] **Step 3: 实现 AI 检测方法**

在 `backend/app/services/entity_extraction_service.py` 中添加:

```python
    def _detect_world_settings(
        self,
        content: str,
        existing_settings: List[WorldSetting]
    ) -> List[Dict[str, Any]]:
        """
        使用 AI 检测章节中的世界观设定

        Args:
            content: 章节内容
            existing_settings: 已有设定列表（用于提示 AI）

        Returns:
            检测到的设定列表
        """
        if not self.ai_service or not self.ai_service.client:
            logger.error("AI 服务未初始化")
            return []

        # 构建已有设定名称列表
        existing_names = [setting.name for setting in existing_settings]
        existing_str = ", ".join(existing_names) if existing_names else "无"

        # 构建 prompt
        prompt = f"""请分析以下小说章节内容，提取出所有提到的世界观设定。

类型包括：
- era: 时代背景
- region: 地域/地点
- rule: 规则（魔法/科技体系）
- culture: 文化习俗
- power: 权力结构
- location: 具体地点
- faction: 势力/组织
- item: 重要物品
- event: 历史事件

对于每个设定，请提取：
- name: 名称（必须）
- setting_type: 类型（从上述类型中选择）
- description: 详细描述
- attributes: 扩展属性（JSON 对象）
- is_core_rule: 是否为核心规则（0或1）

章节内容：
{content}

参考已有的设定名称以避免重复（但请返回所有检测到的设定，系统会在服务端进行最终去重）：
{existing_str}

请以 JSON 格式返回，格式如下：
{{
  "world_settings": [
    {{
      "name": "青云剑派",
      "setting_type": "faction",
      "description": "江湖上著名的剑术门派",
      "attributes": {{"founding_year": "明朝", "location": "华山"}},
      "is_core_rule": 0
    }}
  ]
}}

只返回 JSON，不要有其他内容。"""

        try:
            response = self.ai_service.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的小说世界观分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            result_text = response.choices[0].message.content.strip()

            # 尝试解析 JSON
            import json
            # 移除可能的 markdown 代码块标记
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            result = json.loads(result_text)
            settings = result.get("world_settings", [])

            logger.info(f"AI 检测到 {len(settings)} 个世界观设定")
            return settings

        except json.JSONDecodeError as e:
            logger.error(f"AI 返回的 JSON 解析失败: {e}, 原始内容: {result_text}")
            return []
        except Exception as e:
            logger.error(f"AI 检测世界观设定失败: {e}")
            return []
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_detect_world_settings_calls_ai -v
```

预期: 测试通过

- [ ] **Step 5: 提交**

```bash
git add backend/app/services/entity_extraction_service.py tests/services/test_entity_extraction_service.py
git commit -m "feat: implement AI world setting detection"
```

---

## Task 8: 实现主提取方法

**目标:** 实现整合所有逻辑的主提取方法

**文件:**
- Modify: `backend/app/services/entity_extraction_service.py`
- Test: `backend/tests/services/test_entity_extraction_service.py`

- [ ] **Step 1: 编写失败的测试**

在 `backend/tests/services/test_entity_extraction_service.py` 中添加:

```python
def test_extract_characters_to_database():
    """测试提取人物并保存到数据库"""
    from app.core.database import SessionLocal
    from app.models.project import Project

    db = SessionLocal()
    # 创建测试项目
    project = Project(title="测试项目", user_id=1)
    db.add(project)
    db.commit()

    # Mock AI 服务
    mock_ai_service = Mock()
    mock_ai_service.client.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content='{"characters": [{"name": "张三", "age": 25, "role": "supporting"}]}'))
    ]

    service = EntityExtractionService(ai_service=mock_ai_service)

    result = service.extract_characters(
        db=db,
        project_id=project.id,
        content="章节内容"
    )

    assert result["added"] == 1
    assert result["skipped"] == 0

    # 验证数据库
    characters = db.query(Character).filter(Character.project_id == project.id).all()
    assert len(characters) == 1
    assert characters[0].name == "张三"

    # 清理
    db.delete(project)
    db.commit()
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_extract_characters_to_database -v
```

预期: `AttributeError: 'EntityExtractionService' object has no attribute 'extract_characters'`

- [ ] **Step 3: 实现主提取方法**

在 `backend/app/services/entity_extraction_service.py` 中添加:

```python
    def extract_characters(
        self,
        db: Session,
        project_id: int,
        content: str
    ) -> Dict[str, int]:
        """
        从章节内容中提取并创建人物

        Args:
            db: 数据库会话
            project_id: 项目 ID
            content: 章节内容

        Returns:
            {"added": 数量, "skipped": 数量}
        """
        if not content or not content.strip():
            logger.warning("章节内容为空，跳过人物提取")
            return {"added": 0, "skipped": 0}

        # 获取已有人物
        existing_characters = db.query(Character).filter(
            Character.project_id == project_id
        ).all()

        # AI 检测人物
        detected_characters = self._detect_characters(content, existing_characters)

        if not detected_characters:
            logger.info("AI 未检测到任何人物")
            return {"added": 0, "skipped": 0}

        # 去重
        unique_characters = self._deduplicate_characters(
            detected_characters,
            existing_characters
        )

        # 创建人物
        added_count = 0
        skipped_count = len(detected_characters) - len(unique_characters)

        for char_data in unique_characters:
            try:
                # 验证数据
                validated_char = ExtractedCharacter(**char_data)

                # 创建人物记录
                new_char = Character(
                    project_id=project_id,
                    **validated_char.model_dump(exclude_unset=True)
                )
                db.add(new_char)
                added_count += 1
                logger.info(f"创建人物: {validated_char.name}")

            except Exception as e:
                logger.error(f"创建人物失败: {e}, 数据: {char_data}")
                continue

        try:
            db.commit()
        except Exception as e:
            logger.error(f"提交数据库失败: {e}")
            db.rollback()
            return {"added": 0, "skipped": skipped_count}

        logger.info(f"人物提取完成: 添加 {added_count} 个，跳过 {skipped_count} 个")
        return {"added": added_count, "skipped": skipped_count}
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_extract_characters_to_database -v
```

预期: 测试通过

- [ ] **Step 5: 提交**

```bash
git add backend/app/services/entity_extraction_service.py tests/services/test_entity_extraction_service.py
git commit -m "feat: implement main character extraction method"
```

---

## Task 9: 实现世界观设定主提取方法

**目标:** 实现世界观设定的完整提取流程

**文件:**
- Modify: `backend/app/services/entity_extraction_service.py`
- Test: `backend/tests/services/test_entity_extraction_service.py`

- [ ] **Step 1: 编写失败的测试**

在 `backend/tests/services/test_entity_extraction_service.py` 中添加:

```python
def test_extract_world_settings_to_database():
    """测试提取世界观设定并保存到数据库"""
    from app.core.database import SessionLocal
    from app.models.project import Project

    db = SessionLocal()
    project = Project(title="测试项目", user_id=1)
    db.add(project)
    db.commit()

    mock_ai_service = Mock()
    mock_ai_service.client.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content='{"world_settings": [{"name": "青云剑派", "setting_type": "faction"}]}'))
    ]

    service = EntityExtractionService(ai_service=mock_ai_service)

    result = service.extract_world_settings(
        db=db,
        project_id=project.id,
        content="章节内容"
    )

    assert result["added"] == 1
    assert result["skipped"] == 0

    settings = db.query(WorldSetting).filter(WorldSetting.project_id == project.id).all()
    assert len(settings) == 1
    assert settings[0].name == "青云剑派"

    db.delete(project)
    db.commit()
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_extract_world_settings_to_database -v
```

预期: `AttributeError: 'EntityExtractionService' object has no attribute 'extract_world_settings'`

- [ ] **Step 3: 实现主提取方法**

在 `backend/app/services/entity_extraction_service.py` 中添加:

```python
    def extract_world_settings(
        self,
        db: Session,
        project_id: int,
        content: str
    ) -> Dict[str, int]:
        """
        从章节内容中提取并创建世界观设定

        Args:
            db: 数据库会话
            project_id: 项目 ID
            content: 章节内容

        Returns:
            {"added": 数量, "skipped": 数量}
        """
        if not content or not content.strip():
            logger.warning("章节内容为空，跳过世界观设定提取")
            return {"added": 0, "skipped": 0}

        # 获取已有设定
        existing_settings = db.query(WorldSetting).filter(
            WorldSetting.project_id == project_id
        ).all()

        # AI 检测设定
        detected_settings = self._detect_world_settings(content, existing_settings)

        if not detected_settings:
            logger.info("AI 未检测到任何世界观设定")
            return {"added": 0, "skipped": 0}

        # 去重
        unique_settings = self._deduplicate_world_settings(
            detected_settings,
            existing_settings
        )

        # 创建设定
        added_count = 0
        skipped_count = len(detected_settings) - len(unique_settings)

        for setting_data in unique_settings:
            try:
                # 验证数据
                validated_setting = ExtractedWorldSetting(**setting_data)

                # 创建设定记录
                new_setting = WorldSetting(
                    project_id=project_id,
                    **validated_setting.model_dump(exclude_unset=True)
                )
                db.add(new_setting)
                added_count += 1
                logger.info(f"创建世界观设定: {validated_setting.name}")

            except Exception as e:
                logger.error(f"创建世界观设定失败: {e}, 数据: {setting_data}")
                continue

        try:
            db.commit()
        except Exception as e:
            logger.error(f"提交数据库失败: {e}")
            db.rollback()
            return {"added": 0, "skipped": skipped_count}

        logger.info(f"世界观设定提取完成: 添加 {added_count} 个，跳过 {skipped_count} 个")
        return {"added": added_count, "skipped": skipped_count}
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd backend
pytest tests/services/test_entity_extraction_service.py::test_extract_world_settings_to_database -v
```

预期: 测试通过

- [ ] **Step 5: 提交**

```bash
git add backend/app/services/entity_extraction_service.py tests/services/test_entity_extraction_service.py
git commit -m "feat: implement main world setting extraction method"
```

---

## Task 10: 创建全局服务实例

**目标:** 在 AIService 模块中创建全局 EntityExtractionService 实例

**文件:**
- Modify: `backend/app/services/entity_extraction_service.py`
- Modify: `backend/app/api/chapters.py`

- [ ] **Step 1: 添加全局实例**

在 `backend/app/services/entity_extraction_service.py` 末尾添加:

```python
# 创建全局服务实例
entity_extraction_service = EntityExtractionService(ai_service=None)
```

在 `backend/app/api/chapters.py` 的导入部分添加:

```python
from app.services.entity_extraction_service import entity_extraction_service
```

- [ ] **Step 2: 验证导入**

运行测试:

```bash
cd backend
python -c "from app.services.entity_extraction_service import entity_extraction_service; print(entity_extraction_service)"
```

预期: 成功打印服务实例

- [ ] **Step 3: 提交**

```bash
git add backend/app/services/entity_extraction_service.py backend/app/api/chapters.py
git commit -m "feat: create global entity extraction service instance"
```

---

## Task 11: 添加 API 端点

**目标:** 在章节 API 中添加实体提取端点

**文件:**
- Modify: `backend/app/api/chapters.py`
- Test: `backend/tests/api/test_chapters_extraction.py`

- [ ] **Step 1: 编写失败的测试**

创建 `backend/tests/api/test_chapters_extraction.py`:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.project import Project
from app.models.chapter import Chapter
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_extract_entities_endpoint(db_session):
    """测试实体提取端点"""
    # 创建测试用户
    user = User(email="test@example.com", username="testuser", hashed_password="hash")
    db_session.add(user)
    db_session.commit()

    # 创建测试项目
    project = Project(title="测试项目", user_id=user.id)
    db_session.add(project)
    db_session.commit()

    # 创建测试章节
    chapter = Chapter(
        project_id=project.id,
        chapter_number=1,
        title="第一章",
        content="张三走进了青云剑派的大门。"
    )
    db_session.add(chapter)
    db_session.commit()

    # Mock AI 服务（需要注入）
    # 这里需要登录 token，简化起见跳过真实调用测试

    # 实际测试需要完整的认证流程
    # response = client.post(f"/api/chapters/{chapter.id}/extract-entities")
    # assert response.status_code == 200
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd backend
pytest tests/api/test_chapters_extraction.py::test_extract_entities_endpoint -v
```

预期: 测试通过（端点不存在时会有 404）

- [ ] **Step 3: 实现 API 端点**

在 `backend/app/api/chapters.py` 中添加端点:

```python
@router.post("/{chapter_id}/extract-entities", summary="从章节提取实体")
def extract_entities_from_chapter(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从章节内容中提取人物和世界观设定

    返回统计信息：
    - characters: {"added": 数量, "skipped": 数量}
    - world_settings: {"added": 数量, "skipped": 数量}
    """
    # 获取章节
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException("章节不存在")

    # 验证项目权限
    project = require_project(chapter.project_id, current_user, db)

    # 检查章节内容
    if not chapter.content or not chapter.content.strip():
        raise BusinessException("章节内容为空，无法提取实体")

    try:
        # 注入 AI 服务
        from app.services.ai_service import ai_service
        entity_extraction_service.ai_service = ai_service

        # 提取人物
        characters_result = entity_extraction_service.extract_characters(
            db=db,
            project_id=project.id,
            content=chapter.content
        )

        # 提取世界观设定
        settings_result = entity_extraction_service.extract_world_settings(
            db=db,
            project_id=project.id,
            content=chapter.content
        )

        # 构建响应
        message_parts = []
        if characters_result["added"] > 0:
            message_parts.append(f"{characters_result['added']} 个人物")
        if settings_result["added"] > 0:
            message_parts.append(f"{settings_result['added']} 个世界观设定")

        message_text = "、".join(message_parts) if message_parts else "未发现新实体"
        if not message_text.startswith("未"):
            message_text = f"成功添加 {message_text}"

        return {
            "code": 200,
            "message": message_text,
            "data": {
                "characters": characters_result,
                "world_settings": settings_result
            }
        }

    except Exception as e:
        logger.error(f"提取实体失败: {e}")
        raise BusinessException(f"提取实体失败: {str(e)}")
```

- [ ] **Step 4: 验证端点存在**

```bash
cd backend
python -c "from app.api.chapters import router; print([r.path for r in router.routes if 'extract' in r.path])"
```

预期: 包含 `/{chapter_id}/extract-entities`

- [ ] **Step 5: 提交**

```bash
git add backend/app/api/chapters.py tests/api/test_chapters_extraction.py
git commit -m "feat: add entity extraction API endpoint"
```

---

## Task 12: 添加前端 API 调用方法

**目标:** 在前端 API 服务中添加调用方法

**文件:**
- Modify: `frontend/src/services/api.ts`

- [ ] **Step 1: 添加 API 方法**

在 `frontend/src/services/api.ts` 中添加:

```typescript
/**
 * 从章节提取实体
 * @param chapterId 章节 ID
 * @returns 提取结果
 */
export const extractEntitiesFromChapter = async (chapterId: number) => {
  const response = await api.post(`/chapters/${chapterId}/extract-entities`);
  return response.data;
};
```

- [ ] **Step 2: 验证 TypeScript 类型检查**

```bash
cd frontend
npm run type-check
```

预期: 无类型错误

- [ ] **Step 3: 提交**

```bash
git add frontend/src/services/api.ts
git commit -m "feat: add extractEntitiesFromChapter API method"
```

---

## Task 13: 添加前端"提取实体"按钮

**目标:** 在章节详情页添加提取实体按钮和事件处理

**文件:**
- Modify: `frontend/src/pages/ProjectDetail.tsx`

- [ ] **Step 1: 添加状态**

在 `ProjectDetail.tsx` 的状态声明部分添加:

```typescript
const [extracting, setExtracting] = useState<Record<number, boolean>>({});
```

- [ ] **Step 2: 添加事件处理函数**

在 `ProjectDetail.tsx` 中添加函数:

```typescript
const handleExtractEntities = async (chapterId: number) => {
  setExtracting({ ...extracting, [chapterId]: true });

  try {
    const result = await extractEntitiesFromChapter(chapterId);

    const addedChars = result.data.characters.added;
    const addedSettings = result.data.world_settings.added;

    if (addedChars > 0 || addedSettings > 0) {
      message.success(
        `成功添加 ${addedChars} 个人物，${addedSettings} 个世界观设定`
      );
    } else {
      message.info('未发现新的人物或世界观设定');
    }

    // 刷新人物和世界观列表
    await Promise.all([
      fetchCharacters(project?.id),
      fetchWorldSettings(project?.id)
    ]);

  } catch (error: any) {
    console.error('提取实体失败:', error);
    message.error(error.response?.data?.message || '提取实体失败，请稍后重试');
  } finally {
    setExtracting({ ...extracting, [chapterId]: false });
  }
};
```

- [ ] **Step 3: 添加按钮**

在章节操作按钮区域添加按钮（找到其他章节按钮附近添加）:

```tsx
<Button
  type="default"
  icon={<ScanOutlined />}
  onClick={() => handleExtractEntities(chapter.id)}
  loading={extracting[chapter.id]}
  disabled={!chapter.content}
>
  提取实体
</Button>
```

- [ ] **Step 4: 添加图标导入**

在文件顶部添加:

```typescript
import { ScanOutlined } from '@ant-design/icons';
```

- [ ] **Step 5: 验证 TypeScript 编译**

```bash
cd frontend
npm run type-check
```

预期: 无类型错误

- [ ] **Step 6: 提交**

```bash
git add frontend/src/pages/ProjectDetail.tsx
git commit -m "feat: add extract entities button and handler"
```

---

## Task 14: 端到端测试

**目标:** 手动测试完整流程

**文件:**
- Manual testing

- [ ] **Step 1: 启动后端服务**

```bash
cd backend
python main.py
```

验证: 后端在 http://localhost:8000 运行

- [ ] **Step 2: 启动前端服务**

```bash
cd frontend
npm run dev
```

验证: 前端在 http://localhost:5173 运行

- [ ] **Step 3: 登录系统**

打开 http://localhost:5173，使用测试账号登录：
- Email: `test@example.com`
- Password: `password123`

- [ ] **Step 4: 创建测试项目**

1. 创建新项目
2. 添加第一章，内容包含人物和世界观描述，例如：
   ```
   张三走进了青云剑派的大门。这个成立于明朝的剑术门派坐落在华山上，
   门派中有着严格的等级制度。作为门派的长老，李四正在等待着他。
   ```

- [ ] **Step 5: 测试提取功能**

1. 点击章节的"提取实体"按钮
2. 等待处理完成（5-15秒）
3. 查看成功消息
4. 检查人物列表，应该包含"张三"、"李四"
5. 检查世界观设定列表，应该包含"青云剑派"

- [ ] **Step 6: 测试去重功能**

1. 再次点击"提取实体"按钮
2. 应该提示"未发现新的人物或世界观设定"

- [ ] **Step 7: 测试空内容**

1. 创建一个没有内容的章节
2. 点击"提取实体"按钮
3. 应该提示"章节内容为空"

- [ ] **Step 8: 记录测试结果**

记录测试中发现的问题：

```
[测试结果记录]
- 功能正常: [是/否]
- 发现的问题:
  1.
  2.
- 性能: 处理时间约 ___ 秒
```

- [ ] **Step 9: 提交文档更新**

如果有文档需要更新：

```bash
# 如果有 API 文档或其他文档需要更新
git add docs/
git commit -m "docs: update API documentation for entity extraction"
```

---

## Task 15: 代码审查和优化

**目标:** 审查代码，优化性能和错误处理

**文件:**
- Review all modified files

- [ ] **Step 1: 检查日志记录**

确保所有关键操作都有日志记录：
- AI 调用
- 数据库操作
- 错误处理

- [ ] **Step 2: 检查错误处理**

确保所有异常都被正确捕获和处理：
- JSON 解析错误
- 数据库错误
- AI 调用错误

- [ ] **Step 3: 性能优化**

检查是否需要优化：
- [ ] 批量插入优化（如果检测到大量实体）
- [ ] 缓存已有实体列表（避免重复查询）
- [ ] AI prompt 优化（减少 token 消耗）

- [ ] **Step 4: 代码格式化**

```bash
cd backend
black app/
isort app/

cd frontend
npm run lint
```

- [ ] **Step 5: 最终测试**

```bash
cd backend
pytest tests/ -v

cd frontend
npm run type-check
npm run build
```

- [ ] **Step 6: 提交优化**

```bash
git add .
git commit -m "refactor: optimize entity extraction code"
```

---

## Task 16: 更新文档

**目标:** 更新项目文档以反映新功能

**文件:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 更新 API 端点文档**

在 `CLAUDE.md` 的"Chapters"部分添加:

```markdown
### Chapters
- ...
- `POST /api/chapters/{id}/extract-entities` - 从章节内容中提取人物和世界观设定
  - 返回统计信息：添加和跳过的实体数量
```

- [ ] **Step 2: 更新功能概述**

在项目概述部分添加:

```markdown
## AI 实体提取

系统支持从章节内容中自动提取人物和世界观设定：
- 点击"提取实体"按钮触发 AI 分析
- 自动识别并创建新实体
- 通过名称相似度匹配避免重复
- 可配置的相似度阈值（默认 0.7）
```

- [ ] **Step 3: 提交文档更新**

```bash
git add CLAUDE.md
git commit -m "docs: update documentation for entity extraction feature"
```

---

## 验收检查清单

完成后验证以下所有项目：

- [ ] 点击"提取实体"按钮能成功触发分析
- [ ] 正确识别章节中的人物（姓名、年龄、性别等）
- [ ] 正确识别世界观设定（名称、类型、描述等）
- [ ] 名称相似度匹配正确工作（避免重复）
- [ ] 前端显示准确的统计信息（添加数量、跳过数量）
- [ ] 创建的实体数据完整（所有字段正确填充）
- [ ] 错误情况有友好提示（空内容、AI 失败等）
- [ ] 性能可接受（单次分析 < 20 秒）
- [ ] 所有单元测试通过
- [ ] 前端 TypeScript 类型检查通过
- [ ] 代码已格式化
- [ ] 文档已更新

---

## 实施说明

**开发环境要求:**
- Python 3.10+
- Node.js 18+
- PostgreSQL 15
- ZhipuAI API Key

**测试数据准备:**
建议准备包含以下内容的测试章节：
- 3-5 个人物（主角、配角、反派）
- 2-3 个世界观设定（门派、地点、物品）
- 部分与已有实体相似的名称（测试去重）

**故障排查:**
- AI 调用失败：检查 API Key 和网络连接
- 数据库错误：检查数据库连接和表结构
- 前端报错：检查 TypeScript 类型和 API 调用
