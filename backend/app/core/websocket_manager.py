from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json
import logging

logger = logging.getLogger(__name__)

# WebSocket连接管理
active_websockets: Dict[str, WebSocket] = {}


async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket端点，用于推送章节生成进度"""
    await websocket.accept()
    active_websockets[task_id] = websocket
    logger.info(f"WebSocket连接建立: {task_id}")

    try:
        # 保持连接活跃
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开: {task_id}")
        if task_id in active_websockets:
            del active_websockets[task_id]


async def send_websocket_message(task_id: str, event: str, data: dict):
    """发送WebSocket消息"""
    if task_id in active_websockets:
        try:
            message = {
                "event": event,
                "data": data
            }
            await active_websockets[task_id].send_text(json.dumps(message))
            logger.info(f"发送WebSocket消息: {task_id} - {event}")
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {task_id} - {str(e)}")
            # 如果发送失败，清理连接
            if task_id in active_websockets:
                del active_websockets[task_id]