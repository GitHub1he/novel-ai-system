#!/bin/bash

echo "===================================="
echo "小说AI系统 - 快速启动脚本"
echo "===================================="
echo ""

echo "[1/3] 启动数据库..."
docker-compose up -d postgres
if [ $? -ne 0 ]; then
    echo "数据库启动失败，请确保Docker已安装并运行"
    exit 1
fi
echo "数据库启动成功！"
echo ""

echo "[2/3] 启动后端服务..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..
echo "后端服务启动中... (PID: $BACKEND_PID)"
sleep 3
echo ""

echo "[3/3] 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo "前端服务启动中... (PID: $FRONTEND_PID)"
sleep 3
echo ""

echo "===================================="
echo "启动完成！"
echo "后端地址: http://localhost:8000"
echo "前端地址: http://localhost:5173"
echo "API文档: http://localhost:8000/api/docs"
echo "按 Ctrl+C 停止所有服务"
echo "===================================="

# 捕获退出信号，关闭所有进程
trap "kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT TERM

# 等待
wait
