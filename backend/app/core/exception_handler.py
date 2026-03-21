from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import traceback
from typing import Union
from app.core.logger import logger


class BusinessException(Exception):
    """业务异常"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(Exception):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在"):
        self.message = message
        super().__init__(self.message)


class ValidationException(Exception):
    """验证异常"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理器"""
    logger.warning(f"业务异常: {exc.message} - URL: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # 统一返回200
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None
        }
    )


async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """资源不存在异常处理器"""
    logger.warning(f"资源不存在: {exc.message} - URL: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # 统一返回200
        content={
            "code": 404,
            "message": exc.message,
            "data": None
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationException):
    """验证异常处理器"""
    logger.warning(f"验证失败: {exc.message} - URL: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # 统一返回200
        content={
            "code": 400,
            "message": exc.message,
            "data": None
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail} - URL: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # 统一返回200
        content={
            "code": exc.status_code,
            "message": str(exc.detail),
            "data": None
        }
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    """请求验证错误处理器"""
    errors = exc.errors()
    error_messages = []
    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"])
        error_messages.append(f"{field}: {error['msg']}")

    logger.warning(f"请求参数验证失败: {'; '.join(error_messages)} - URL: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # 统一返回200
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "data": {"errors": error_messages}
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """数据库异常处理器"""
    logger.error(f"数据库异常: {str(exc)} - URL: {request.url}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # 统一返回200
        content={
            "code": 500,
            "message": "数据库操作失败",
            "data": None
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器（捕获所有未处理的异常）"""
    logger.error(f"系统异常: {str(exc)} - URL: {request.url}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # 统一返回200
        content={
            "code": 500,
            "message": "系统异常，请稍后重试",
            "data": None
        }
    )
