#!/usr/bin/env python3
"""
简单的WebSocket测试脚本
"""
import asyncio
import websockets
import json
import uuid

async def test_websocket():
    # 生成测试task_id
    task_id = str(uuid.uuid4())
    uri = f"ws://localhost:8000/ws/chapters/generate/{task_id}"

    try:
        print(f"正在连接到: {uri}")

        # 创建WebSocket连接
        async with websockets.connect(uri) as websocket:
            print("WebSocket连接成功！")

            # 发送测试消息
            test_message = {"type": "ping", "data": "Hello Server"}
            await websocket.send(json.dumps(test_message))
            print(f"发送测试消息: {test_message}")

            # 等待响应
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"收到响应: {response}")

            # 保持连接一段时间
            print("等待5秒...")
            await asyncio.sleep(5)

    except websockets.ConnectionClosed:
        print("WebSocket连接已关闭")
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
    finally:
        print("WebSocket测试完成")

if __name__ == "__main__":
    asyncio.run(test_websocket())