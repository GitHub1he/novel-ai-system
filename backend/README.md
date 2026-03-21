# Novel AI System - Backend

AI小说生成与管理系统后端服务

## 技术栈

- **框架**: FastAPI
- **数据库**: PostgreSQL
- **AI**: OpenAI API
- **认证**: JWT

## 快速开始

### 方式一：使用 Docker（推荐）

**1. 启动 PostgreSQL 数据库**

```bash
# 在项目根目录运行
docker-compose up -d postgres
```

> 💡 **提示**：Docker 会自动创建数据库和用户，无需手动执行 SQL 脚本

**2. 配置环境变量**

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
```

确保数据库配置正确：

```env
DATABASE_URL=postgresql://novel_ai_user:novel_ai_password@localhost:5432/novel_ai_db
ZHIPUAI_API_KEY=your-zhipuai-api-key
```

**获取智谱AI密钥：**
1. 访问：https://open.bigmodel.cn/usercenter/apikeys
2. 注册/登录并创建API密钥
3. 复制到 `.env` 文件的 `ZHIPUAI_API_KEY`

**3. 初始化数据库**

选择以下方式之一：

**方式A：使用 Python 脚本（推荐）**
```bash
python init_db.py
```

**方式B：使用 SQL 脚本**
```bash
# 如果数据库已存在旧表，先清理
docker-compose exec -T postgres psql -U novel_ai_user -d novel_ai_db < rebuild_db.sql

# 然后创建新表
docker-compose exec -T postgres psql -U novel_ai_user -d novel_ai_db < init_db_fresh.sql

# 或一步完成（本地 PostgreSQL）
psql -U novel_ai_user -d novel_ai_db -f rebuild_db.sql -f init_db_fresh.sql
```

**3. 安装依赖并启动后端**

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

后端将在 http://localhost:8000 启动

---

### 方式二：本地安装 PostgreSQL

**1. 安装 PostgreSQL**

- **Windows**: https://www.postgresql.org/download/windows/
- **Mac**: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql`

**2. 创建数据库**

打开 SQL Shell 或命令行：

```sql
CREATE USER novel_ai_user WITH PASSWORD 'novel_ai_password';
CREATE DATABASE novel_ai_db OWNER novel_ai_user;
GRANT ALL PRIVILEGES ON DATABASE novel_ai_db TO novel_ai_user;
```

**3. 配置环境变量**

复制 `.env.example` 到 `.env`：

```bash
cp .env.example .env
```

编辑 `backend/.env` 文件：

```env
DATABASE_URL=postgresql://novel_ai_user:novel_ai_password@localhost:5432/novel_ai_db
```

**4. 安装依赖并启动后端**

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 验证安装

访问以下地址验证服务是否正常运行：

- **API 文档**: http://localhost:8000/api/docs
- **健康检查**: http://localhost:8000/health

---

## 常见问题

### Q: 启动后端报错 "No module named 'xxx'"
**A:** 安装缺失的依赖：
```bash
pip install -r requirements.txt
```

### Q: 数据库连接失败
**A:** 检查以下几点：
1. PostgreSQL 服务是否正在运行
2. `.env` 文件中的数据库连接字符串是否正确
3. 数据库用户名、密码和数据库名是否匹配

### Q: 如何重置数据库？
**A:** 连接到数据库并重新创建：
```bash
# 使用 Docker
docker-compose exec postgres psql -U novel_ai_user -d novel_ai_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# 或本地 PostgreSQL
psql -U novel_ai_user -d novel_ai_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

然后重启后端，表结构会自动创建。

---

## Docker 常用命令

```bash
# 启动数据库
docker-compose up -d postgres

# 停止数据库
docker-compose stop postgres

# 查看日志
docker-compose logs postgres

# 进入数据库容器
docker-compose exec postgres psql -U novel_ai_user -d novel_ai_db

# 完全删除数据库（警告：会删除所有数据）
docker-compose down -v
```

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

项目默认使用 **智谱AI (GLM-4)**，提供高质量的中文小说生成能力。

**支持的模型：**
- `glm-4-flash` - 快速响应，低成本（推荐日常使用）
- `glm-4` - 标准版本，性能均衡
- `glm-4-plus` - 最强性能，适合复杂场景
- `glm-4-air` - 轻量版本，极速响应

**获取API密钥：**
1. 访问智谱AI开放平台：https://open.bigmodel.cn/
2. 注册/登录账号
3. 进入API密钥页面：https://open.bigmodel.cn/usercenter/apikeys
4. 创建新的API密钥

**配置示例：**
```env
ZHIPUAI_API_KEY=your-zhipuai-api-key
OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4/
AI_MODEL=glm-4-flash
```

如需切换回OpenAI或其他兼容服务，只需修改 `OPENAI_API_BASE` 和 `AI_MODEL`。

## 后续开发计划

- [ ] 增加人物管理API
- [ ] 增加世界观设定API
- [ ] 实现版本管理
- [ ] 增加逻辑一致性检查
- [ ] 实现导出功能
