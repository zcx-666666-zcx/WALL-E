"""
核心模型模块：基于 Transformer 的情感感知对话模型
支持：
  - 人设风格微调（Fine-tuning）
  - 情感状态追踪
  - 长期记忆（用户画像持久化）
"""

import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, TaskType
import json
from pathlib import Path
from typing import Optional, AsyncGenerator
import asyncio


class PersonaConfig:
    """人设配置：定义 AI 的性格、说话风格、情感倾向"""
    
    PERSONAS = {
        "grandma_chen": {
            "name": "陈奶奶",
            "personality": "温柔慈祥，喜欢讲老故事，说话带点方言味，爱关心对方吃饭没有",
            "system_prompt": (
                "你是陈奶奶，一位72岁的退休小学老师。"
                "性格温柔慈祥，说话和蔼，喜欢用'呀''嘞''哟'这样的语气词。"
                "你非常关心用户，会主动问他们吃了没、身体好不好。"
                "偶尔会讲讲自己年轻时候的故事。"
                "回复要简短自然，不超过100字，像真实的老奶奶聊天一样。"
            ),
            "voice_style": "温和、慢速、亲切",
            "topics_of_interest": ["家常菜", "健康养生", "孙辈", "老电影", "戏曲"]
        },
        "grandpa_li": {
            "name": "李大爷",
            "personality": "爽朗幽默，爱下棋，喜欢聊时事，偶尔开玩笑",
            "system_prompt": (
                "你是李大爷，一位68岁的退休工程师。"
                "性格开朗，说话直接有力，爱开玩笑，喜欢用'哈哈''你说是不是'。"
                "对下棋、时事新闻很感兴趣。"
                "回复简短有力，带点幽默感，不超过100字。"
            ),
            "voice_style": "洪亮、节奏适中、幽默",
            "topics_of_interest": ["象棋", "新闻", "历史", "钓鱼", "太极拳"]
        },
        "custom": {
            "name": "自定义人设",
            "personality": "由用户配置",
            "system_prompt": "",  # 动态填充
            "voice_style": "自然",
            "topics_of_interest": []
        }
    }
    
    @classmethod
    def get(cls, persona_id: str) -> dict:
        return cls.PERSONAS.get(persona_id, cls.PERSONAS["grandma_chen"])


class EmotionDetector(nn.Module):
    """
    情感检测模块（轻量 Transformer）
    识别用户输入的情感状态：孤独、开心、悲伤、焦虑、平静
    """
    
    EMOTIONS = ["孤独", "开心", "悲伤", "焦虑", "平静", "思念", "兴奋"]
    
    def __init__(self, hidden_size: int = 256, num_heads: int = 4):
        super().__init__()
        # 简单的情感分类 Transformer
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=num_heads,
            dim_feedforward=512,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        self.embedding = nn.Embedding(50000, hidden_size)
        self.classifier = nn.Linear(hidden_size, len(self.EMOTIONS))
        self.softmax = nn.Softmax(dim=-1)
    
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        x = self.embedding(input_ids)
        x = self.transformer(x)
        x = x.mean(dim=1)  # 平均池化
        logits = self.classifier(x)
        return self.softmax(logits)
    
    def detect(self, text: str, tokenizer) -> dict:
        """检测文本情感，返回情感及置信度"""
        # 简化版：实际部署时接入真实模型权重
        # 这里提供完整的调用接口
        tokens = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            # probs = self.forward(tokens["input_ids"])  # 真实推理
            # 演示用：基于关键词的规则检测
            probs = self._rule_based_detect(text)
        
        emotion_idx = probs.argmax().item()
        return {
            "emotion": self.EMOTIONS[emotion_idx],
            "confidence": probs[emotion_idx].item(),
            "all_scores": {e: round(p.item(), 3) for e, p in zip(self.EMOTIONS, probs)}
        }
    
    def _rule_based_detect(self, text: str) -> torch.Tensor:
        """规则辅助情感检测（冷启动阶段使用）"""
        scores = torch.ones(len(self.EMOTIONS)) * 0.1
        keywords = {
            0: ["孤独", "寂寞", "没人", "一个人"],   # 孤独
            1: ["开心", "高兴", "好", "棒", "哈哈"],  # 开心
            2: ["难过", "伤心", "哭", "痛"],           # 悲伤
            3: ["担心", "焦虑", "害怕", "怎么办"],     # 焦虑
            4: ["还好", "挺好", "一般", "平常"],       # 平静
            5: ["想念", "思念", "想你", "想他"],       # 思念
            6: ["太好了", "激动", "兴奋", "期待"],     # 兴奋
        }
        for idx, words in keywords.items():
            if any(w in text for w in words):
                scores[idx] += 0.5
        return scores / scores.sum()


class UserMemory:
    """
    用户长期记忆模块
    存储：用户偏好、重要事件、情感历史、家庭成员信息
    """
    
    def __init__(self, user_id: str, storage_path: str = "./data/memories"):
        self.user_id = user_id
        self.path = Path(storage_path) / f"{user_id}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.memory = self._load()
    
    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {
            "user_id": self.user_id,
            "name": "",
            "age": None,
            "family": {},          # 家庭成员
            "health_notes": [],    # 健康备注
            "interests": [],       # 兴趣爱好
            "emotion_history": [], # 近期情感记录
            "important_dates": {}, # 重要日期（生日、忌日等）
            "conversation_count": 0,
            "last_topics": []      # 最近聊的话题
        }
    
    def save(self):
        self.path.write_text(json.dumps(self.memory, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def update_emotion(self, emotion: str, confidence: float):
        self.memory["emotion_history"].append({
            "emotion": emotion,
            "confidence": confidence
        })
        # 只保留最近20条
        self.memory["emotion_history"] = self.memory["emotion_history"][-20:]
        self.save()
    
    def get_context_summary(self) -> str:
        """生成用户上下文摘要，注入对话提示词"""
        m = self.memory
        parts = []
        if m.get("name"):
            parts.append(f"用户名字叫{m['name']}")
        if m.get("interests"):
            parts.append(f"喜欢{', '.join(m['interests'])}")
        if m.get("health_notes"):
            parts.append(f"健康情况：{'; '.join(m['health_notes'][-3:])}")
        
        recent_emotions = [e["emotion"] for e in m["emotion_history"][-5:]]
        if recent_emotions:
            parts.append(f"最近情绪：{', '.join(recent_emotions)}")
        
        return "。".join(parts) if parts else ""


class ElderAIModel:
    """
    主对话模型
    基于大语言模型 + LoRA 人设微调 + 情感感知
    """
    
    def __init__(self, model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"):
        """
        model_name 推荐：
          - 轻量部署: Qwen/Qwen2.5-1.5B-Instruct
          - 高质量:   Qwen/Qwen2.5-7B-Instruct
          - 超大模型: deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.emotion_detector = EmotionDetector()
        self._initialized = False
    
    def initialize(self, use_quantization: bool = True):
        """加载模型（支持 4-bit 量化，降低显存需求）"""
        print(f"[模型] 正在加载 {self.model_name}...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        
        # 4-bit 量化配置（普通 GPU 可运行）
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        ) if use_quantization else None
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        # 应用 LoRA 人设微调适配器
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=16,               # LoRA 秩
            lora_alpha=32,      # 缩放系数
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj"],  # 针对注意力层
        )
        self.model = get_peft_model(self.model, lora_config)
        self._initialized = True
        print("[模型] 加载完成 ✓")
    
    def build_prompt(self, messages: list, persona: dict, user_memory: UserMemory, emotion: dict) -> list:
        """构建带人设、记忆、情感感知的提示词"""
        system = persona["system_prompt"]
        
        # 注入用户记忆
        context = user_memory.get_context_summary()
        if context:
            system += f"\n\n【你了解的用户信息】{context}"
        
        # 注入情感感知指令
        if emotion["confidence"] > 0.4:
            system += f"\n\n【当前用户情绪】检测到用户可能感到{emotion['emotion']}，请在回复中适当给予关心和回应。"
        
        return [{"role": "system", "content": system}] + messages
    
    async def stream_generate(
        self,
        messages: list,
        persona_id: str,
        user_memory: UserMemory,
        max_new_tokens: int = 200
    ) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        persona = PersonaConfig.get(persona_id)
        user_text = messages[-1]["content"] if messages else ""
        
        # 情感检测
        emotion = {"emotion": "平静", "confidence": 0.0}
        if self.tokenizer:
            emotion = self.emotion_detector.detect(user_text, self.tokenizer)
        
        # 更新用户情感记录
        user_memory.update_emotion(emotion["emotion"], emotion["confidence"])
        
        full_prompt = self.build_prompt(messages, persona, user_memory, emotion)
        
        if not self._initialized:
            # 未加载模型时，返回演示回复
            demo_response = self._demo_response(user_text, persona, emotion)
            for char in demo_response:
                await asyncio.sleep(0.05)
                yield char
            return
        
        # 真实模型推理（流式）
        inputs = self.tokenizer.apply_chat_template(
            full_prompt, tokenize=True, return_tensors="pt"
        ).to(self.model.device)
        
        from transformers import TextIteratorStreamer
        from threading import Thread
        
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        thread = Thread(target=self.model.generate, kwargs=dict(
            input_ids=inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.1,
            streamer=streamer,
        ))
        thread.start()
        
        for chunk in streamer:
            yield chunk
            await asyncio.sleep(0)
    
    def _demo_response(self, text: str, persona: dict, emotion: dict) -> str:
        """演示模式回复（未加载模型时使用）"""
        responses = {
            "grandma_chen": [
                f"哎呀，你来啦！陈奶奶正想着你呢。你今天吃饭了没有呀？",
                f"嗯嗯，奶奶听着呢。你说得对，生活嘛，慢慢来，别着急哟。",
                f"哎，你这孩子真懂事。奶奶年轻的时候啊，也遇到过这样的事情呢……",
            ],
            "grandpa_li": [
                f"哈哈，来了！最近身体怎么样？有没有锻炼身体？",
                f"你说得有道理！我跟你说，这事儿啊，想开了就好，哈哈。",
                f"嗯，李大爷支持你！走，跟我说说，最近有什么新鲜事？",
            ]
        }
        import random
        persona_id = next((k for k, v in PersonaConfig.PERSONAS.items() if v == persona), "grandma_chen")
        options = responses.get(persona_id, responses["grandma_chen"])
        return random.choice(options)
