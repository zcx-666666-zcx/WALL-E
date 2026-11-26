"""
REST + WebSocket API 服务（预留前端接口）
────────────────────────────────────────────────────────────────
端点：
  GET  /health                → 健康检查（含活体检测状态）
  GET  /personas              → 获取所有人设
  POST /personas              → 创建自定义人设
  GET  /personas/{id}         → 获取单个人设
  PUT  /personas/{id}         → 更新人设内容

  POST /chat/send             → 普通对话（完整返回）
  POST /chat/stream           → SSE 流式对话
  WS   /ws/{user_id}         → WebSocket 实时对话

  POST /user/init_wali        → 注册时初始化专属瓦利
  POST /user/bind_persona     → 绑定人设
  GET  /user/{user_id}/persona → 查询绑定的人设

  GET  /memory/{user_id}      → 获取用户记忆
  PUT  /memory/{user_id}      → 更新用户信息
  GET  /memory/{user_id}/stats → 情感趋势统计

  POST /stt                   → 语音转文字（SenseVoice）
  POST /input                 → 统一输入（意图识别 + 对话）
  POST /face/liveness         → 面部活体检测
  GET  /face/health           → 活体检测模块状态

启动：
  python -m api.server
  uvicorn api.server:app --host 0.0.0.0 --port 6006
"""

from __future__ import annotations
import json
import asyncio
from typing import Optional, AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi import UploadFile, File
import shutil, time, os, re

_stt_model = None
_engine = None
_pm = None
_emotion_detector = None
_liveness_detector = None
_tts_engine = None

def get_engine():
    global _engine
    if _engine is None:
        from core.engine import DialogueEngine
        _engine = DialogueEngine()
        _engine.load()
    return _engine

def get_pm():
    global _pm
    if _pm is None:
        from personas.persona_manager import PersonaManager
        _pm = PersonaManager()
    return _pm

def get_emotion():
    global _emotion_detector
    if _emotion_detector is None:
        from core.emotion import EmotionDetector
        _emotion_detector = EmotionDetector()
    return _emotion_detector

def get_liveness():
    global _liveness_detector
    if _liveness_detector is None:
        from core.liveness import LivenessDetector
        _liveness_detector = LivenessDetector()
    return _liveness_detector

def get_tts():
    global _tts_engine
    if _tts_engine is None:
        from core.tts import GTSTTSEngine
        _tts_engine = GTSTTSEngine()
    return _tts_engine

# ════════════════════════════════════════════
# FastAPI App
# ════════════════════════════════════════════

app = FastAPI(
    title="Elder AI API",
    description="适老化情感陪伴 AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

from config.settings import TTS_OUTPUT_DIR
TTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(TTS_OUTPUT_DIR)), name="audio")

_sessions: dict[str, dict] = {}

def get_session(user_id: str, persona_id: str = None) -> dict:
    from memory.user_memory import UserMemory
    if user_id not in _sessions:
        if persona_id is None:
            memory = UserMemory(user_id)
            persona_id = memory.get_persona_id()
        _sessions[user_id] = {"history": [], "persona_id": persona_id}
    elif persona_id is not None:
        _sessions[user_id]["persona_id"] = persona_id
    return _sessions[user_id]

# ════════════════════════════════════════════
# STT语音识别
# ════════════════════════════════════════════

def get_stt_model():
    global _stt_model
    if _stt_model is None:
        from funasr import AutoModel
        print(">>> 正在加载 SenseVoice 模型...")
        _stt_model = AutoModel(
            model="iic/SenseVoiceSmall",
            device="cuda",
            disable_update=True
        )
        print(">>> SenseVoice 加载完毕")
    return _stt_model

@app.post("/stt")
async def speech_to_text(audio_file: UploadFile = File(...)):
    start = time.time()
    temp_path = f"/tmp/stt_{int(time.time()*1000)}.wav"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(audio_file.file, f)
    try:
        res = get_stt_model().generate(
            input=temp_path, cache={},
            language="auto", use_itn=True
        )
        raw = res[0]["text"]
        clean = re.sub(r"<\|.*?\|>", "", raw).strip()
        return {"text": clean, "cost": round(time.time() - start, 3)}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ════════════════════════════════════════════
# 数据模型
# ════════════════════════════════════════════

class ChatRequest(BaseModel):
    user_id: str
    message: str
    persona_id: Optional[str] = None

class BindPersonaRequest(BaseModel):
    user_id: str
    persona_id: str

class PersonaCreateRequest(BaseModel):
    persona_id: str
    name: str
    age: int
    persona_desc: str = ""
    background: str = ""
    personality: str = ""
    speaking_style: str = ""
    catchphrases: list[str] = []
    topics_of_interest: list[str] = []
    taboo_topics: list[str] = []
    emotion_tendency: str = "温和积极"

class PersonaUpdateRequest(BaseModel):
    persona_desc:       Optional[str]       = None   # 统一人设描述
    background:         Optional[str]       = None
    personality:        Optional[str]       = None
    speaking_style:     Optional[str]       = None
    catchphrases:       Optional[list[str]] = None
    topics_of_interest: Optional[list[str]] = None
    taboo_topics:       Optional[list[str]] = None
    emotion_tendency:   Optional[str]       = None

class MemoryUpdateRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    interests: Optional[list[str]] = None
    health_notes: Optional[list[str]] = None


# ════════════════════════════════════════════
# 健康检查
# ════════════════════════════════════════════

@app.get("/health")
def health():
    detector = get_liveness()
    return {
        "status": "ok",
        "service": "Elder AI",
        "liveness": "ready" if detector._ready else f"no_model: {detector._error[:80]}",
    }


# ════════════════════════════════════════════
# 面部活体检测接口
# ════════════════════════════════════════════

@app.get("/face/health")
def face_health():
    detector = get_liveness()
    return {
        "ready": detector._ready,
        "error": detector._error or None,
    }


@app.post("/face/liveness")
async def face_liveness(image: UploadFile = File(...)):
    image_bytes = await image.read()
    detector = get_liveness()
    result = detector.predict(image_bytes)
    return result.to_dict()


# ════════════════════════════════════════════
# 人设接口
# ════════════════════════════════════════════

@app.get("/personas")
def list_personas():
    return {"personas": get_pm().list_all()}

@app.get("/personas/{persona_id}")
def get_persona(persona_id: str):
    try:
        p = get_pm().get(persona_id)
        return {
            "id":                 p.id,
            "name":               p.name,
            "age":                p.age,
            "persona_desc":       p.persona_desc,   # 新字段，前端 getStyle 用这个
            "background":         p.background,
            "personality":        p.personality,
            "speaking_style":     p.speaking_style,
            "topics_of_interest": p.topics_of_interest,
            "type": "built_in" if p.is_builtin else "custom",
        }
    except ValueError as e:
        raise HTTPException(404, str(e))

@app.post("/personas")
def create_persona(req: PersonaCreateRequest):
    try:
        p = get_pm().create(
            persona_id=req.persona_id,
            name=req.name,
            age=req.age,
            persona_desc=req.persona_desc,
            background=req.background,
            personality=req.personality,
            speaking_style=req.speaking_style,
            catchphrases=req.catchphrases,
            topics_of_interest=req.topics_of_interest,
            taboo_topics=req.taboo_topics,
            emotion_tendency=req.emotion_tendency,
        )
        return {"message": f"人设 {p.name} 创建成功", "persona_id": p.id}
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.delete("/personas/{persona_id}")
def delete_persona(persona_id: str):
    try:
        get_pm().delete(persona_id)
        return {"message": f"人设 {persona_id} 已删除"}
    except (ValueError, KeyError) as e:
        raise HTTPException(400, str(e))

@app.put("/personas/{persona_id}")
def update_persona(persona_id: str, req: PersonaUpdateRequest):
    """更新人设内容，只覆盖传入的字段，不新建。"""
    try:
        upd = {k: v for k, v in req.model_dump().items() if v is not None}
        p = get_pm().update(persona_id, **upd)
        return {"message": f"人设【{p.name}】已更新", "persona_id": p.id}
    except KeyError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


# ════════════════════════════════════════════
# 用户初始化 & 人设绑定
# ════════════════════════════════════════════

@app.post("/user/init_wali")
def init_wali(user_id: str):
    """
    注册时调用：为新用户创建专属瓦利并绑定。
    已存在则跳过创建，只确保绑定关系正确。
    """
    from memory.user_memory import UserMemory

    persona_id = f"wali_{user_id}"

    try:
        get_pm().get(persona_id)
    except ValueError:
        # 用 persona_desc 统一存储，不拆字段
        get_pm().create(
            persona_id=persona_id,
            name="瓦利",
            age=20,
            persona_desc=(
                "专门与老人对话陪伴老人的小伙伴，是一个智能AI，全名瓦利，一般叫做小瓦。\n"
                "性格：活泼开朗，思维活跃，感情细腻，不喜欢说太多话，说话风格比较简练，一般不会以疑问句结尾。\n"
                "说话风格：较少使用语气词，回复相对简短，但在老人遇到烦心事时候会很热情。"
            ),
        )

    memory = UserMemory(user_id)
    memory.set_persona_id(persona_id)

    return {
        "message": f"用户 {user_id} 的专属瓦利已就绪",
        "user_id": user_id,
        "persona_id": persona_id,
    }

@app.post("/user/bind_persona")
def bind_persona(req: BindPersonaRequest):
    """给用户绑定专属人设"""
    from memory.user_memory import UserMemory
    try:
        get_pm().get(req.persona_id)
    except ValueError:
        raise HTTPException(404, f"人设 '{req.persona_id}' 不存在")

    memory = UserMemory(req.user_id)
    memory.set_persona_id(req.persona_id)

    if req.user_id in _sessions:
        _sessions[req.user_id]["persona_id"] = req.persona_id
        _sessions[req.user_id]["history"] = []

    persona = get_pm().get(req.persona_id)
    return {
        "message": f"用户 {req.user_id} 已绑定人设【{persona.name}】",
        "user_id": req.user_id,
        "persona_id": req.persona_id,
        "persona_name": persona.name,
    }

@app.get("/user/{user_id}/persona")
def get_user_persona(user_id: str):
    """查询用户当前绑定的人设"""
    from memory.user_memory import UserMemory
    memory = UserMemory(user_id)
    persona_id = memory.get_persona_id()
    try:
        persona = get_pm().get(persona_id)
        return {
            "user_id":      user_id,
            "persona_id":   persona_id,
            "persona_name": persona.name,
            "persona_age":  persona.age,
        }
    except ValueError:
        return {
            "user_id":      user_id,
            "persona_id":   "grandma_chen",
            "persona_name": "陈奶奶（默认）",
            "persona_age":  72,
        }


# ════════════════════════════════════════════
# 对话接口
# ════════════════════════════════════════════

@app.post("/chat/send")
def chat_send(req: ChatRequest):
    """普通对话，不传 persona_id 则自动使用用户绑定的人设。"""
    from memory.user_memory import UserMemory
    memory = UserMemory(req.user_id)

    persona_id = req.persona_id or memory.get_persona_id()
    session = get_session(req.user_id, persona_id)
    persona = get_pm().get(persona_id)
    emotion = get_emotion().detect(req.message)

    reply = get_engine().generate(
        persona=persona,
        history=session["history"][-30:],
        user_input=req.message,
        memory=memory,
        emotion=emotion,
    )

    session["history"].append({"role": "user", "content": req.message})
    session["history"].append({"role": "assistant", "content": reply})
    memory.update_emotion(emotion.emotion, emotion.confidence)
    memory.increment_chat()

    return {
        "reply":      reply,
        "emotion":    {"label": emotion.emotion, "confidence": emotion.confidence},
        "user_id":    req.user_id,
        "persona_id": persona_id,
    }


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """SSE 流式对话，不传 persona_id 则自动使用用户绑定的人设。"""
    from memory.user_memory import UserMemory

    memory = UserMemory(req.user_id)
    persona_id = req.persona_id or memory.get_persona_id()
    session = get_session(req.user_id, persona_id)
    persona = get_pm().get(persona_id)
    emotion = get_emotion().detect(req.message)

    async def event_gen() -> AsyncGenerator[str, None]:
        full_reply = ""
        for chunk in get_engine().stream(
            persona=persona,
            history=session["history"][-30:],
            user_input=req.message,
            memory=memory,
            emotion=emotion,
        ):
            full_reply += chunk
            data = json.dumps({"chunk": chunk}, ensure_ascii=False)
            yield f"data: {data}\n\n"
            await asyncio.sleep(0)

        yield f"data: {json.dumps({'done': True, 'emotion': emotion.emotion})}\n\n"

        session["history"].append({"role": "user", "content": req.message})
        session["history"].append({"role": "assistant", "content": full_reply})
        memory.update_emotion(emotion.emotion, emotion.confidence)
        memory.increment_chat()

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.websocket("/ws/{user_id}")
async def ws_chat(websocket: WebSocket, user_id: str):
    """WebSocket 实时对话。"""
    from memory.user_memory import UserMemory

    await websocket.accept()
    memory = UserMemory(user_id)

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            text = msg.get("text", "")
            persona_id = msg.get("persona_id") or memory.get_persona_id()

            session = get_session(user_id, persona_id)
            persona = get_pm().get(persona_id)
            emotion = get_emotion().detect(text)

            full_reply = ""
            for chunk in get_engine().stream(
                persona=persona,
                history=session["history"][-30:],
                user_input=text,
                memory=memory,
                emotion=emotion,
            ):
                full_reply += chunk
                await websocket.send_text(json.dumps({"type": "chunk", "content": chunk}))

            await websocket.send_text(json.dumps({
                "type":    "done",
                "emotion": emotion.emotion,
            }))

            session["history"].append({"role": "user", "content": text})
            session["history"].append({"role": "assistant", "content": full_reply})
            memory.update_emotion(emotion.emotion, emotion.confidence)
            memory.increment_chat()

    except WebSocketDisconnect:
        memory.save()


@app.post("/chat/clear")
def chat_clear(req: dict):
    """清空指定用户的对话历史"""
    user_id = req.get("user_id", "")
    if user_id in _sessions:
        _sessions[user_id]["history"] = []
    return {"message": "对话历史已清空", "user_id": user_id}


# ════════════════════════════════════════════
# 意图识别 + 统一入口
# ════════════════════════════════════════════

class InputRequest(BaseModel):
    user_id: str
    text: str                        # 语音转文字后的文本

@app.post("/input")
async def unified_input(req: InputRequest):
    """
    统一输入入口（硬件端调这一个接口即可）

    流程：
      文本 → 意图识别
        ├─ 是指令（1-6）→ 直接返回指令编号，不进对话
        └─ 是对话（0）  → 走对话流程，返回 AI 回复

    返回格式：
      指令：{"type": "command", "command": 1, "label": "前进"}
      对话：{"type": "chat",    "reply": "...", "emotion": "..."}
    """
    from core.intent import recognize_intent, INTENT_LABELS

    intent = recognize_intent(req.text)

    # ── 是指令，直接返回 ──────────────────────
    if intent != 0:
        print(f"[意图] 指令识别：{req.text!r} → {INTENT_LABELS[intent]}({intent})")
        return {
            "type":    "command",
            "command": intent,
            "label":   INTENT_LABELS[intent],
            "reply":   "",
        }

    # ── 是对话，走对话流程 ───────────────────
    print(f"[意图] 对话识别：{req.text!r}")
    from memory.user_memory import UserMemory

    memory = UserMemory(req.user_id)
    persona_id = memory.get_persona_id()
    session = get_session(req.user_id, persona_id)
    persona = get_pm().get(persona_id)
    emotion = get_emotion().detect(req.text)

    reply = get_engine().generate(
        persona=persona,
        history=session["history"][-30:],
        user_input=req.text,
        memory=memory,
        emotion=emotion,
    )

    session["history"].append({"role": "user",      "content": req.text})
    session["history"].append({"role": "assistant",  "content": reply})
    memory.update_emotion(emotion.emotion, emotion.confidence)
    memory.increment_chat()

    # ── TTS 语音合成 ───────────────────────
    audio_url = ""
    try:
        wav_path = get_tts().synthesize_to_file(
            text=reply,
            persona_id=persona_id,
        )
        if wav_path:
            audio_url = f"/audio/{os.path.basename(wav_path)}"
    except Exception as e:
        print(f"[TTS] 合成失败，降级为纯文本：{e}")

    return {
        "type":     "chat",
        "command":  0,
        "label":    "对话",
        "reply":    reply,
        "emotion":  emotion.emotion,
        "audio_url": audio_url,
    }


# ════════════════════════════════════════════
# 记忆接口
# ════════════════════════════════════════════

@app.get("/memory/{user_id}")
def get_memory(user_id: str):
    from memory.user_memory import UserMemory
    m = UserMemory(user_id)
    return m.data

@app.put("/memory/{user_id}")
def update_memory(user_id: str, req: MemoryUpdateRequest):
    from memory.user_memory import UserMemory
    m = UserMemory(user_id)
    upd = {k: v for k, v in req.model_dump().items() if v is not None}
    m.update_profile(**upd)
    return {"message": "记忆已更新", "user_id": user_id}

@app.get("/memory/{user_id}/stats")
def memory_stats(user_id: str):
    from memory.user_memory import UserMemory
    m = UserMemory(user_id)
    return {
        "chat_count":    m.data["chat_count"],
        "persona_id":    m.get_persona_id(),
        "emotion_trend": m.emotion_trend(20),
        "last_topics":   m.data["last_topics"],
    }


# ════════════════════════════════════════════
# 启动入口
# ════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    from config.settings import API_HOST, API_PORT
    uvicorn.run("api.server_with_intent:app", host=API_HOST, port=API_PORT, reload=True)
