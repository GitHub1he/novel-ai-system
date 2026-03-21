# 小说生成与管理系统 - 项目结构文档

> **重要提示**：本文档用于Claude AI理解项目结构，请保持更新。

## 项目概述

这是一个基于AI的小说创作辅助系统，帮助作者进行小说创作、人物管理、世界观设定和章节管理。

### 核心功能
- 项目管理：创建和管理多个小说项目
- 章节创作：章节列表、内容编辑、大纲管理
- 人物管理：角色设定、关系网络、故事线追踪
- 世界观设定：世界观元素的创建和管理
- AI辅助：基于上下文的AI内容生成

---

## 技术栈

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI库**: Ant Design (antd)
- **路由**: React Router v6
- **HTTP客户端**: Axios

### 后端
- **框架**: FastAPI (Python)
- **数据库**: SQLAlchemy ORM + MySQL/PostgreSQL
- **认证**: JWT (JSON Web Tokens)
- **日志**: Python logging
- **AI服务**: 集成AI生成服务（待实现）

---

## 项目目录结构

```
novel-ai-system/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── auth.py        # 认证相关API
│   │   │   ├── projects.py    # 项目管理API
│   │   │   ├── chapters.py    # 章节管理API
│   │   │   ├── characters.py  # 人物管理API
│   │   │   └── world_settings.py  # 世界观设定API
│   │   ├── core/              # 核心功能
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── database.py    # 数据库连接
│   │   │   ├── exception_handler.py  # 异常处理
│   │   │   └── logger.py      # 日志配置
│   │   ├── models/            # 数据模型
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── project.py     # 项目模型
│   │   │   ├── chapter.py     # 章节模型
│   │   │   ├── character.py   # 人物模型
│   │   │   └── world_setting.py  # 世界观模型
│   │   ├── schemas/           # Pydantic模式（请求/响应验证）
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── chapter.py
│   │   │   ├── character.py
│   │   │   └── world_setting.py
│   │   ├── services/          # 业务逻辑服务
│   │   │   └── ai_service.py  # AI生成服务
│   │   └── main.py            # FastAPI应用入口
│   ├── requirements.txt       # Python依赖
│   ├── .env.example           # 环境变量示例
│   └── init_db.py             # 数据库初始化脚本
│
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/        # React组件
│   │   │   ├── CharacterManagement.tsx      # 人物管理组件
│   │   │   ├── CharacterArcEditor.tsx       # 人物成长弧编辑器
│   │   │   ├── AttributesEditor.tsx         # 属性编辑器
│   │   │   ├── VoiceStyleEditor.tsx         # 声音风格编辑器
│   │   │   ├── WorldSettingManagement.tsx   # 世界观管理组件
│   │   │   └── EntitySelector.tsx           # 实体选择器
│   │   ├── pages/            # 页面组件
│   │   │   ├── Login.tsx     # 登录页
│   │   │   ├── Register.tsx  # 注册页
│   │   │   ├── Dashboard.tsx # 项目列表页
│   │   │   └── ProjectDetail.tsx  # 项目详情页（核心）
│   │   ├── services/         # API服务
│   │   │   └── api.ts        # Axios封装和API定义
│   │   ├── types/            # TypeScript类型定义
│   │   │   └── index.ts      # 核心类型定义
│   │   ├── main.tsx          # React入口
│   │   └── App.tsx           # 根组件
│   ├── package.json          # Node依赖
│   ├── vite.config.ts        # Vite配置
│   └── index.html            # HTML入口
│
├── docker-compose.yml         # Docker编排配置
├── QUICKSTART.md             # 快速开始指南
└── README.md                 # 项目说明
```

---

## 数据模型关系

```
User (用户)
  ├── 1:N Project (项目)
       ├── 1:N Chapter (章节)
       ├── 1:N Character (人物)
       └── 1:N WorldSetting (世界观设定)
```

### 核心模型说明

**User (用户)**
- id, email, username, password
- 角色：管理员/普通用户
- 状态：激活/未激活

**Project (项目)**
- 标题、作者、类型、风格
- 目标字数、完成度
- 状态：草稿/写作中/已完成/归档

**Chapter (章节)**
- 章节号、标题、内容、大纲
- 状态：草稿/修订中/已完成
- 字数统计、版本号

**Character (人物)**
- 基本信息：姓名、年龄、性别
- 角色定位：主角/反派/配角/次要
- 人物弧光：初始状态→转折点→最终状态
- 声音风格、样本对话

**WorldSetting (世界观设定)**
- 设定类型：时代/地域/规则/文化/力量体系/地点/势力/物品/事件
- 核心规则标记
- 关联实体

---

## API路由结构

### 认证相关 `/auth`
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录

### 项目管理 `/projects`
- `GET /projects/list` - 获取项目列表
- `GET /projects/detail/{id}` - 获取项目详情
- `POST /projects/create` - 创建项目
- `POST /projects/update/{id}` - 更新项目
- `POST /projects/del/{id}` - 删除项目

### 章节管理 `/chapters`
- `GET /chapters/list/{project_id}` - 获取章节列表（不包含content）
- `GET /chapters/{chapter_id}` - 获取章节详情（包含content）
- `POST /chapters/` - 创建章节
- `PUT /chapters/{chapter_id}` - 更新章节
- `POST /chapters/{chapter_id}/generate` - AI生成章节内容

### 人物管理 `/characters`
- `GET /characters/list/{project_id}` - 获取人物列表
- `GET /characters/detail/{id}` - 获取人物详情
- `POST /characters/create` - 创建人物
- `POST /characters/update/{id}` - 更新人物
- `POST /characters/del/{id}` - 删除人物

### 世界观设定 `/world-settings`
- `GET /world-settings/list/{project_id}` - 获取世界观列表
- `GET /world-settings/detail/{id}` - 获取世界观详情
- `POST /world-settings/create` - 创建世界观设定
- `POST /world-settings/update/{id}` - 更新世界观设定
- `POST /world-settings/del/{id}` - 删除世界观设定

---

## 前端页面结构

### 页面路由
- `/login` - 登录页
- `/register` - 注册页
- `/dashboard` - 项目列表
- `/project/:id` - 项目详情（核心页面）

### 核心页面：ProjectDetail (`/src/pages/ProjectDetail.tsx`)

**布局结构**：
```
┌─────────────────────────────────────────────────┐
│  Tab切换 (章节创作 | 人物管理 | 世界观设定)        │
├─────────────────────────────────────────────────┤
│  主内容区              │  右侧面板 (300px)       │
│                       │                         │
│  章节列表/编辑区        │  - 项目信息              │
│  - 章节列表            │  - 快捷指令              │
│  - 章节编辑框          │  - 当前章节信息          │
│  - AI指令输入          │  - 提示信息              │
│                       │                         │
└─────────────────────────────────────────────────┘
```

**关键状态管理**：
- `project`: 当前项目信息
- `chapters`: 章节列表
- `currentChapter`: 当前选中的章节（含完整内容）
- `loadingChapter`: 章节加载状态

**重要函数**：
- `fetchChapters()`: 获取章节列表（不含content）
- `handleSelectChapter()`: 点击章节时获取完整详情
- `handleCreateChapter()`: 创建新章节
- `handleStatusChange()`: 切换章节状态
- `handleSaveContent()`: 保存章节内容
- `handleEditOutline()`: 编辑大纲
- `handleGenerate()`: AI生成内容

---

## 响应格式规范

所有API响应统一使用以下格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

**特殊响应**：
- 列表接口：`data: { items: [], total: number }`
- 详情接口：`data: { ...object }`
- 创建/更新：`data: { ...created_object }`

---

## 开发规范

### 后端
1. 使用 `ChapterStatus`、`ProjectStatus` 等枚举类型
2. 列表接口不返回大字段（如content、outline）
3. 使用 `NotFoundException`、`BusinessException` 处理错误
4. 所有更新操作记录日志

### 前端
1. 使用 TypeScript 类型定义
2. API调用统一使用 `src/services/api.ts`
3. 列表和详情分离：列表不加载大字段
4. 使用 Ant Design 组件库
5. 错误处理使用 `message.error()`
6. 成功操作使用 `message.success()`

---

## 常见任务指南

### 添加新功能模块
1. 后端：创建 `app/models/xxx.py`、`app/schemas/xxx.py`、`app/api/xxx.py`
2. 前端：创建 `src/components/XxxManagement.tsx`、添加类型到 `src/types/index.ts`
3. 在 `ProjectDetail.tsx` 的 Tab 中添加新页面

### 修复API问题
1. 检查 `backend/app/api/` 对应的路由文件
2. 确认响应格式符合规范
3. 检查异常处理和日志

### 修复UI问题
1. 检查 `frontend/src/pages/ProjectDetail.tsx`
2. 确认状态管理和事件处理
3. 查看浏览器控制台错误

---

## 最近更新 (2026-03)

### 已完成
- ✅ 章节列表性能优化（不返回content字段）
- ✅ 章节详情按需加载
- ✅ 章节状态切换功能（草稿/修订中/已完成）
- ✅ 章节创建功能（自动计算章节号）
- ✅ 大纲编辑功能
- ✅ 内容保存功能
- ✅ 返回列表按钮
- ✅ 修复编辑器中文输入问题（使用TextArea）
- ✅ UI样式优化（卡片式设计、颜色编码、悬停效果）

### 待实现
- ⏳ AI内容生成功能（后端集成）
- ⏳ 章节导出功能
- ⏳ 自动保存功能
- ⏳ 章节删除功能
- ⏳ 人物和世界观管理的完整实现

### 已知问题
- 无

---

## 环境配置

### 后端
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 配置数据库等信息
python init_db.py     # 初始化数据库
python -m app.main    # 启动后端服务
```

### 前端
```bash
cd frontend
npm install
npm run dev          # 启动开发服务器
```

---

## 数据库初始化

运行 `backend/init_db.py` 脚本会创建所有必要的表。

注意：初始化前需要配置 `.env` 文件中的数据库连接信息。

---

## 快速定位代码

| 功能 | 文件位置 |
|-----|---------|
| 章节创作页面 | `frontend/src/pages/ProjectDetail.tsx` |
| 章节API | `backend/app/api/chapters.py` |
| 章节模型 | `backend/app/models/chapter.py` |
| 章节Schema | `backend/app/schemas/chapter.py` |
| API定义 | `frontend/src/services/api.ts` |
| 类型定义 | `frontend/src/types/index.ts` |
| 人物管理组件 | `frontend/src/components/CharacterManagement.tsx` |
| 世界观管理组件 | `frontend/src/components/WorldSettingManagement.tsx` |

---

**最后更新**: 2026-03-16
**维护者**: Claude AI Assistant
