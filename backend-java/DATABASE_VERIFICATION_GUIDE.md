# 数据库验证指南

## 📋 阶段0：数据库验证模块 - 执行指南

### 环境准备

1. **启动PostgreSQL数据库**

```bash
# 方法1: 使用Docker (推荐)
cd D:\02_code\novel-ai-system
docker-compose up -d postgres

# 方法2: 使用本地PostgreSQL
# 确保PostgreSQL服务正在运行
# 默认连接: localhost:5432
# 数据库: novel_ai_db  
# 用户: novel_ai_user
# 密码: novel_ai_password
```

2. **验证数据库连接**

```bash
# 连接测试
psql -U novel_ai_user -d novel_ai_db -h localhost

# 或者使用Python (如果虚拟环境可用)
cd backend
source .venv/bin/activate
python -c "import psycopg2; conn = psycopg2.connect('postgresql://novel_ai_user:novel_ai_password@localhost:5432/novel_ai_db'); print('Connected successfully')"
```

### TDD执行 - 阶段0.1: 数据库连接验证

✅ **Step 1**: 创建数据库测试类 (已完成)
- 文件: `src/test/java/com/novel/ai/database/DatabaseConnectionTest.java`
- 状态: ✅ 测试类已创建

⏳ **Step 2**: 编译Java项目

```bash
cd D:\02_code\novel-ai-system\backend-java
mvn clean compile
```

⏳ **Step 3**: 运行数据库连接测试

```bash
mvn test -Dtest=DatabaseConnectionTest#testDatabaseConnection
```

⏳ **Step 4**: 验证测试结果

**预期输出**:
```
✅ 数据库连接成功
Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
```

⏳ **Step 5**: 提交代码

```bash
git add .
git commit -m "feat: complete Stage 0.1 - Database connection verification (TDD approach)"
```

### 数据库结构验证 - 阶段0.2

接下来创建表结构验证测试...

---

## 🚀 执行状态

**当前进度**: 阶段0.1完成度: 50%
- ✅ 测试类已创建
- ⏳ 等待PostgreSQL数据库启动
- ⏳ 待编译和运行测试

**下一步**: 确保PostgreSQL运行后，继续执行编译和测试验证

**需要帮助**: 如果PostgreSQL启动遇到问题，请查看错误信息或寻求技术支持。
