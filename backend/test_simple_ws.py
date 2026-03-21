#!/usr/bin/env python3
"""
简单WebSocket连接测试
"""
import asyncio
import websockets

async def test_simple_ws():
    uri = "ws://localhost:8000/ws/chapters/generate/test123"

    try:
        print(f"连接到: {uri}")
        websocket = await websockets.connect(uri)
        print("连接成功！")

        # 发送一条消息
        await websocket.send('{"type": "test", "message": "Hello"}')

        # 接收响应
        response = await websocket.recv()
        print(f"收到响应: {response}")

        # 关闭连接
        await websocket.close()
        print("连接已关闭")

    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_simple_ws())