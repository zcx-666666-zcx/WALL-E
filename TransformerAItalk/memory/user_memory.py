"""
用户记忆系统（User Memory）
────────────────────────────────────────────────────────────────
职责：
  · 持久化每个用户的画像、偏好、情感历史
  · 提炼"记忆摘要"注入 System Prompt，让 AI 越聊越懂老人
  · 自动更新聊天次数、最近话题、情感轨迹

文件存储：data/memory/{user_id}.json
"""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from config.settings import MEMORY_DIR


class UserMemory:
    """单用户的长期记忆，自动持久化"""

    DEFAULT = {
        "user_id": "",
        "persona_id": "瓦利",  # 该用户绑定的专属人设
        "name": "",
        "age": None,
        "location": "",
        "family_members": {},       # {"儿子": "小明", "孙女": "豆豆"}
        "health_notes": [],         # ["有轻度高血压", "膝盖不好"]
        "interests": [],            # ["下棋", "园艺"]
        "disliked_topics": [],      # 不喜欢聊的内容
        "important_dates": {},      # {"生日": "1952-03-15"}
        "emotion_log": [],          # [{ts, emotion, confidence}, ...]
        "last_topics": [],          # 最近聊过的话题
        "chat_count": 0,
        "created_at": "",
        "last_active": "",
    }

    def __init__(self, user_id: str):
        self.user_id = user_id
        self._path = MEMORY_DIR / f"{user_id}.json"
        self.data: dict = self._load()

    # ── 加载 / 保存 ──────────────────────────
    def _load(self) -> dict:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text(encoding="utf-8"))
            except Exception:
                pass
        d = dict(self.DEFAULT)
        d["user_id"] = self.user_id
        d["created_at"] = datetime.now().isoformat()
        return d

    def save(self):
        self.data["last_active"] = datetime.now().isoformat()
        self._path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # ── 更新接口 ─────────────────────────────
    # ── 人设绑定 ─────────────────────────────
    def get_persona_id(self) -> str:
        """获取该用户绑定的人设 ID"""
        return self.data.get("persona_id", "瓦利")

    def set_persona_id(self, persona_id: str):
        """绑定专属人设，持久化保存"""
        self.data["persona_id"] = persona_id
        self.save()

    def update_name(self, name: str):
        self.data["name"] = name
        self.save()

    def update_emotion(self, emotion: str, confidence: float):
        log = self.data["emotion_log"]
        log.append({
            "ts": datetime.now().isoformat(),
            "emotion": emotion,
            "confidence": round(confidence, 3)
        })
        self.data["emotion_log"] = log[-30:]   # 保留最近 30 条
        self.save()

    def add_topic(self, topic: str):
        topics = self.data["last_topics"]
        if topic not in topics:
            topics.insert(0, topic)
        self.data["last_topics"] = topics[:10]  # 最近 10 个话题

    def increment_chat(self):
        self.data["chat_count"] += 1
        self.save()

    def update_profile(self, **kwargs):
        """批量更新用户画像字段"""
        allowed = {"name", "age", "location", "family_members",
                   "health_notes", "interests", "disliked_topics", "important_dates"}
        for k, v in kwargs.items():
            if k in allowed:
                self.data[k] = v
        self.save()

    # ── 生成记忆摘要（注入 Prompt）────────────
    def context_summary(self) -> str:
        d = self.data
        parts = []

        if d.get("name"):
            parts.append(f"用户名字叫{d['name']}")
        if d.get("age"):
            parts.append(f"今年{d['age']}岁")
        if d.get("location"):
            parts.append(f"住在{d['location']}")
        if d.get("family_members"):
            fm = "、".join(f"{k}叫{v}" for k, v in d["family_members"].items())
            parts.append(f"家人：{fm}")
        if d.get("health_notes"):
            parts.append(f"健康情况：{'；'.join(d['health_notes'][-3:])}")
        if d.get("interests"):
            parts.append(f"兴趣爱好：{'、'.join(d['interests'])}")
        if d.get("last_topics"):
            parts.append(f"最近聊过：{'、'.join(d['last_topics'][:5])}")

        recent_emotions = [e["emotion"] for e in d["emotion_log"][-5:]]
        if recent_emotions:
            parts.append(f"近期情绪：{'→'.join(recent_emotions)}")

        return "，".join(parts) + "。" if parts else ""

    # ── 情感趋势分析 ─────────────────────────
    def emotion_trend(self, last_n: int = 10) -> dict:
        """统计最近 N 条情感记录的分布"""
        log = self.data["emotion_log"][-last_n:]
        if not log:
            return {}
        from collections import Counter
        counts = Counter(e["emotion"] for e in log)
        total = len(log)
        return {k: round(v / total, 2) for k, v in counts.most_common()}

    def __repr__(self):
        return (f"UserMemory(user_id={self.user_id!r}, "
                f"name={self.data['name']!r}, "
                f"chats={self.data['chat_count']})")
