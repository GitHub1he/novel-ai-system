from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.logger import logger
from app.core.exception_handler import (
    BusinessException,
    NotFoundException,
    ValidationException,
    business_exception_handler,
    not_found_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    validation_error_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from app.api import auth, projects, chapters, characters, world_settings, plot_nodes, context_analysis
from app.core.websocket_manager import websocket_endpoint, send_websocket_message
from app.models import ContentGenerationDraft

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 配置速率限制
limiter = Limiter(key_func=get_remote_address)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI小说生成与管理系统API",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
app.state.limiter = limiter

# 清理旧草稿函数
def clean_old_drafts():
    """清理7天前的未选中草稿"""
    try:
        db = SessionLocal()
        cutoff = datetime.now() - timedelta(days=7)
        deleted_count = db.query(ContentGenerationDraft).filter(
            ContentGenerationDraft.created_at < cutoff,
            ContentGenerationDraft.is_selected == False
        ).delete()
        db.commit()
        logger.info(f"清理了 {deleted_count} 个未选中的旧草稿")
    except Exception as e:
        logger.error(f"清理旧草稿时出错: {str(e)}")
        db.rollback()
    finally:
        db.close()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """日志中间件"""
    logger.info(f"收到请求: {request.method} {request.url}")
    logger.info(f"请求头: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"响应状态: {response.status_code}")
    return response


# 速率限制异常处理器
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """处理速率限制超出的异常"""
    return {
        "code": 429,
        "message": f"请求过于频繁，请稍后再试。重试时间: {exc.detail}",
        "data": None
    }

# 注册全局异常处理器
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(NotFoundException, not_found_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 添加速率限制中间件
app.add_middleware(SlowAPIMiddleware, limiter=limiter)

# 创建调度器
scheduler = BackgroundScheduler()
scheduler.start()

# 添加定时任务
scheduler.add_job(
    clean_old_drafts,
    CronTrigger(hour=2, minute=0),  # 每天2点执行
    id="clean_old_drafts",
    replace_existing=True,
)

# 应用关闭时停止调度器
import atexit
atexit.register(lambda: scheduler.shutdown())


# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(chapters.router, prefix="/api")
app.include_router(characters.router, prefix="/api")
app.include_router(world_settings.router, prefix="/api")
app.include_router(plot_nodes.router, prefix="/api")
app.include_router(context_analysis.router, prefix="/api")


@app.get("/", tags=["根路径"])
def read_root():
    """API根路径"""
    return {
        "message": "欢迎使用AI小说生成与管理系统",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.websocket("/ws/chapters/generate/{task_id}")
async def websocket_chapters_generate(websocket: WebSocket, task_id: str):
    """WebSocket端点，用于推送章节生成进度"""
    await websocket_endpoint(websocket, task_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
