# AI 实体提取功能设计文档

**创建日期**: 2026-03-29
**作者**: Claude
**状态**: 设计阶段

## 1. 功能概述

为小说 AI 系统添加自动实体提取功能，用户可以点击按钮分析章节内容，AI 自动识别并创建新的人物和世界观设定。

### 1.1 核心需求

- 用户主动触发分析（非自动）
- 同时检测人物和世界观设定
- 自动创建所有检测到的实体
- 通过名称相似度匹配避免重复
- 提取完整信息（所有字段）

### 1.2 用户场景

1. 用户在章节详情页点击"提取实体"按钮
2. 系统调用 AI 分析章节内容
3. AI 返回检测到的人物和世界观设定
4. 系统自动去重（名称相似度匹配）
5. 自动创建新实体到数据库
6. 显示成功提示，告知用户添加了多少个实体

## 2. 系统架构

```
Frontend (章节详情页)
    ↓ [点击按钮]
API Endpoint: POST /api/chapters/{id}/extract-entities
    ↓
EntityExtractionService (新增)
    ├── extract_entities() - 主入口
    ├── _detect_characters() - 检测人物
    ├── _detect_world_settings() - 检测世界观
    ├── _deduplicate_characters() - 人物去重
    └── _deduplicate_world_settings() - 世界观去重
    ↓
AIService (复用)
    └── 调用 AI 模型进行实体识别
    ↓
Database
    ├── Characters 表
    └── WorldSettings 表
```

## 3. 后端实现

### 3.1 新增服务: EntityExtractionService

**文件位置**: `backend/app/services/entity_extraction_service.py`

**主要方法**:

```python
class EntityExtractionService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    def extract_entities(
        self,
        chapter_id: int,
        project_id: int,
        chapter_content: str
    ) -> Dict[str, Any]:
        """
        从章节内容中提取实体

        Returns:
            {
                "characters": {"added": 5, "skipped": 2},
                "world_settings": {"added": 3, "skipped": 1}
            }
        """

    def _detect_characters(
        self,
        content: str,
        existing_characters: List[Character]
    ) -> List[Dict]:
        """使用 AI 检测人物"""

    def _detect_world_settings(
        self,
        content: str,
        existing_settings: List[WorldSetting]
    ) -> List[Dict]:
        """使用 AI 检测世界观设定"""

    def _deduplicate_characters(
        self,
        detected: List[Dict],
        existing: List[Character]
    ) -> List[Dict]:
        """通过名称相似度去重"""

    def _deduplicate_world_settings(
        self,
        detected: List[Dict],
        existing: List[WorldSetting]
    ) -> List[Dict]:
        """通过名称相似度去重"""
```

### 3.2 AI Prompt 设计

#### 人物提取 Prompt

```
请分析以下小说章节内容，提取出所有出现的人物。

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
{chapter_content}

参考已有的人物名称以避免重复（但请返回所有检测到的人物，系统会在服务端进行最终去重）：
{existing_characters}

请以 JSON 格式返回，格式如下：
{
  "characters": [
    {
      "name": "张三",
      "age": 25,
      "gender": "男",
      "appearance": "身材高大，眉目清秀",
      "identity": "剑客",
      "role": "supporting",
      ...
    }
  ]
}
```

#### 世界观设定提取 Prompt

```
请分析以下小说章节内容，提取出所有提到的世界观设定。

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
{chapter_content}

参考已有的设定名称以避免重复（但请返回所有检测到的设定，系统会在服务端进行最终去重）：
{existing_settings}

请以 JSON 格式返回，格式如下：
{
  "world_settings": [
    {
      "name": "青云剑派",
      "setting_type": "faction",
      "description": "江湖上著名的剑术门派",
      "attributes": {"founding_year": "明朝", "location": "华山"},
      "is_core_rule": 0
    }
  ]
}
```

### 3.3 名称相似度匹配算法

使用 **编辑距离（Levenshtein Distance）** + **相似度阈值**：

```python
def _is_similar_name(name1: str, name2: str, threshold: float = 0.7) -> bool:
    """
    判断两个名称是否相似

    Args:
        name1: 第一个名称
        name2: 第二个名称
        threshold: 相似度阈值（0-1），默认 0.7，可通过配置调整

    Returns:
        True if similar enough to be considered duplicate
    """
    from difflib import SequenceMatcher

    similarity = SequenceMatcher(None, name1, name2).ratio()
    return similarity >= threshold
```

**配置说明**: 相似度阈值默认为 0.7，可根据实际使用情况在后端配置文件中调整。

**匹配规则**:
- 相似度 >= threshold: 视为重复，跳过
- 相似度 < threshold: 视为新实体，创建

**示例**:
- "张三" vs "张小三" → 相似度 0.67 → 创建
- "李明" vs "李鸣" → 相似度 0.67 → 创建
- "王大" vs "王大人" → 相似度 0.67 → 创建
- "剑派" vs "剑派" → 相似度 1.0 → 跳过

### 3.4 API 端点

**文件位置**: `backend/app/api/chapters.py`

```python
@router.post("/{chapter_id}/extract-entities")
def extract_entities_from_chapter(
    chapter_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    从章节内容中提取人物和世界观设定

    Returns:
        {
            "code": 200,
            "message": "成功添加 5 个人物，3 个世界观设定",
            "data": {
                "characters": {"added": 5, "skipped": 2},
                "world_settings": {"added": 3, "skipped": 1}
            }
        }
    """
```

### 3.5 数据验证

使用 Pydantic 验证 AI 返回的数据：

**文件位置**: `backend/app/schemas/entity_extraction.py`

```python
class ExtractedCharacter(BaseModel):
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
    name: str
    setting_type: SettingType
    description: Optional[str] = None
    attributes: Optional[Dict] = None
    is_core_rule: int = 0

class EntityExtractionResponse(BaseModel):
    characters: Dict[str, int]  # {"added": 5, "skipped": 2}
    world_settings: Dict[str, int]
```

## 4. 前端实现

### 4.1 按钮位置

**文件位置**: `frontend/src/pages/ProjectDetail.tsx`

在章节操作按钮区域添加：

```tsx
<Button
  type="primary"
  icon={<ScanOutlined />}
  onClick={() => handleExtractEntities(chapter.id)}
  loading={extracting[chapter.id]}
>
  提取实体
</Button>
```

### 4.2 API 调用

**文件位置**: `frontend/src/services/api.ts`

```typescript
/**
 * 从章节提取实体
 */
export const extractEntitiesFromChapter = async (chapterId: number) => {
  const response = await api.post(`/chapters/${chapterId}/extract-entities`);
  return response.data;
};
```

### 4.3 事件处理

```typescript
const [extracting, setExtracting] = useState<Record<number, boolean>>({});

const handleExtractEntities = async (chapterId: number) => {
  setExtracting({ ...extracting, [chapterId]: true });

  try {
    const result = await extractEntitiesFromChapter(chapterId);

    message.success(
      `成功添加 ${result.data.characters.added} 个人物，` +
      `${result.data.world_settings.added} 个世界观设定`
    );

    // 刷新人物和世界观列表
    await Promise.all([
      fetchCharacters(projectId),
      fetchWorldSettings(projectId)
    ]);

  } catch (error) {
    message.error('提取实体失败');
  } finally {
    setExtracting({ ...extracting, [chapterId]: false });
  }
};
```

### 4.4 UI 反馈

使用 Ant Design 的 `message` 组件显示结果：

- **成功**: "成功添加 5 个人物，3 个世界观设定"
- **无新实体**: "未发现新的人物或世界观设定"
- **错误**: "提取实体失败，请稍后重试"

## 5. 数据流

### 5.1 完整流程图

```
用户点击"提取实体"
    ↓
前端发送 POST /api/chapters/{id}/extract-entities
    ↓
后端验证章节权限
    ↓
EntityExtractionService.extract_entities()
    ↓
获取章节内容、已有的人物和世界观
    ↓
_detect_characters() → AI 调用 → 返回人物列表
    ↓
_deduplicate_characters() → 名称相似度匹配
    ↓
创建新人物到数据库
    ↓
_detect_world_settings() → AI 调用 → 返回世界观列表
    ↓
_deduplicate_world_settings() → 名称相似度匹配
    ↓
创建新世界观到数据库
    ↓
返回统计结果
    ↓
前端显示成功消息
    ↓
刷新人物和世界观列表
```

### 5.2 错误处理

| 场景 | 处理方式 |
|------|---------|
| 章节内容为空 | 返回错误："章节内容为空" |
| AI 调用失败 | 返回错误："AI 分析失败" |
| AI 返回无效 JSON | 记录日志，返回部分结果 |
| 数据库创建失败 | 记录日志，回滚已创建的实体 |
| 名称相似度计算异常 | 跳过该实体，继续处理 |

## 6. 技术细节

### 6.1 AI 模型选择

- **默认**: `glm-4-flash`（快速、经济）
- **备选**: `glm-4-plus`（复杂场景，更高准确率）

### 6.2 性能考虑

- **单次分析耗时**: 预计 5-15 秒
- **Token 消耗**:
  - 输入: ~2000 tokens（章节内容 + 上下文）
  - 输出: ~500-1000 tokens（实体列表）
- **并发处理**: 暂不支持（按钮点击后禁用，显示 loading）

### 6.3 数据库影响

- **Characters 表**: 可能新增多条记录
- **WorldSettings 表**: 可能新增多条记录
- **事务处理**: 使用数据库事务，失败时回滚

## 7. 测试计划

### 7.1 单元测试

- `EntityExtractionService` 的各个方法
- 名称相似度匹配算法
- 数据验证 Pydantic 模型

### 7.2 集成测试

- 完整的实体提取流程
- 去重逻辑验证
- API 端点响应

### 7.3 手动测试场景

1. **空章节**: 应返回错误
2. **纯描写章节**: 可能无新实体
3. **对话密集章节**: 应检测到多个人物
4. **已有实体**: 应正确去重
5. **名称相似实体**: 应正确判断是否重复

## 8. 未来扩展

### 8.1 可能的改进

- **批量分析**: 支持一次分析多个章节
- **增量分析**: 只分析新增的内容
- **实体关系**: 检测人物之间的关系
- **智能合并**: 检测到相似实体时，提示用户合并而非跳过
- **置信度评分**: AI 为每个检测到的实体提供置信度，用户可筛选

### 8.2 性能优化

- **缓存**: 缓存已有实体列表，避免重复查询
- **异步处理**: 使用后台任务处理大量章节
- **批量创建**: 优化数据库批量插入

## 9. 依赖项

### 9.1 Python 依赖

无需新增依赖，使用现有：
- `fastapi`: API 框架
- `sqlalchemy`: ORM
- `pydantic`: 数据验证
- `openai`: AI 客户端
- `python-Levenshtein` (可选): 更快的编辑距离计算

### 9.2 前端依赖

无需新增依赖，使用现有：
- `react`: UI 框架
- `antd`: UI 组件库
- `axios`: HTTP 客户端

## 10. 实施步骤

1. 创建 `EntityExtractionService` 类
2. 实现 AI 调用和 Prompt 设计
3. 实现名称相似度匹配算法
4. 添加 API 端点
5. 添加前端按钮和事件处理
6. 编写单元测试
7. 手动测试验证
8. 更新文档

## 11. 风险与限制

### 11.1 风险

- **AI 准确率**: 可能误识别或遗漏实体
- **名称冲突**: 相似度阈值可能不适合所有场景
- **性能问题**: 大章节可能导致 AI 超时

### 11.2 限制

- 仅支持中文小说（AI 模型限制）
- 一次性分析整章，不支持分段
- 不支持实时编辑时分析

## 12. 验收标准

本功能需要满足以下验收标准：

1. 点击按钮后能成功提取实体
2. 正确去重已存在的实体
3. 前端显示准确的统计信息
4. 创建的实体数据完整
5. 错误情况有友好提示
6. 性能可接受（< 20 秒）
