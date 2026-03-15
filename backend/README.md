# Novel AI System - Backend

AI小说生成与管理系统后端服务

## 技术栈

- **框架**: FastAPI
- **数据库**: PostgreSQL
- **AI**: OpenAI API
- **认证**: JWT

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
```

主要配置项：
- `DATABASE_URL`: PostgreSQL数据库连接
- `OPENAI_API_KEY`: OpenAI API密钥（或国内大模型API）

### 3. 启动数据库

使用Docker启动PostgreSQL：

```bash
docker run -d \
  --name novel_ai_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=novel_ai \
  -p 5432:5432 \
  postgres:15
```

### 4. 运行服务

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 http://localhost:8000 启动

API文档：http://localhost:8000/api/docs

## API接口

### 认证

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 项目管理

- `POST /api/projects/` - 创建项目
- `GET /api/projects/` - 获取项目列表
- `GET /api/projects/{id}` - 获取项目详情
- `PUT /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目

### 章节管理

- `POST /api/chapters/` - 创建章节
- `GET /api/chapters/{id}` - 获取章节
- `PUT /api/chapters/{id}` - 更新章节
- `POST /api/chapters/{id}/generate` - AI生成章节内容

## 项目结构

```
backend/
├── app/
│   ├── api/          # API路由
│   ├── core/         # 核心配置
│   ├── models/       # 数据库模型
│   ├── schemas/      # Pydantic模型
│   └── services/     # 业务服务
├── main.py           # 应用入口
├── requirements.txt  # 依赖列表
└── .env.example      # 环境变量模板
```

## 开发说明

### 数据库模型

- **User**: 用户
- **Project**: 小说项目
- **Character**: 人物
- **Chapter**: 章节
- **WorldSetting**: 世界观设定

### AI集成

支持配置不同的AI服务：
- OpenAI (GPT-3.5/GPT-4)
- 国内大模型（文心一言、通义千问等）通过修改API_BASE

## 后续开发计划

- [ ] 增加人物管理API
- [ ] 增加世界观设定API
- [ ] 实现版本管理
- [ ] 增加逻辑一致性检查
- [ ] 实现导出功能
