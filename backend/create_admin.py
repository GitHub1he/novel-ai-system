#!/usr/bin/env python3
"""
初始化管理员账号脚本

使用方法：
    python create_admin.py --username admin --email admin@example.com --password admin123
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.core.logger import logger


def create_admin_user(username: str, email: str, password: str) -> User:
    """
    创建管理员用户

    Args:
        username: 用户名
        email: 邮箱
        password: 密码

    Returns:
        创建的User对象
    """
    db: Session = SessionLocal()

    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            logger.warning(f"用户名 {username} 已存在")
            # 如果已存在，将其设置为管理员
            existing_user.is_admin = 1
            db.commit()
            logger.info(f"已将用户 {username} 设置为管理员")
            return existing_user

        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            logger.warning(f"邮箱 {email} 已被使用")
            # 如果已存在，将其设置为管理员
            existing_email.is_admin = 1
            db.commit()
            logger.info(f"已将用户 {email} 设置为管理员")
            return existing_email

        # 创建新的管理员用户
        admin_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_admin=1,
            is_active=1
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        logger.info(f"管理员账号创建成功: {username} (ID: {admin_user.id})")

        return admin_user

    except Exception as e:
        db.rollback()
        logger.error(f"创建管理员失败: {str(e)}")
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="创建管理员账号")
    parser.add_argument("--username", "-u", default="admin", help="管理员用户名 (默认: admin)")
    parser.add_argument("--email", "-e", default="admin@example.com", help="管理员邮箱 (默认: admin@example.com)")
    parser.add_argument("--password", "-p", default="admin123", help="管理员密码 (默认: admin123)")

    args = parser.parse_args()

    print("=" * 60)
    print("创建管理员账号")
    print("=" * 60)
    print(f"用户名: {args.username}")
    print(f"邮箱: {args.email}")
    print(f"密码: {args.password}")
    print("=" * 60)

    try:
        admin_user = create_admin_user(args.username, args.email, args.password)
        print(f"\n✅ 管理员账号创建成功！")
        print(f"   用户ID: {admin_user.id}")
        print(f"   用户名: {admin_user.username}")
        print(f"   邮箱: {admin_user.email}")
        print(f"\n⚠️  请妥善保管登录凭证！")
        print(f"   登录地址: http://localhost:5173/login")
    except Exception as e:
        print(f"\n❌ 创建失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
