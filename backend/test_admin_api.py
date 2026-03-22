#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试管理员 API 调用
模拟完整的登录和查询流程
"""

import sys
import os
import requests
import json

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "http://localhost:8000/api"

def test_admin_api():
    """测试管理员 API 调用"""

    print("=" * 70)
    print("管理员 API 测试")
    print("=" * 70)

    # 1. 管理员登录
    print("\n[1] 管理员登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        response.raise_for_status()

        token_data = response.json()
        access_token = token_data["access_token"]

        print(f"  ✅ 登录成功")
        print(f"  Token: {access_token[:50]}...")

        # 解码 JWT token 查看内容
        import base64
        import json

        # 解码 JWT payload
        payload_b64 = access_token.split('.')[1]
        # 添加 padding
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload_json = base64.b64decode(payload_b64)
        payload = json.loads(payload_json)

        print(f"\n  JWT Payload:")
        print(f"    sub: {payload.get('sub')}")
        print(f"    is_admin: {payload.get('is_admin')}")

        # 2. 获取项目列表
        print("\n[2] 获取项目列表...")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(f"{BASE_URL}/projects/list", headers=headers)
        response.raise_for_status()

        result = response.json()

        print(f"  响应状态码: {response.status_code}")
        print(f"  业务状态码: {result.get('code')}")
        print(f"  消息: {result.get('message')}")

        if result.get('code') == 200:
            projects = result.get('data', {}).get('projects', [])
            total = result.get('data', {}).get('total', 0)

            print(f"\n  ✅ 查询成功")
            print(f"  项目总数: {total}")
            print(f"\n  项目列表:")
            for p in projects:
                print(f"    - {p.get('title')} (ID: {p.get('id')}, user_id: {p.get('user_id')})")

            # 检查是否包含了所有项目
            if total == 6:
                print(f"\n  ✅✅✅ 完美！管理员能看到所有 6 个项目")
            else:
                print(f"\n  ❌ 错误！应该有 6 个项目，但只返回了 {total} 个")
        else:
            print(f"  ❌ API 返回错误: {result.get('message')}")

        # 3. 获取当前用户信息（测试 get_current_user）
        print("\n[3] 测试 get_current_user...")
        # 这个可以通过任何需要认证的接口来测试

        # 4. 对比普通用户
        print("\n[4] 测试普通用户登录...")
        login_data2 = {
            "username": "testuser",
            "password": "password123"
        }

        response = requests.post(f"{BASE_URL}/auth/login", json=login_data2)
        response.raise_for_status()

        token_data2 = response.json()
        access_token2 = token_data2["access_token"]

        # 解码 JWT
        payload_b642 = access_token2.split('.')[1]
        payload_b642 += '=' * (4 - len(payload_b642) % 4)
        payload_json2 = base64.b64decode(payload_b642)
        payload2 = json.loads(payload_json2)

        print(f"  testuser JWT Payload:")
        print(f"    sub: {payload2.get('sub')}")
        print(f"    is_admin: {payload2.get('is_admin')}")

        # 获取项目列表
        headers2 = {
            "Authorization": f"Bearer {access_token2}",
            "Content-Type": "application/json"
        }

        response = requests.get(f"{BASE_URL}/projects/list", headers=headers2)
        response.raise_for_status()

        result2 = response.json()
        projects2 = result2.get('data', {}).get('projects', [])
        total2 = result2.get('data', {}).get('total', 0)

        print(f"\n  testuser 能看到的项目数: {total2}")

        if total2 == 5:
            print(f"  ✅ 正确！普通用户只能看到自己的 5 个项目")
        else:
            print(f"  ❌ 错误！普通用户应该只能看到 5 个项目，但看到了 {total2} 个")

    except requests.exceptions.RequestException as e:
        print(f"\n  ❌ 请求失败: {e}")
        print(f"\n  请确保后端服务已启动：cd backend && python main.py")
    except Exception as e:
        print(f"\n  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

if __name__ == "__main__":
    test_admin_api()
