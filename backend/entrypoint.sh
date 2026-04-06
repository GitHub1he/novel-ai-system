#!/bin/bash
set -e

echo "=========================================="
echo "Novel AI Backend 启动脚本"
echo "=========================================="

# 等待数据库就绪
echo "等待数据库启动..."
until pg_isready -h postgres -U novel_ai_user -d novel_ai_db; do
  echo "数据库尚未就绪，等待中..."
  sleep 2
done

echo "✓ 数据库已就绪"

# 检查是否需要初始化数据库
echo "检查数据库是否需要初始化..."

# 尝试连接数据库并检查 users 表是否存在
TABLE_EXISTS=$(python -c "
from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print('users' in tables)
" 2>/dev/null || echo "False")

if [ "$TABLE_EXISTS" = "True" ]; then
  echo "✓ 数据库已初始化，跳过"
else
  echo "初始化数据库..."
  python init_db.py
  echo "✓ 数据库初始化完成"
fi

# 启动应用
echo ""
echo "启动 FastAPI 服务..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
