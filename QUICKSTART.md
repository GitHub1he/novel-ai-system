# 小说AI生成与管理系统 - 快速启动指南

## 🚀 快速启动

### 方式一：使用 Docker（推荐）

**1. 启动 PostgreSQL 数据库**

```bash
# 在项目根目录运行
docker-compose up -d postgres
```

> 💡 **提示**：Docker 会自动创建数据库、用户和权限，无需手动执行 SQL 脚本

**2. 启动后端**

```bash
cd backend

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和智谱AI API密钥
# ZHIPUAI_API_KEY=your-zhipuai-api-key (获取地址: https://open.bigmodel.cn/usercenter/apikeys)

# 安装依赖
pip install -r requirements.txt

# 初始化数据库和创建测试用户
python init_db.py

# 启动服务
python main.py
```

后端将在 http://localhost:8000 启动

> 📝 **测试账号**：初始化脚本会创建测试用户
> - 邮箱: `test@example.com`
> - 用户名: `testuser`
> - 密码: `password123`

**3. 启动前端**（新开终端）

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动

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

**3. 启动后端**

```bash
cd backend

# 配置环境变量
cp .env.example .env
# 编辑 .env，设置 DATABASE_URL 和智谱AI API密钥
# DATABASE_URL=postgresql://novel_ai_user:novel_ai_password@localhost:5432/novel_ai_db
# ZHIPUAI_API_KEY=your-zhipuai-api-key (获取地址: https://open.bigmodel.cn/usercenter/apikeys)

# 安装依赖
pip install -r requirements.txt

# 初始化数据库和创建测试用户
python init_db.py

# 启动服务
python main.py
```

> 📝 **测试账号**：初始化脚本会创建测试用户
> - 邮箱: `test@example.com`
> - 用户名: `testuser`
> - 密码: `password123`

**4. 启动前端**（新开终端）

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 📋 验证安装

访问以下地址验证服务是否正常运行：

- **前端应用**: http://localhost:5173
- **后端 API 文档**: http://localhost:8000/api/docs
- **健康检查**: http://localhost:8000/health

---

## 🔧 常见问题

### Q: API 返回 500 Internal Server Error？
**A:** 运行诊断脚本排查问题：
```bash
cd backend
python diagnose.py
```

诊断脚本会检查：
- 数据库连接状态
- 表是否存在
- 用户数据是否存在
- API 查询是否正常

### Q: 如何初始化数据库？
**A:** 两种方式：
```bash
# 方式1: Python脚本（推荐）
cd backend
python init_db.py

# 方式2: SQL脚本
# 先清理旧表（如果存在）
docker-compose exec -T postgres psql -U novel_ai_user -d novel_ai_db < backend/rebuild_db.sql
# 再创建新表
docker-compose exec -T postgres psql -U novel_ai_user -d novel_ai_db < backend/init_db_fresh.sql
```

### Q: SQL 脚本报错 "column does not exist"？
**A:** 这是因为表已存在但结构旧。运行清理脚本：
```bash
docker-compose exec -T postgres psql -U novel_ai_user -d novel_ai_db < backend/rebuild_db.sql
```

### Q: 启动后端报错 "No module named 'xxx'"
**A:** 安装缺失的依赖：
```bash
cd backend
pip install -r requirements.txt
```

### Q: 前端启动失败 "Cannot resolve dependency"
**A:** 删除 node_modules 重新安装：
```bash
cd frontend
rm -rf node_modules
npm install
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

## 📄 数据库脚本

项目提供 SQL 初始化脚本 `backend/init_db.sql`，包含：
- ✅ 所有表的创建语句
- ✅ 索引优化
- ✅ 默认测试用户
- ✅ 项目统计视图

**后续数据库改动请直接修改此文件。**

---

## 🐳 Docker 常用命令

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

---

## 📚 更多文档

- **[后端详细文档](./backend/README.md)** - 后端技术栈、API接口、开发指南
- **[前端详细文档](./frontend/README.md)** - 前端技术栈、组件说明、开发指南