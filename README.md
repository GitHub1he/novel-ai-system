# 小说AI生成与管理系统

一个基于AI的小说创作辅助系统，提供多小说管理、维度化设定配置、AI辅助生成、逻辑一致性校验等全流程创作工具。

## 项目简介

本项目旨在帮助小说创作者：
- 降低创作门槛：通过模板化、可视化配置，将模糊构思转化为精准设定
- 保障创作质量：AI辅助+逻辑校验，避免人设崩坏、剧情矛盾
- 提升创作效率：多项目并行管理、自动化生成、版本回溯

## 技术栈

### 后端
- FastAPI (Python 3.10+)
- PostgreSQL 15
- OpenAI API / 国内大模型

### 前端
- React 18 + TypeScript
- Vite
- Ant Design 5
- TipTap (富文本编辑器)

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.10+
- PostgreSQL 15+
- Docker (可选)

### 1. 克隆项目

```bash
git clone <repository-url>
cd novel-ai-system
```

### 2. 启动数据库

使用Docker（推荐）：

```bash
docker-compose up -d postgres
```

或手动安装PostgreSQL。

### 3. 配置后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库和AI API密钥

# 运行后端
python main.py
```

后端将在 http://localhost:8000 启动

API文档：http://localhost:8000/api/docs

### 4. 配置前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动

## 项目结构

```
novel-ai-system/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据库模型
│   │   ├── schemas/     # Pydantic模型
│   │   └── services/    # 业务服务
│   ├── main.py          # 应用入口
│   └── requirements.txt
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   ├── services/    # API服务
│   │   ├── types/       # 类型定义
│   │   └── utils/       # 工具
│   └── package.json
├── docker-compose.yml   # Docker配置
└── README.md
```

## MVP功能（当前阶段）

### 已实现
- 用户注册/登录
- 项目创建和管理
- 项目列表查看
- 基础布局框架
- API接口封装

### 开发中
- 章节管理
- AI内容生成
- 富文本编辑器
- 人物/世界观设定

### 规划中
- 版本管理
- 逻辑一致性检查
- 数据可视化
- 多格式导出

## 环境配置

### 后端环境变量 (.env)

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/novel_ai
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1  # 可改为国内大模型API
SECRET_KEY=your-secret-key
```

### AI服务配置

支持以下AI服务：
- OpenAI (GPT-3.5/GPT-4)
- 国内大模型（文心一言、通义千问、智谱AI等）

修改 `OPENAI_API_BASE` 即可切换不同AI服务。

## 开发指南

### 后端开发

```bash
cd backend

# 运行开发服务器（自动重载）
uvicorn main:app --reload

# 运行测试
pytest

# 数据库迁移（待实现）
alembic upgrade head
```

### 前端开发

```bash
cd frontend

# 运行开发服务器
npm run dev

# 类型检查
tsc --noEmit

# 构建生产版本
npm run build
```

## API文档

启动后端后访问：http://localhost:8000/api/docs

### 主要接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/projects/` - 获取项目列表
- `POST /api/projects/` - 创建项目
- `POST /api/chapters/` - 创建章节
- `POST /api/chapters/{id}/generate` - AI生成内容

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系开发团队。

---

> 本项目基于PRD文档开发，详见 [小说生成与管理系统 PRD](./小说生成与管理系统 PRD（产品需求文档）.md)
