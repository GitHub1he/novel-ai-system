"""
迁移脚本：添加 display_summary 字段到 chapters 表

使用方法：
    python migrations/add_display_summary.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """添加 display_summary 字段"""
    db = SessionLocal()
    try:
        # 检查字段是否已存在
        check_sql = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'chapters'
            AND column_name = 'display_summary';
        """

        result = db.execute(text(check_sql)).fetchone()

        if result:
            logger.info("字段 display_summary 已存在，无需迁移")
            return

        # 添加字段
        add_column_sql = """
            ALTER TABLE chapters
            ADD COLUMN display_summary TEXT;
        """

        logger.info("开始添加 display_summary 字段...")
        db.execute(text(add_column_sql))
        db.commit()

        logger.info("成功添加 display_summary 字段")

        # 为现有记录生成 display_summary（可选）
        # 如果需要，可以在这里添加逻辑将 summary 复制到 display_summary

    except Exception as e:
        logger.error(f"迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
    logger.info("迁移完成")
