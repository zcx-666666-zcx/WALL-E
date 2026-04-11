"""
人设管理 API
支持：查询内置人设、创建自定义人设、更新人设配置
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from models.ai_model import PersonaConfig
import json
from pathlib import Path

router = APIRouter()
CUSTOM_PERSONA_PATH = Path("./data/custom_personas.json")


def load_custom_personas() -> dict:
    if CUSTOM_PERSONA_PATH.exists():
        return json.loads(CUSTOM_PERSONA_PATH.read_text(encoding="utf-8"))
    return {}


def save_custom_personas(personas: dict):
    CUSTOM_PERSONA_PATH.parent.mkdir(parents=True, exist_ok=True)
    CUSTOM_PERSONA_PATH.write_text(json.dumps(personas, ensure_ascii=False, indent=2), encoding="utf-8")


class CustomPersonaRequest(BaseModel):
    persona_id: str
    name: str
    personality: str              # 性格描述
    background: str               # 背景故事
    speaking_style: str           # 说话风格
    topics_of_interest: List[str] # 感兴趣的话题
    catchphrases: List[str] = []  # 口头禅


@router.get("/list")
async def list_personas():
    """列出所有可用人设（内置 + 自定义）"""
    built_in = [
        {
            "id": pid,
            "name": p["name"],
            "personality": p["personality"],
            "topics": p.get("topics_of_interest", []),
            "type": "built_in"
        }
        for pid, p in PersonaConfig.PERSONAS.items()
        if pid != "custom"
    ]
    
    custom = [
        {
            "id": pid,
            "name": p["name"],
            "personality": p["personality"],
            "topics": p.get("topics_of_interest", []),
            "type": "custom"
        }
        for pid, p in load_custom_personas().items()
    ]
    
    return {"personas": built_in + custom, "total": len(built_in) + len(custom)}


@router.get("/{persona_id}")
async def get_persona(persona_id: str):
    """获取单个人设详情"""
    # 先查内置
    if persona_id in PersonaConfig.PERSONAS:
        p = PersonaConfig.PERSONAS[persona_id]
        return {"id": persona_id, **p, "type": "built_in"}
    
    # 再查自定义
    customs = load_custom_personas()
    if persona_id in customs:
        return {"id": persona_id, **customs[persona_id], "type": "custom"}
    
    raise HTTPException(status_code=404, detail=f"人设 '{persona_id}' 不存在")


@router.post("/create")
async def create_persona(req: CustomPersonaRequest):
    """创建自定义人设"""
    customs = load_custom_personas()
    
    if req.persona_id in PersonaConfig.PERSONAS:
        raise HTTPException(status_code=400, detail="不能覆盖内置人设")
    
    # 自动生成 system prompt
    catchphrase_str = "，".join(req.catchphrases) if req.catchphrases else "嗯嗯、是啊"
    system_prompt = (
        f"你是{req.name}。{req.background}。"
        f"你的性格：{req.personality}。"
        f"说话风格：{req.speaking_style}。"
        f"你常说的口头禅有：{catchphrase_str}。"
        f"你对以下话题很感兴趣：{', '.join(req.topics_of_interest)}。"
        f"请用自然、亲切的方式回复，回复不超过100字。"
    )
    
    persona_data = {
        "name": req.name,
        "personality": req.personality,
        "system_prompt": system_prompt,
        "voice_style": req.speaking_style,
        "topics_of_interest": req.topics_of_interest,
        "catchphrases": req.catchphrases,
        "background": req.background,
    }
    
    customs[req.persona_id] = persona_data
    save_custom_personas(customs)
    
    return {"message": f"人设 '{req.name}' 创建成功", "persona_id": req.persona_id}


@router.delete("/{persona_id}")
async def delete_persona(persona_id: str):
    """删除自定义人设"""
    if persona_id in PersonaConfig.PERSONAS:
        raise HTTPException(status_code=400, detail="内置人设不可删除")
    
    customs = load_custom_personas()
    if persona_id not in customs:
        raise HTTPException(status_code=404, detail="人设不存在")
    
    del customs[persona_id]
    save_custom_personas(customs)
    return {"message": f"人设 '{persona_id}' 已删除"}
