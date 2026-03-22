#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员权限诊断和修复脚本

使用方法：
    python diagnose_admin.py
"""

import sys
import os
from pathlib import Path

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.project import Project


def diagnose_and_fix():
    """
    诊断并修复管理员权限问题
    """
    db: Session = SessionLocal()

    try:
        print("=" * 70)
        print("管理员权限诊断和修复")
        print("=" * 70)

        # 1. 检查 admin 用户
        print("\n[1] 检查 admin 用户...")
        admin_user = db.query(User).filter(User.username == "admin").first()

        if not admin_user:
            print("  ❌ admin 用户不存在")
            print("  → 正在创建 admin 用户...")

            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_admin=1,
                is_active=1
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            print(f"  ✅ admin 用户创建成功 (ID: {admin_user.id})")
        else:
            print(f"  ✓ admin 用户存在 (ID: {admin_user.id})")

            # 检查 is_admin 状态
            if admin_user.is_admin != 1:
                print(f"  ⚠️  admin 用户的 is_admin = {admin_user.is_admin} (应该为 1)")
                print("  → 正在修复...")
                admin_user.is_admin = 1
                db.commit()
                print("  ✅ 已修复: is_admin 设置为 1")
            else:
                print(f"  ✓ admin 用户的 is_admin = 1 (正确)")

        # 2. 检查 testuser 用户
        print("\n[2] 检查 testuser 用户...")
        test_user = db.query(User).filter(User.username == "testuser").first()

        if not test_user:
            print("  ⚠️  testuser 用户不存在")
            print("  → 正在创建 testuser 用户...")

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
            db.refresh(test_user)

            print(f"  ✅ testuser 用户创建成功 (ID: {test_user.id})")
        else:
            print(f"  ✓ testuser 用户存在 (ID: {test_user.id})")

        # 3. 创建测试项目（如果不存在）
        print("\n[3] 创建测试项目...")

        # testuser 的项目
        testuser_projects = db.query(Project).filter(Project.user_id == test_user.id).all()
        if not testuser_projects:
            print("  → 正在为 testuser 创建测试项目...")
            project1 = Project(
                user_id=test_user.id,
                title="测试用户的项目1",
                author="测试作者",
                genre='["玄幻", "修真"]',
                summary="这是一个测试项目",
                target_readers="青少年",
                status="draft",
                default_pov="第一人称",
                style="轻松幽默",
                target_words_per_chapter=3000,
                tags='["热血", "冒险"]',
                total_words=0,
                total_chapters=0
            )
            db.add(project1)
            db.commit()
            print(f"  ✅ 为 testuser 创建项目成功 (ID: {project1.id})")
        else:
            print(f"  ✓ testuser 已有 {len(testuser_projects)} 个项目")

        # admin 的项目
        admin_projects = db.query(Project).filter(Project.user_id == admin_user.id).all()
        if not admin_projects:
            print("  → 正在为 admin 创建测试项目...")
            project2 = Project(
                user_id=admin_user.id,
                title="管理员的项目",
                author="管理员",
                genre='["科幻", "未来"]',
                summary="这是管理员创建的项目",
                target_readers="成年人",
                status="writing",
                default_pov="第三人称",
                style="严肃深刻",
                target_words_per_chapter=5000,
                tags='["思考", "哲学"]',
                total_words=0,
                total_chapters=0
            )
            db.add(project2)
            db.commit()
            print(f"  ✅ 为 admin 创建项目成功 (ID: {project2.id})")
        else:
            print(f"  ✓ admin 已有 {len(admin_projects)} 个项目")

        # 4. 显示所有用户和项目统计
        print("\n[4] 数据库统计...")
        all_users = db.query(User).all()
        all_projects = db.query(Project).all()

        print(f"\n  所有用户 ({len(all_users)} 个):")
        for user in all_users:
            role = "管理员" if user.is_admin else "普通用户"
            project_count = len([p for p in all_projects if p.user_id == user.id])
            print(f"    - {user.username} (ID: {user.id}, {role}, {project_count} 个项目)")

        print(f"\n  所有项目 ({len(all_projects)} 个):")
        for project in all_projects:
            owner = db.query(User).filter(User.id == project.user_id).first()
            owner_name = owner.username if owner else "未知"
            print(f"    - {project.title} (ID: {project.id}, 所有者: {owner_name})")

        # 5. 测试权限检查
        print("\n[5] 测试权限检查...")
        print(f"  admin.is_admin = {admin_user.is_admin}")
        print(f"  testuser.is_admin = {test_user.is_admin}")

        if admin_user.is_admin == 1:
            print("  ✅ admin 用户权限正确")
        else:
            print("  ❌ admin 用户权限错误！")

        # 6. 打印测试建议
        print("\n" + "=" * 70)
        print("诊断完成！")
        print("=" * 70)
        print("\n📝 测试账号：")
        print(f"   管理员: admin / admin123 (ID: {admin_user.id})")
        print(f"   普通用户: testuser / password123 (ID: {test_user.id})")
        print(f"\n📊 项目统计:")
        print(f"   总用户数: {len(all_users)}")
        print(f"   总项目数: {len(all_projects)}")
        print(f"   testuser 项目数: {len([p for p in all_projects if p.user_id == test_user.id])}")
        print(f"   admin 项目数: {len([p for p in all_projects if p.user_id == admin_user.id])}")

        print("\n🔍 测试步骤：")
        print("   1. 使用 admin 账号登录")
        print("   2. 查看 Dashboard，应该能看到所有项目（包括 testuser 的项目）")
        print("   3. 点击 testuser 的项目，应该能查看和编辑")
        print("   4. 退出登录")
        print("   5. 使用 testuser 账号登录")
        print("   6. 查看 Dashboard，应该只能看到自己的项目")
        print("   7. 尝试访问 admin 的项目（应该显示无权限）")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    diagnose_and_fix()
