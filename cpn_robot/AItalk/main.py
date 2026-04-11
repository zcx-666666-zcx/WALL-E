"""
Elder AI - 老年人情感陪护系统
主入口：FastAPI 后端服务
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
import asyncio
from api.chat import router as chat_router
from api.persona import router as persona_router
from models.conversation_manager import ConversationManager

app = FastAPI(
    title="Elder AI 情感陪护系统",
    description="基于 Transformer 的老年人情感陪护 AI",
    version="1.0.0"
)

# 跨域配置（对接 Vue 前端）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router, prefix="/api/chat", tags=["对话"])
app.include_router(persona_router, prefix="/api/persona", tags=["人设"])

# WebSocket 连接管理
conversation_manager = ConversationManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket 实时对话接口
    支持流式输出，让老人感受到"AI在思考"的自然节奏
    """
    await websocket.accept()
    print(f"[连接] 用户 {user_id} 已连接")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 流式回复（逐字输出，更自然）
            async for chunk in conversation_manager.stream_response(
                user_id=user_id,
                user_message=message.get("text", ""),
                persona_id=message.get("persona_id", "grandma_chen")
            ):
                await websocket.send_text(json.dumps({
                    "type": "chunk",
                    "content": chunk
                }))
            
            # 回复结束信号
            await websocket.send_text(json.dumps({"type": "done"}))
            
    except WebSocketDisconnect:
        print(f"[断开] 用户 {user_id} 已断开连接")
        conversation_manager.cleanup_user(user_id)

@app.get("/")
async def root():
    return {"message": "Elder AI 服务运行中 🌸", "status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
