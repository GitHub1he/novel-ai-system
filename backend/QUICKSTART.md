# 快速启动指南 - SQLite版本

## 🚀 无需Docker的快速启动方式

如果你的Docker没有运行，可以使用SQLite数据库快速启动项目（适合本地开发）。

### 步骤1：修改数据库配置

**方式A：修改环境变量（推荐）**

编辑 `backend/.env` 文件，添加：
```env
DATABASE_URL=sqlite:///./novel_ai.db
```

**方式B：直接修改代码**

编辑 `backend/app/core/config.py` 第15行，取消注释SQLite：
```python
DATABASE_URL: str = "sqlite:///./novel_ai.db"  # 取消这行的注释
```

### 步骤2：启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

后端将在 http://localhost:8000 启动，数据库文件会自动创建在 `backend/novel_ai.db`

### 步骤3：启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动服务
npm run dev
```

前端将在 http://localhost:5173 启动

### 完成！

访问 http://localhost:5173 开始使用

---

## ⚠️ 注意事项

### SQLite vs PostgreSQL

| 特性 | SQLite | PostgreSQL |
|------|--------|------------|
| 安装 | ✅ 无需安装 | ❌ 需要安装 |
| 性能 | 适合开发/测试 | 适合生产 |
| 并发 | 有限 | 优秀 |
| 功能 | 基础SQL | 高级特性 |

### 迁移到PostgreSQL

当你准备好切换到PostgreSQL时：

1. 安装PostgreSQL（见下方）
2. 修改 `.env` 中的 `DATABASE_URL`
3. 重启后端服务

---

## 📦 安装PostgreSQL（可选）

### Windows

1. 下载安装包：https://www.postgresql.org/download/windows/
2. 运行安装程序，记住密码
3. 安装后打开SQL Shell，创建数据库：
   ```sql
   CREATE DATABASE novel_ai;
   ```
4. 修改 `.env`：
   ```env
   DATABASE_URL=postgresql://postgres:你的密码@localhost:5432/novel_ai
   ```

### 使用Docker（推荐）

1. 启动Docker Desktop
2. 运行：
   ```bash
   docker-compose up -d postgres
   ```

---

## 🔧 常见问题

### Q: 启动后端报错 "No module named 'xxx'"
A: 安装缺失的依赖：
```bash
pip install -r requirements.txt
```

### Q: 前端报错 "Cannot resolve dependency"
A: 删除node_modules重新安装：
```bash
cd frontend
rm -rf node_modules
npm install
```

### Q: 数据库文件在哪？
A: SQLite数据库文件在 `backend/novel_ai.db`

### Q: 如何重置数据库？
A: 删除数据库文件，重启后端会自动创建：
```bash
cd backend
rm novel_ai.db
python main.py
```
