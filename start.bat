@echo off
chcp 65001 >nul
echo ====================================
echo 小说AI系统 - 快速启动脚本
echo ====================================
echo.

echo [1/3] 启动数据库...
docker-compose up -d postgres
if errorlevel 1 (
    echo 数据库启动失败，请确保Docker已安装并运行
    pause
    exit /b 1
)
echo 数据库启动成功！
echo.

echo [2/3] 启动后端服务...
cd backend
start cmd /k "python main.py"
cd ..
echo 后端服务启动中...
timeout /t 3 >nul
echo.

echo [3/3] 启动前端服务...
cd frontend
start cmd /k "npm run dev"
cd ..
echo 前端服务启动中...
timeout /t 3 >nul
echo.

echo ====================================
echo 启动完成！
echo 后端地址: http://localhost:8000
echo 前端地址: http://localhost:5173
echo API文档: http://localhost:8000/api/docs
echo ====================================
pause
