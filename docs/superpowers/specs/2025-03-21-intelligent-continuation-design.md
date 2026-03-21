# 智能续写功能设计文档

**项目**: Novel AI System (小说AI生成与管理系统)
**文档版本**: v1.1
**创建日期**: 2025-03-21
**最后更新**: 2025-03-21
**作者**: Claude
**状态**: 设计阶段（已根据审查意见更新）

---

## 一、文档概述

### 1.1 背景与目标

当前系统的AI生成功能存在以下限制：
- 无法基于前文内容续写章节
- 人物和世界观数据未传递给AI
- 只能生成单一版本，无法对比选择
- 无法直接生成第一章，必须先创建空白章节

**本设计的目标**：
1. 实现基于前文内容的智能续写功能
2. 支持直接生成第一章
3. 提供多版本生成供用户选择
4. 实现关键信息自动提取到设定库

### 1.2 实施策略

采用**渐进式增强**方案，分两个阶段实施：

**第一阶段**（核心续写）：
- 基于前文的智能续写
- 支持简单/标准/高级三种模式
- 生成2-3个版本供选择
- 手动提取关键信息

**第二阶段**（智能提取）：
- AI自动识别新实体
- 弹窗确认机制
- 保留手动提取功能

---

## 二、功能需求

### 2.1 核心功能

#### 2.1.1 首章生成模式

**场景**：用户从零开始创作小说的第一章

**功能**：
- 无前文内容，基于项目设定生成
- 支持设置开篇场景、核心要素、基调
- 可选择登场人物、相关世界观设定
- 生成2-3个版本供选择

**参数**：
```json
{
  "mode": "simple|standard|advanced",
  "project_id": 1,
  "chapter_number": 1,
  "first_chapter_mode": {
    "opening_scene": "开篇场景描述",
    "key_elements": ["主角登场", "世界观展示", "冲突暗示"],
    "tone": "悬疑"
  },
  "featured_characters": [1, 3],
  "word_count": 2000,
  "versions": 3
}
```

#### 2.1.2 续写模式

**场景**：基于上一章结尾继续创作

**功能**：
- 自动获取前文内容（最后800字）
- 支持选择衔接方式（紧接上文/三天后/换个场景）
- 指定情节方向、冲突点
- 可选出场人物、世界观设定
- 生成2-3个版本供选择

**参数**：
```json
{
  "mode": "simple|standard|advanced",
  "project_id": 1,
  "chapter_number": 2,
  "continue_mode": {
    "previous_chapter_id": 1,
    "transition": "紧接上文",
    "plot_direction": "本章情节方向",
    "conflict_point": "核心冲突"
  },
  "featured_characters": [1, 3],
  "word_count": 2000,
  "versions": 3
}
```

### 2.2 三种控制模式

#### 2.2.1 简单模式（Simple）

**适用场景**：快速生成，不关心细节

**参数**：
- 前文内容（自动获取）
- 续写字数
- 情节方向（简短描述）

**AI上下文**：
- 项目基础信息
- 前文提要（800字）

#### 2.2.2 标准模式（Standard）

**适用场景**：常规创作，需要一定控制

**额外参数**：
- 本章出场人物（从现有人物中选择）
- 相关世界观设定
- 冲突点描述
- 风格强度（0-100）

**AI上下文**：
- 简单模式全部内容
- 出场人物的详细设定
- 相关世界观规则
- 风格要求

#### 2.2.3 高级模式（Advanced）

**适用场景**：精细控制，专业创作

**额外参数**：
- 关联情节节点（PlotNode）
- 人物弧光进展
- 叙事视角（POV人物）
- AI创造性参数（temperature）

**AI上下文**：
- 标准模式全部内容
- 情节节点详情
- POV视角限制
- 人物弧光变化

---

## 二点五、非功能需求

### 2.5.1 成本控制

**问题**：多版本生成会导致API调用成本倍增（3版本 = 3倍成本）

**解决方案**：

#### 2.5.1.1 生成配额限制

**数据库扩展**：

```sql
-- 在 projects 表增加字段
ALTER TABLE projects ADD COLUMN daily_generation_limit INTEGER DEFAULT 10;
ALTER TABLE projects ADD COLUMN monthly_api_budget DECIMAL(10,2) DEFAULT 100.0;

-- 记录每日生成次数
CREATE TABLE generation_usage_logs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    generation_date DATE NOT NULL,
    versions_generated INTEGER DEFAULT 0,  -- 生成的版本总数
    estimated_cost DECIMAL(10,4) DEFAULT 0.0,  -- 预估成本（元）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(project_id, generation_date)
);
```

**配额检查逻辑**：

```python
def check_generation_quota(project_id: int, versions: int) -> tuple[bool, str]:
    """检查生成配额

    Returns:
        (allowed: bool, message: str)
    """
    # 1. 检查每日限额
    today_usage = db.query(GenerationUsageLog).filter(
        GenerationUsageLog.project_id == project_id,
        GenerationUsageLog.generation_date == date.today()
    ).first()

    if today_usage and today_usage.versions_generated >= today_usage.project.daily_generation_limit:
        return False, f"今日生成次数已达上限（{today_usage.project.daily_generation_limit}次）"

    # 2. 检查月度预算
    monthly_cost = db.query(func.sum(GenerationUsageLog.estimated_cost)).filter(
        GenerationUsageLog.project_id == project_id,
        extract('year', GenerationUsageLog.generation_date) == date.today().year,
        extract('month', GenerationUsageLog.generation_date) == date.today().month
    ).scalar() or 0

    estimated_cost = versions * 0.001  # 假设每版本成本0.001元

    if monthly_cost + estimated_cost > get_project(project_id).monthly_api_budget:
        return False, f"月度API预算不足（剩余：{monthly_cost:.2f}元）"

    return True, ""
```

#### 2.5.1.2 成本预估与提示

**前端显示**：

```
┌─ 生成设置 ──────────────────────────────────────────┐
│  生成版本：[3] 个                                    │
│  预估成本：¥0.003  （今日剩余：7次，本月预算：¥95.2）│
│  ⚠️ 提示：多版本生成会增加成本，请合理使用           │
└───────────────────────────────────────────────────────┘
```

**API响应增加成本信息**：

```json
{
  "code": 200,
  "data": {
    "versions": [...],
    "cost_info": {
      "estimated_cost": 0.003,
      "remaining_quota": 7,
      "monthly_budget_remaining": 95.2
    }
  }
}
```

### 2.5.2 安全与权限设计

#### 2.5.2.1 API认证

**JWT认证要求**：

所有续写相关接口必须验证JWT token：

```python
from app.core.auth import get_current_user

@router.post("/api/chapters/generate")
def generate_chapter(
    request_data: ChapterGenerateRequest,
    current_user: User = Depends(get_current_user),  # JWT认证
    db: Session = Depends(get_db)
):
    # 验证用户是否有权限访问该项目
    project = db.query(Project).filter(
        Project.id == request_data.project_id,
        Project.user_id == current_user.id  # 仅创建者可访问
    ).first()

    if not project:
        raise NotFoundException("项目不存在或无权访问")

    # ... 生成逻辑
```

#### 2.5.2.2 API速率限制

**防止恶意请求导致成本激增**：

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/chapters/generate")
@limiter.limit("10/minute")  # 每分钟最多10次请求
def generate_chapter(...):
    # ... 生成逻辑
```

#### 2.5.2.3 草稿数据隔离

**草稿仅创建者可见**：

```python
# 查询草稿时验证权限
def get_drafts(chapter_id: int, current_user: User, db: Session):
    chapter = db.query(Chapter).join(Project).filter(
        Chapter.id == chapter_id,
        Project.user_id == current_user.id  # 验证权限
    ).first()

    if not chapter:
        raise NotFoundException("无权访问")

    return db.query(ContentGenerationDraft).filter(
        ContentGenerationDraft.chapter_id == chapter_id
    ).all()
```

### 2.5.3 数据清理策略

**问题**：`content_generation_drafts` 表会无限增长

**解决方案**：自动清理过期草稿

```python
# 定时任务（使用 APScheduler）
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=2, minute=0)  # 每天凌晨2点
def clean_old_drafts():
    """删除7天前未选中的草稿"""
    cutoff_date = datetime.now() - timedelta(days=7)

    deleted_count = db.query(ContentGenerationDraft).filter(
        ContentGenerationDraft.created_at < cutoff_date,
        ContentGenerationDraft.is_selected == False
    ).delete()

    db.commit()
    logger.info(f"清理了 {deleted_count} 条过期草稿")

scheduler.start()
```

**优化**：提供手动清理按钮

```
┌─ 草稿管理 ──────────────────────────────────────────┐
│  历史草稿：15条  （占用空间：2.3MB）                  │
│  [🗑️ 清理7天前的草稿]  [📊 查看详情]                │
└───────────────────────────────────────────────────────┘
```

---

## 三、架构设计

### 3.1 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (React)                         │
├─────────────────────────────────────────────────────────┤
│  章节编辑页                                               │
│  ├── 续写控制面板（模式选择）                            │
│  ├── 版本选择器（2-3个生成版本）                         │
│  └── 关键信息提取工具（第二阶段）                        │
└──────────────────────┬──────────────────────────────────┘
                       │ API调用
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  后端 (FastAPI)                          │
├─────────────────────────────────────────────────────────┤
│  /api/chapters/generate (统一生成接口)                  │
│  ├── POST /api/chapters/generate                        │
│  ├── POST /api/chapters/{id}/select-version             │
│  └── POST /api/chapters/{id}/extract-entities (第二阶段)│
│                                                           │
│  AI服务层 (ai_service.py)                                │
│  ├── build_generation_context() - 上下文构建            │
│  ├── generate_versions() - 多版本生成                   │
│  └── extract_entities() - 实体提取（第二阶段）          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              AI模型 (智谱AI GLM-4-Flash)                 │
└─────────────────────────────────────────────────────────┘
```

### 3.2 数据流

```
用户选择模式
    ↓
填写对应参数
    ↓
构建AI上下文
    ├─ 首章模式：项目信息 + 开篇要求 + 登场人物
    └─ 续写模式：项目信息 + 前文 + 情节方向 + 人物
    ↓
调用AI生成（多版本）
    ├─ Version 1 (temperature=0.8)
    ├─ Version 2 (temperature=0.85)
    └─ Version 3 (temperature=0.9)
    ↓
保存到草稿表
    ↓
用户选择版本
    ↓
保存到章节内容
```

---

## 四、API设计

### 4.1 统一生成接口

**端点**：`POST /api/chapters/generate`

**请求参数**：

```json
{
  "mode": "simple|standard|advanced",
  "project_id": 1,
  "chapter_number": 1,

  // 首章模式（chapter_number == 1）
  "first_chapter_mode": {
    "opening_scene": "开篇场景",
    "key_elements": ["要素1", "要素2"],
    "tone": "基调"
  },

  // 续写模式（chapter_number > 1）
  "continue_mode": {
    "previous_chapter_id": 1,
    "transition": "紧接上文",
    "plot_direction": "情节方向",
    "conflict_point": "冲突点"
  },

  // 通用参数
  "featured_characters": [1, 3],
  "related_world_settings": [2, 7],
  "related_plot_nodes": [10],
  "word_count": 2000,
  "versions": 3,
  "style_intensity": 70,
  "pov_character_id": 1,
  "temperature": 0.8
}
```

**响应格式**：

```json
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "chapter_id": 123,
    "versions": [
      {
        "version_id": "v1",
        "content": "生成的完整内容...",
        "word_count": 1950,
        "summary": "AI生成的版本摘要"
      }
    ],
    "context_used": {
      "previous_chapter": {
        "id": 122,
        "ending": "...最后800字..."
      },
      "characters": ["张三", "李四"],
      "world_settings": ["修仙体系", "宗门规则"]
    }
  }
}
```

### 4.1.1 API兼容策略

**现状**：现有系统有 `POST /api/chapters/{id}/generate` 接口（简单模式）

**兼容方案**：

```
旧接口（保留向后兼容）：
POST /api/chapters/{id}/generate
参数：prompt: str
行为：简单模式生成，覆盖章节内容
状态：标记为 @deprecated，计划在下一版本移除

新接口（推荐使用）：
POST /api/chapters/generate
参数：完整JSON对象（支持三种模式）
行为：多版本生成，保存到草稿表
状态：稳定功能
```

**迁移路径**：

1. **第一阶段**（v1.0）：
   - 新旧接口并存
   - 旧接口调用新接口的简单模式
   - 前端逐步迁移到新接口

2. **第二阶段**（v1.5）：
   - 旧接口标记为 `@deprecated`
   - 文档中说明废弃计划
   - 引导用户使用新接口

3. **第三阶段**（v2.0）：
   - 完全移除旧接口
   - 仅保留新接口

### 4.2 版本选择接口

**端点**：`POST /api/chapters/{chapter_id}/select-version`

**请求参数**：

```json
{
  "version_id": "v2",
  "edited_content": "用户编辑后的内容（可选）"
}
```

**响应**：更新后的章节完整信息

### 4.3 实体提取接口（第二阶段）

**端点**：`POST /api/chapters/{chapter_id}/extract-entities`

**响应**：

```json
{
  "code": 200,
  "data": {
    "summary": {
      "new_characters_count": 2,
      "new_locations_count": 1
    },
    "new_characters": [
      {
        "name": "王五",
        "personality": "沉稳、冷静",
        "suggested": true
      }
    ]
  }
}
```

---

## 五、数据库设计

### 5.1 新增表：内容生成版本草稿

```sql
CREATE TABLE content_generation_drafts (
    id SERIAL PRIMARY KEY,
    chapter_id INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    version_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    summary TEXT,
    is_selected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(chapter_id, version_id)
);

CREATE INDEX idx_drafts_chapter ON content_generation_drafts(chapter_id);
```

**用途**：
- 保存多个生成版本供用户选择
- 支持版本回溯
- 防止用户后悔

### 5.2 现有表字段说明

**现有表无需修改**，所有字段已满足需求：
- `chapters` 表：`content`, `outline`, `pov_character_id`
- `characters` 表：`character_arcs` (JSONB)
- `world_settings` 表：`related_entities` (JSON)
- `plot_nodes` 表：`related_characters`, `related_world_settings`

---

## 六、AI服务设计

### 6.1 上下文构建策略

#### 6.1.1 首章上下文

```python
def _build_first_chapter_context(project, mode, options, db):
    context = []

    # 1. 项目基础信息（详细）
    context.append(f"书名：{project.title}")
    context.append(f"类型：{project.genre}")
    context.append(f"简介：{project.summary}")
    context.append(f"文风：{project.style}")
    context.append(f"目标读者：{project.target_readers}")

    # 2. 开篇要求
    if options.get("first_chapter_mode"):
        context.append(f"开篇场景：{opening_scene}")
        context.append(f"核心要素：{key_elements}")
        context.append(f"开篇基调：{tone}")

    # 3. 核心世界观规则
    core_settings = 获取核心规则(db, project.id)
    context.append(f"核心规则：{core_settings}")

    # 4. 登场人物
    if options.get("featured_characters"):
        characters = 获取人物详情(db, options["featured_characters"])
        context.append(f"登场人物：{格式化人物(characters)}")

    return "\n".join(context)
```

#### 6.1.2 续写上下文

```python
def _build_continue_context(project, chapter_number, mode, options, db):
    context = []

    # 1. 项目基础信息（简化）
    context.append(f"书名：{project.title}")
    context.append(f"文风：{project.style}")

    # 2. 前文提要（最后800字）
    if options.get("continue_mode"):
        previous_content = 获取前文(options["continue_mode"]["previous_chapter_id"])
        ending = 提取最后800字(previous_content)
        context.append(f"前文提要：\n{ending}")

        # 3. 衔接方式
        context.append(f"衔接：{options['continue_mode']['transition']}")
        context.append(f"本章情节：{options['continue_mode']['plot_direction']}")

    # 4. 出场人物、世界观（根据模式）
    if mode in ["standard", "advanced"]:
        context.append(build_character_context(options["featured_characters"]))
        context.append(build_world_setting_context(options["related_world_settings"]))

    # 5. 高级模式额外信息
    if mode == "advanced":
        context.append(build_plot_node_context(options["related_plot_nodes"]))
        context.append(build_pov_context(options["pov_character_id"]))

    return "\n".join(context)
```

### 6.2 多版本生成策略

```python
def generate_versions(prompt, context, versions=3, temperature=0.8, word_count=2000):
    results = []

    for i in range(versions):
        # 每个版本略微调整temperature，增加多样性
        version_temp = temperature + (i * 0.05)  # 0.8, 0.85, 0.9

        response = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": build_system_prompt(context)},
                {"role": "user", "content": prompt}
            ],
            temperature=version_temp,
            max_tokens=word_count * 2
        )

        results.append({
            "version_id": f"v{i+1}",
            "content": response.choices[0].message.content,
            "word_count": len(response.choices[0].message.content),
            "summary": generate_summary(response.choices[0].message.content)
        })

    return results
```

### 6.3 AI Prompt模板

#### 首章生成Prompt

```
你是一个专业的小说创作助手。请为以下小说创作第一章。

{context}

第一章创作要求：
1. 这是开篇章节，目标：吸引读者继续阅读
2. 字数：约{word_count}字
3. 开篇场景：{opening_scene}
4. 必须包含的要素：{key_elements}
5. 开篇基调：{tone}

创作注意事项：
- 前三章不要展开过多世界观设定，保持神秘感
- 以行动和对话开场，避免大量背景介绍
- 在章节结尾留下悬念或引入冲突
- 确保主角性格鲜明，让读者产生共鸣
- 展示而非讲述（Show, don't tell）

请开始创作第一章。
```

#### 续写Prompt

```
你是一个专业的小说创作助手。请根据以下信息续写小说。

{context}

续写要求：
1. 这是第{chapter_number}章，保持与前文的连贯性
2. 衔接方式：{transition}
3. 本章情节：{plot_direction}
4. 字数：约{word_count}字

创作注意事项：
- 保持人物性格、世界观设定的一致性
- 承接上一章的情节，不要出现逻辑漏洞
- 推进主线或支线剧情
- 在章节结尾为下章铺垫

请开始续写。
```

---

## 七、前端设计

### 7.1 续写控制面板

**位置**：章节编辑页面底部

**组件结构**：
```
┌─ 续写控制 ──────────────────────────────────────────┐
│  模式选择：⚪ 简单  ⦿ 标准  ⚪ 高级                  │
│                                                       │
│  ┌─ 标准模式参数 ─────────────────────────────┐     │
│  │ 前文内容：☑ 自动获取  [预览 800字]          │     │
│  │ 衔接方式：[紧接上文 ▼]                      │     │
│  │ 情节方向：[输入本章方向_______________]       │     │
│  │ 冲突点：[输入核心冲突_______________]         │     │
│  │ 续写字数：[2000] 字                         │     │
│  │ 生成版本：[3] 个                             │     │
│  │                                              │     │
│  │           [🎯 开始生成续写]                 │     │
│  └──────────────────────────────────────────────┘     │
│                                                       │
│  ┌─ 标准模式额外选项 ─────────────────────────┐     │
│  │ 本章出场人物：                               │     │
│  │ [☑ 张三] [☑ 李四] [+ 添加人物]             │     │
│  │ 相关世界观：[☑ 修仙体系] [+ 添加设定]        │     │
│  │ 风格强度：━━━━●━━━ 70%                      │     │
│  └──────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────┘
```

### 7.2 版本选择器

```
┌─ 版本选择 ──────────────────────────────────────────┐
│  生成了 3 个版本，请选择或编辑：                      │
│                                                       │
│  ┌─ 版本 1 ─────────────────────────────────────┐   │
│  │ 📝 1950字  |  ⭐⭐⭐☆☆  |  [查看完整内容]    │   │
│  │ 摘要：张三在山路上遇到了李四，两人交谈后...    │   │
│  │ [📄 使用此版本]  [✏️ 编辑后使用]  [🗑️ 删除]    │   │
│  └───────────────────────────────────────────────┘   │
│                                                       │
│  ┌─ 版本 2 ─────────────────────────────────────┐   │
│  │ 📝 2100字  |  ⭐⭐⭐⭐☆  |  [查看完整内容]    │   │
│  │ 摘要：张三独自走在山路上，忽然听到...          │   │
│  │ [📄 使用此版本]  [✏️ 编辑后使用]  [🗑️ 删除]    │   │
│  └───────────────────────────────────────────────┘   │
│                                                       │
│  [🔄 全部重新生成]                                    │
└───────────────────────────────────────────────────────┘
```

### 7.3 首章创建向导

```
┌─ 创建第一章 ─────────────────────────────────────────┐
│  步骤 1/3：基础信息                                   │
│  章节号：自动生成（第1章）                            │
│  章节标题：[第一章 惊变_______________]                │
│  生成方式：⦿ AI生成首章  ⚪ 手动编写                  │
│              [下一步 →]                              │
│                                                       │
│  步骤 2/3：首章设置                                   │
│  开篇场景：                                           │
│  [例如：主角在家中醒来_______________]                 │
│  核心要素：[☑] 主角登场  [☑] 悬念设置                 │
│  开篇基调：[悬疑 ▼]                                   │
│              [上一步]  [下一步 →]                     │
│                                                       │
│  步骤 3/3：高级设置                                   │
│  登场人物：[☑ 张三]                                   │
│  目标字数：[2000] 字                                  │
│              [上一步]  [🚀 开始生成]                  │
└───────────────────────────────────────────────────────┘
```

---

## 八、错误处理

### 8.1 API错误码

| 错误场景 | HTTP码 | 错误信息 | 处理策略 |
|---------|--------|---------|---------|
| **认证相关** ||||
| JWT Token无效 | 401 | 未授权访问，请重新登录 | 跳转到登录页 |
| 无权访问项目 | 403 | 项目不存在或无权访问 | 返回项目列表 |
| 请求速率超限 | 429 | 请求过于频繁，请稍后再试 | 显示重试时间（60秒） |
| **资源相关** ||||
| 章节不存在 | 404 | 章节不存在 | 返回404，前端提示返回列表 |
| 项目不存在 | 404 | 项目不存在 | 返回404，前端提示返回列表 |
| 人物/设定不存在 | 404 | 指定的人物或设定不存在 | 提示用户重新选择 |
| **配额相关** ||||
| 达到每日生成上限 | 403 | 今日生成次数已达上限（10次） | 提示明日再试或升级配额 |
| 月度预算不足 | 403 | 月度API预算不足（剩余¥X.XX） | 显示剩余预算，提示充值 |
| **AI服务相关** ||||
| AI服务未配置 | 500 | AI服务未配置，请检查API密钥 | 返回500，提示管理员 |
| AI服务不可用 | 503 | AI服务暂时不可用，请稍后重试 | 提供重试时间估计 |
| AI生成超时 | 504 | 生成超时，请重试 | 返回504，显示重试按钮 |
| 部分版本失败 | 200 | 生成完成，但有X个版本失败 | 显示成功版本，提供重试选项 |
| **内容质量相关** ||||
| 字数严重不足 | 200 | 生成成功，但字数不足（X/2000） | 警告提示，建议扩写或重新生成 |
| 前文内容为空 | 400 | 前文内容为空，无法续写 | 提示用户先完成前一章 |
| **系统错误** ||||
| 版本保存失败 | 500 | 版本保存失败，请重试 | 记录日志，提示重试 |
| 数据库错误 | 500 | 数据库错误，请联系管理员 | 记录详细日志，通知管理员 |
| 未知错误 | 500 | 系统错误，请稍后重试 | 记录错误堆栈，返回通用错误信息 |

### 8.2 边界情况处理

**场景1：前文内容过长**
- 策略：只取最后800字作为前文提要
- 原因：控制token消耗，聚焦最相关内容

**场景2：前文内容为空或不足**
- 策略：
  - 如果上一章内容为空，提示用户"前章内容为空，请先完成前一章"
  - 如果不足800字，使用全部可用内容

**场景3：AI生成部分版本失败**
- 策略：
  - 如果3个版本中有1-2个失败，返回成功的版本
  - 提示用户："生成了X个版本，有Y个版本失败，是否重试？"
  - 提供"重新生成失败版本"按钮

**场景4：第一章节生成**
- 策略：
  - 检测 `chapter_number == 1`
  - 跳过前文获取逻辑
  - 使用首章模式构建上下文

**场景5：并发生成请求**
- 策略：
  - 使用速率限制（10次/分钟）
  - 超出限制返回429错误
  - 提供排队功能（可选，第二阶段）

---

### 8.3 生成进度反馈

**问题**：用户需等待30秒无提示，体验差

**解决方案**：使用WebSocket推送实时进度

#### 8.3.1 后端实现

```python
from fastapi import WebSocket

@app.websocket("/ws/chapters/generate/{task_id}")
async def generation_progress(websocket: WebSocket, task_id: str):
    await websocket.accept()

    try:
        # 生成过程中推送进度
        for i, version in enumerate(generate_versions(...)):
            await websocket.send_json({
                "event": "version_generated",
                "data": {
                    "version_number": i + 1,
                    "total_versions": 3,
                    "progress": ((i + 1) / 3) * 100,
                    "version_id": version["version_id"],
                    "word_count": version["word_count"]
                }
            })

        await websocket.send_json({
            "event": "completed",
            "data": {"total_versions": 3}
        })
    except Exception as e:
        await websocket.send_json({
            "event": "error",
            "data": {"message": str(e)}
        })
    finally:
        await websocket.close()
```

#### 8.3.2 前端实现

```typescript
// 建立WebSocket连接
const ws = new WebSocket(`ws://api/ws/chapters/generate/${taskId}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.event) {
    case 'version_generated':
      setProgress(data.data.progress);
      setGeneratedVersions(prev => [...prev, data.data]);
      break;

    case 'completed':
      setGenerating(false);
      message.success(`生成完成，共${data.data.total_versions}个版本`);
      break;

    case 'error':
      setGenerating(false);
      message.error(`生成失败：${data.data.message}`);
      break;
  }
};
```

#### 8.3.3 前端UI

```
┌─ 生成中... ──────────────────────────────────────────┐
│  版本 1：███████████ 100%  (1950字) ✓                │
│  版本 2：███████████ 100%  (2100字) ✓                │
│  版本 3：████████░░░  70%  生成中...                  │
│                                                       │
│  总进度：███░░░░░░░  73%  预计剩余时间：8秒            │
│  [✗ 取消生成]                                        │
└───────────────────────────────────────────────────────┘
```

---

## 九、测试策略

### 9.1 单元测试

**AI服务测试**：
- `test_build_first_chapter_context()`
- `test_build_continue_context()`
- `test_generate_versions()`
- `test_extract_entities()`

**API测试**：
- `test_generate_first_chapter()`
- `test_continue_chapter()`
- `test_select_version()`
- `test_extract_entities_api()`

### 9.2 集成测试

**完整流程**：
1. 创建项目 → 2. 创建设定 → 3. 生成第一章 → 4. 选择版本 → 5. 续写第二章

### 9.3 性能测试

- 生成时间：目标<30秒（3版本）
- 提取时间：目标<10秒
- 并发：10用户同时续写

---

## 十、实施计划

### 10.1 第一阶段（核心续写）

**后端开发**（2-3周）：
1. 实现 `build_generation_context()` 方法
2. 实现 `generate_versions()` 方法
3. 创建 `/api/chapters/generate` 接口
4. 创建草稿表和版本选择接口
5. 编写单元测试

**前端开发**（1-2周）：
1. 续写控制面板组件
2. 版本选择器组件
3. 首章创建向导
4. API集成

**测试与优化**（1周）：
1. 集成测试
2. 性能优化
3. Bug修复

### 10.2 第二阶段（智能提取）

**⚠️ 重要提示**：实体识别是复杂的NLP任务，准确性受AI模型能力限制。建议第一阶段稳定后再评估是否实施。

**风险与挑战**：
- **识别准确性**：AI可能误识别或遗漏实体，需要人工校验
- **性能开销**：实体分析需要额外的API调用，增加成本和延迟
- **复杂度高**：涉及NLP、实体去重、关系匹配等多个复杂逻辑
- **用户期望管理**：需要明确告知用户这是辅助功能，准确性有限

**开发**（2-3周，建议）：
1. 实现 `extract_entities()` 方法
   - 使用AI分析文本，提取新实体
   - 与现有实体库对比去重
   - 标记"新实体"状态
2. 创建实体提取API
   - `POST /api/chapters/{id}/extract-entities`
   - 返回候选实体列表供用户确认
3. 前端弹窗确认组件
   - 显示提取的实体
   - 用户可选择/编辑/拒绝
   - 批量添加到设定库
4. 手动提取工具（降级方案）
   - 用户选中文本
   - 选择提取类型（人物/地点/事件）
   - 填写表单添加到设定库

**降级方案**：
如果AI提取效果不理想，提供手动标记界面作为备选方案：

```
┌─ 手动提取工具 ──────────────────────────────────────┐
│  1. 在编辑器中选中要提取的文本                        │
│  2. 点击提取类型：                                    │
│     [👤 提取为人物] [🌍 提取为世界观]                 │
│     [📍 提取为地点]   [📖 提取为事件]                 │
│  3. 在弹出的表单中确认信息，保存到设定库              │
│                                                       │
│  或：                                                 │
│  [🔍 智能分析全章] - 自动提取（可能不准确）          │
└───────────────────────────────────────────────────────┘
```

**测试与优化**（1-2周）：
1. AI提取准确性测试（使用测试样本评估准确率）
2. 用户体验优化（简化确认流程）
3. 文档完善（明确说明功能限制）

**成功标准**：
- 实体提取准确率 ≥ 70%（人物识别）
- 用户确认率 ≥ 60%（说明提取有价值）
- 如果无法达到，考虑延后或取消此功能

## 十一、验收标准

### 11.1 功能验收

- ✅ 可以直接生成第一章
- ✅ 可以基于前文续写
- ✅ 支持三种模式（简单/标准/高级）
- ✅ 生成2-3个版本供选择
- ✅ 版本可以保存、选择、编辑
- ✅ AI自动提取关键信息（第二阶段）

### 11.2 性能验收

- 单章节生成时间 < 30秒
- 实体提取时间 < 10秒
- 支持10个并发用户

### 11.3 体验验收

- 界面直观，操作流畅
- AI生成内容符合设定
- 多版本有明显差异

---

## 附录

### A. 相关文件

**后端**：
- `backend/app/api/chapters.py` - 章节API
- `backend/app/services/ai_service.py` - AI服务
- `backend/app/models/chapter.py` - 章节模型

**前端**：
- `frontend/src/pages/ProjectDetail.tsx` - 章节编辑页
- `frontend/src/services/api.ts` - API客户端

### B. 配置文件

**环境变量**（`.env`）：
```bash
ZHIPUAI_API_KEY=your-api-key
OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4/
AI_MODEL=glm-4-flash
```

### C. 参考资料

- [智谱AI API文档](https://open.bigmodel.cn/dev/api)
- [OpenAI SDK文档](https://github.com/openai/openai-python)
- 项目PRD：`小说生成与管理系统 PRD（产品需求文档）.md`

---

**文档结束**
