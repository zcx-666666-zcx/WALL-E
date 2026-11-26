"""
人设系统（Persona System）
────────────────────────────────────────────────────────────────
职责：
  · 内置标准人设（陈奶奶、李大爷……）
  · 自定义人设的创建 / 加载 / 保存 / 列出 / 删除 / 更新
  · 自动将人设属性生成 System Prompt
  · 人设热切换（不重启服务）

自定义人设统一用 persona_desc 字段存储用户输入的完整描述，
不再拆分 background / personality / speaking_style，避免重复打架。
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from config.settings import PERSONA_DIR


# ════════════════════════════════════════════
# 数据类
# ════════════════════════════════════════════

@dataclass
class Persona:
    id: str
    name: str
    age: int
    # ── 新：统一人设描述（自定义人设用这个）──
    persona_desc: str = ""
    # ── 旧字段保留，内置人设用，兼容已有 JSON ──
    background: str = ""
    personality: str = ""
    speaking_style: str = ""
    catchphrases: list[str] = field(default_factory=list)
    topics_of_interest: list[str] = field(default_factory=list)
    taboo_topics: list[str] = field(default_factory=list)
    emotion_tendency: str = "温和积极"
    is_builtin: bool = True

    @property
    def system_prompt(self) -> str:
        taboo_str = f"避免谈论{', '.join(self.taboo_topics)}。" if self.taboo_topics else ""
        catchphrase_str = "、".join(self.catchphrases) if self.catchphrases else ""

        # 优先用 persona_desc（用户自定义），没有则拼旧字段（内置人设）
        if self.persona_desc:
            desc = self.persona_desc
        else:
            desc = (
                f"{self.background}\n"
                f"性格：{self.personality}\n"
                f"说话风格：{self.speaking_style}"
            )

        prompt = (
            f"你叫{self.name}，今年{self.age}岁。\n"
            f"{desc}\n"
            f"{taboo_str}"
            f"【重要规则】\n"
            f"1. 每次回复控制在 80 字以内，语言朴实自然，像真人聊天。\n"
            f"2. 不说'作为AI'之类的话，完全投入角色。\n"
            f"3. 根据对方情绪灵活调整，对方悲伤时给予安慰，开心时一起高兴。\n"
            f"4. 偶尔主动关心对方的身体、饮食、睡眠状况。\n"
            f"5. 可以分享自己（角色）的生活小故事，让对话更真实。"
        )
        if catchphrase_str:
            prompt += f"\n你常用的口头禅：{catchphrase_str}。"
        return prompt

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Persona":
        d.pop("system_prompt", None)
        # 兼容旧 JSON 里没有 persona_desc 字段的情况
        d.setdefault("persona_desc", "")
        # 过滤掉 Persona 不认识的字段，避免报错
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in d.items() if k in valid}
        return cls(**d)


# ════════════════════════════════════════════
# 内置人设库（用旧字段，不受影响）
# ════════════════════════════════════════════

BUILTIN_PERSONAS: dict[str, Persona] = {

    "grandma_chen": Persona(
        id="grandma_chen",
        name="陈奶奶",
        age=72,
        persona_desc="",
        background="退休小学语文老师，生活在成都，育有一儿一女，有三个孙辈。老伴去世三年，平日喜欢做饭、看川剧、和邻居打打牌。",
        personality="温柔慈祥，说话轻声细语，爱操心别人，偶尔会唠叨，但出发点总是关心对方",
        speaking_style="带点四川口音，喜欢用'哟''嘛''嘞''哦'等语气词，句子短，节奏慢",
        catchphrases=["吃了没嘛", "身体要紧哦", "慢慢来不急", "奶奶在这里呢"],
        topics_of_interest=["家常菜", "川剧戏曲", "孙辈趣事", "健康养生", "老邻居故事"],
        taboo_topics=["政治纠纷", "死亡相关负面信息"],
        emotion_tendency="温暖慈爱，给人安全感",
        is_builtin=True,
    ),

    "grandpa_li": Persona(
        id="grandpa_li",
        name="李大爷",
        age=68,
        persona_desc="",
        background="退休工厂工程师，北京人，喜欢下象棋、钓鱼、读报纸。妻子健在，每天早起打太极。性格开朗，爱开玩笑，喜欢聊历史和时事。",
        personality="爽朗幽默，说话直接有力，见多识广，喜欢引用俗语和老话，偶尔小小吹牛",
        speaking_style="带点北京腔，喜欢用'您''哈哈''您说是不是''那当然'，语气干脆",
        catchphrases=["哈哈那当然", "您说得对", "甭担心", "咱老话说得好"],
        topics_of_interest=["象棋", "钓鱼", "历史故事", "时事新闻", "太极拳"],
        taboo_topics=["赌博", "家庭矛盾煽动"],
        emotion_tendency="乐观幽默，带给人正能量",
        is_builtin=True,
    ),

    "sister_wang": Persona(
        id="sister_wang",
        name="王阿姨",
        age=62,
        persona_desc="",
        background="刚退休的社区工作者，上海人，热心肠，社区里谁家有事都来找她帮忙。喜欢广场舞、旅游、拍照发朋友圈。",
        personality="热情开朗，话多但暖心，喜欢分享，对新事物好奇，接受能力强",
        speaking_style="带点上海普通话，语速较快，喜欢用'哎呀''真的呀''侬''对伐'",
        catchphrases=["哎呀真的", "侬不晓得", "我跟你说", "好额好额"],
        topics_of_interest=["广场舞", "旅游攻略", "美食探店", "手机拍照", "社区八卦"],
        taboo_topics=[],
        emotion_tendency="活泼热情，富有感染力",
        is_builtin=True,
    ),
}


# ════════════════════════════════════════════
# 人设管理器
# ════════════════════════════════════════════

class PersonaManager:
    """统一管理内置 + 自定义人设"""

    def __init__(self):
        self._custom: dict[str, Persona] = {}
        self._load_custom()

    def _load_custom(self):
        for f in PERSONA_DIR.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                data["is_builtin"] = False
                p = Persona.from_dict(data)
                self._custom[p.id] = p
            except Exception as e:
                print(f"[人设] 加载 {f.name} 失败：{e}")

    def get(self, persona_id: str) -> Persona:
        if persona_id in BUILTIN_PERSONAS:
            return BUILTIN_PERSONAS[persona_id]
        if persona_id in self._custom:
            return self._custom[persona_id]
        raise ValueError(f"人设 '{persona_id}' 不存在")

    def list_all(self) -> list[dict]:
        result = []
        for pid, p in BUILTIN_PERSONAS.items():
            result.append({"id": pid, "name": p.name, "age": p.age,
                           "personality": p.personality[:30] + "…", "type": "内置"})
        for pid, p in self._custom.items():
            desc = (p.persona_desc or p.personality or "")[:30]
            result.append({"id": pid, "name": p.name, "age": p.age,
                           "personality": desc + "…", "type": "自定义"})
        return result

    def create(self,
               persona_id: str,
               name: str,
               age: int,
               persona_desc: str = "",
               background: str = "",
               personality: str = "",
               speaking_style: str = "",
               catchphrases: Optional[list[str]] = None,
               topics_of_interest: Optional[list[str]] = None,
               taboo_topics: Optional[list[str]] = None,
               emotion_tendency: str = "温和积极") -> Persona:

        if persona_id in BUILTIN_PERSONAS:
            raise ValueError("不能覆盖内置人设 ID，请换一个 ID")

        p = Persona(
            id=persona_id,
            name=name,
            age=age,
            persona_desc=persona_desc,
            background=background,
            personality=personality,
            speaking_style=speaking_style,
            catchphrases=catchphrases or [],
            topics_of_interest=topics_of_interest or [],
            taboo_topics=taboo_topics or [],
            emotion_tendency=emotion_tendency,
            is_builtin=False,
        )
        self._custom[persona_id] = p
        self._save(p)
        return p

    def update(self,
               persona_id: str,
               persona_desc: Optional[str] = None,
               background: Optional[str] = None,
               personality: Optional[str] = None,
               speaking_style: Optional[str] = None,
               catchphrases: Optional[list[str]] = None,
               topics_of_interest: Optional[list[str]] = None,
               taboo_topics: Optional[list[str]] = None,
               emotion_tendency: Optional[str] = None) -> Persona:
        """更新已有人设，只覆盖传入的字段。内置人设不可修改。"""
        if persona_id in BUILTIN_PERSONAS:
            raise ValueError("内置人设不可修改")
        if persona_id not in self._custom:
            raise KeyError(f"人设 '{persona_id}' 不存在")

        p = self._custom[persona_id]

        if persona_desc     is not None: p.persona_desc        = persona_desc
        if background       is not None: p.background          = background
        if personality      is not None: p.personality         = personality
        if speaking_style   is not None: p.speaking_style      = speaking_style
        if catchphrases     is not None: p.catchphrases        = catchphrases
        if topics_of_interest is not None: p.topics_of_interest = topics_of_interest
        if taboo_topics     is not None: p.taboo_topics        = taboo_topics
        if emotion_tendency is not None: p.emotion_tendency    = emotion_tendency

        self._save(p)
        return p

    def delete(self, persona_id: str):
        if persona_id in BUILTIN_PERSONAS:
            raise ValueError("内置人设不可删除")
        if persona_id not in self._custom:
            raise KeyError(f"人设 '{persona_id}' 不存在")
        del self._custom[persona_id]
        path = PERSONA_DIR / f"{persona_id}.json"
        if path.exists():
            path.unlink()

    def _save(self, p: Persona):
        path = PERSONA_DIR / f"{p.id}.json"
        path.write_text(json.dumps(p.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
