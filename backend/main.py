from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.database import Base, engine
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

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI小说生成与管理系统API",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

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


# 注册全局异常处理器
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(NotFoundException, not_found_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
