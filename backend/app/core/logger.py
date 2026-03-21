import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


# 创建日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class Logger:
    """日志配置类"""

    def __init__(self, name: str = "app"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # 避免重复添加handler
        if not self.logger.handlers:
            # 日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # 文件处理器 - 所有日志
            all_log_file = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = RotatingFileHandler(
                all_log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=10,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            # 文件处理器 - 错误日志
            error_log_file = LOG_DIR / f"error_{datetime.now().strftime('%Y%m%d')}.log"
            error_handler = RotatingFileHandler(
                error_log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=10,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            self.logger.addHandler(error_handler)

    def get_logger(self):
        return self.logger


# 创建全局logger实例
logger_instance = Logger()
logger = logger_instance.get_logger()


def get_logger(name: str = None):
    """获取logger实例"""
    if name:
        return logging.getLogger(name)
    return logger
