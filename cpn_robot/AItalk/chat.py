"""
对话 REST API 路由
提供：发送消息、获取历史、清空历史
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.conversation_manager import ConversationManager
from fastapi.responses import StreamingResponse
import json
import asyncio

router = APIRouter()
manager = ConversationManager()


class ChatRequest(BaseModel):
    user_id: str
    message: str
    persona_id: str = "grandma_chen"


class ClearRequest(BaseModel):
    user_id: str


@router.post("/send")
async def send_message(req: ChatRequest):
    """
    发送消息（非流式，完整返回）
    适合普通 HTTP 调用
    """
    full_response = ""
    async for chunk in manager.stream_response(
        user_id=req.user_id,
        user_message=req.message,
        persona_id=req.persona_id
    ):
        full_response += chunk
    
    return {
        "reply": full_response,
        "user_id": req.user_id,
        "persona_id": req.persona_id
    }


@router.post("/stream")
async def stream_message(req: ChatRequest):
    """
    发送消息（SSE 流式返回）
    适合 Vue 前端实时展示打字效果
    """
    async def event_generator():
        async for chunk in manager.stream_response(
            user_id=req.user_id,
            user_message=req.message,
            persona_id=req.persona_id
        ):
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/history/{user_id}")
async def get_history(user_id: str):
    """获取用户对话历史"""
    history = manager.get_history(user_id)
    return {"user_id": user_id, "history": history, "count": len(history)}


@router.post("/clear")
async def clear_history(req: ClearRequest):
    """清空对话历史（保留长期记忆）"""
    manager.clear_history(req.user_id)
    return {"message": "对话历史已清空", "user_id": req.user_id}
