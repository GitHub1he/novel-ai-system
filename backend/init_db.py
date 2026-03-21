"""
数据库初始化脚本
创建默认测试用户
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash


def init_db():
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表已创建")

    # 创建数据库会话
    db: Session = SessionLocal()

    try:
        # 检查是否已有用户
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("! 测试用户已存在，跳过创建")
            return

        # 创建默认测试用户
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            phone="13800138000",
            preferred_genre="玄幻",
            is_admin=0,
            is_active=1
        )

        db.add(test_user)
        db.commit()
        print("✓ 默认测试用户已创建")
        print("  邮箱: test@example.com")
        print("  用户名: testuser")
        print("  密码: password123")
        print("  用户ID: 1")

    except Exception as e:
        print(f"✗ 创建用户失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("开始初始化数据库...")
    init_db()
    print("初始化完成！")
