from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/test/{task_id}")
async def websocket_test(websocket: WebSocket, task_id: str):
    await websocket.accept()
    print(f"WebSocket连接建立: {task_id}")

    try:
        # 保持连接活跃
        while True:
            data = await websocket.receive_text()
            print(f"收到消息: {data}")
            await websocket.send_text(json.dumps({"response": f"收到: {data}"}))
    except Exception as e:
        print(f"WebSocket断开: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("minimal_app:app", host="0.0.0.0", port=8000, reload=True)