"""
对话管理器：维护每个用户的对话历史、人设状态、情感轨迹
"""

from typing import AsyncGenerator, Dict
from models.ai_model import ElderAIModel, UserMemory
import asyncio


# 全局单例模型（避免重复加载）
_model_instance = None

def get_model() -> ElderAIModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = ElderAIModel()
        # 生产环境取消注释下面这行以加载真实模型：
        # _model_instance.initialize(use_quantization=True)
    return _model_instance


class ConversationManager:
    """管理所有用户的对话会话"""
    
    MAX_HISTORY = 20  # 保留最近20轮对话
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}  # {user_id: {history, persona_id}}
        self.memories: Dict[str, UserMemory] = {}
        self.model = get_model()
    
    def _get_session(self, user_id: str, persona_id: str) -> dict:
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "history": [],
                "persona_id": persona_id
            }
        else:
            self.sessions[user_id]["persona_id"] = persona_id
        return self.sessions[user_id]
    
    def _get_memory(self, user_id: str) -> UserMemory:
        if user_id not in self.memories:
            self.memories[user_id] = UserMemory(user_id)
        return self.memories[user_id]
    
    async def stream_response(
        self,
        user_id: str,
        user_message: str,
        persona_id: str = "grandma_chen"
    ) -> AsyncGenerator[str, None]:
        """处理用户消息，流式返回 AI 回复"""
        
        session = self._get_session(user_id, persona_id)
        memory = self._get_memory(user_id)
        
        # 添加用户消息到历史
        session["history"].append({
            "role": "user",
            "content": user_message
        })
        
        # 维护历史长度
        if len(session["history"]) > self.MAX_HISTORY * 2:
            session["history"] = session["history"][-self.MAX_HISTORY * 2:]
        
        # 流式生成
        full_response = ""
        async for chunk in self.model.stream_generate(
            messages=session["history"],
            persona_id=persona_id,
            user_memory=memory
        ):
            full_response += chunk
            yield chunk
        
        # 保存 AI 回复到历史
        session["history"].append({
            "role": "assistant",
            "content": full_response
        })
        
        # 更新对话计数
        memory.memory["conversation_count"] += 1
        memory.save()
    
    def get_history(self, user_id: str) -> list:
        return self.sessions.get(user_id, {}).get("history", [])
    
    def clear_history(self, user_id: str):
        if user_id in self.sessions:
            self.sessions[user_id]["history"] = []
    
    def cleanup_user(self, user_id: str):
        """用户断开连接时清理内存中的会话（记忆已持久化）"""
        self.sessions.pop(user_id, None)
        self.memories.pop(user_id, None)
