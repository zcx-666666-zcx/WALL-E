"""
对话引擎（Dialogue Engine）
────────────────────────────────────────────────────────────────
职责：
  · 加载大语言模型（支持 4-bit 量化）
  · 应用 LoRA 人设适配器（如已训练）
  · 构建携带人设 + 记忆 + 情感感知的完整 Prompt
  · 流式 / 非流式生成回复

设计原则：
  · 单例模型，避免重复加载
  · 人设适配器热切换（不重新加载基础模型）
  · 无 GPU 时自动降级到演示模式
"""

from __future__ import annotations
import time
from typing import Generator, Optional
from pathlib import Path

from personas.persona_manager import Persona
from memory.user_memory import UserMemory
from core.emotion import EmotionResult
from config.settings import (
    BASE_MODEL, USE_4BIT_QUANT, MAX_NEW_TOKENS,
    TEMPERATURE, TOP_P, REPETITION_PENALTY,
    LORA_R, LORA_ALPHA, LORA_DROPOUT, LORA_TARGET_MODULES,
    CHECKPOINT_DIR,
)


class DialogueEngine:
    """
    对话引擎核心类

    使用方式：
        engine = DialogueEngine()
        engine.load()   # 加载模型（首次耗时）

        for chunk in engine.stream(persona, history, user_input, memory, emotion):
            print(chunk, end="", flush=True)
    """

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._loaded = False
        self._current_adapter: Optional[str] = None   # 当前已挂载的 LoRA 适配器 ID
        self._demo_mode = False

    # ════════════════════════════════════════
    # 模型加载
    # ════════════════════════════════════════

    def load(self, force_demo: bool = False):
        """
        加载模型
        force_demo=True  → 跳过模型加载，使用规则演示回复（适合无 GPU 环境调试）
        """
        if force_demo:
            self._demo_mode = True
            self._loaded = True
            print("[引擎] 演示模式（无需 GPU）已启用")
            return

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
            from peft import get_peft_model, LoraConfig, TaskType

            print(f"[引擎] 正在加载模型 {BASE_MODEL}，请稍候…")
            t0 = time.time()

            self.tokenizer = AutoTokenizer.from_pretrained(
                BASE_MODEL, trust_remote_code=True
            )

            bnb = None
            if USE_4BIT_QUANT:
                bnb = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=(torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16),
                    bnb_4bit_use_double_quant=True,
                )

            self.model = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL,
                quantization_config=bnb,
                device_map="auto",
                trust_remote_code=True,
            )

            # 挂载 LoRA 结构（权重从 checkpoint 加载）
            lora_cfg = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=LORA_R,
                lora_alpha=LORA_ALPHA,
                lora_dropout=LORA_DROPOUT,
                target_modules=LORA_TARGET_MODULES,
                bias="none",
            )
            self.model = get_peft_model(self.model, lora_cfg)
            self.model.eval()

            print(f"[引擎] 模型加载完成，耗时 {time.time()-t0:.1f}s")
            self._loaded = True

        except ImportError as e:
            print(f"[引擎] 缺少依赖库（{e}），切换到演示模式")
            self._demo_mode = True
            self._loaded = True
        except Exception as e:
            print(f"[引擎] 模型加载失败（{e}），切换到演示模式")
            self._demo_mode = True
            self._loaded = True

    def load_adapter(self, persona_id: str) -> bool:
        """
        热切换 LoRA 人设适配器
        返回 True 表示切换成功，False 表示该人设尚无适配器
        """
        if self._demo_mode:
            return False
        adapter_path = CHECKPOINT_DIR / persona_id
        if not adapter_path.exists():
            return False
        if self._current_adapter == persona_id:
            return True
        try:
            self.model.load_adapter(str(adapter_path), adapter_name=persona_id)
            self.model.set_adapter(persona_id)
            self._current_adapter = persona_id
            print(f"[引擎] 已切换人设适配器 → {persona_id}")
            return True
        except Exception as e:
            print(f"[引擎] 适配器加载失败：{e}")
            return False

    # ════════════════════════════════════════
    # Prompt 构建
    # ════════════════════════════════════════

    def _build_messages(
        self,
        persona: Persona,
        history: list[dict],
        user_input: str,
        memory: UserMemory,
        emotion: Optional[EmotionResult],
    ) -> list[dict]:
        """
        构建完整消息列表（system + history + 当前输入）
        """
        system = persona.system_prompt

        # 注入用户长期记忆
        ctx = memory.context_summary()
        if ctx:
            system += f"\n\n【你对这位用户的了解】\n{ctx}"

        # 注入情感感知指令
        if emotion and emotion.needs_care:
            system += (
                f'\n\n【情感提示】检测到对方可能感到"{emotion.emotion}"，'
                f'请在回复中自然地给予关心和温暖，不要刻意提及"情感检测"这类词。'
            )

        # ── 联网搜索注入 ──────────────────────
        from core.searcher import needs_search, search
        if needs_search(user_input):
            print(f"[搜索] 触发联网：{user_input}")
            result = search(user_input)
            if result:
                system += (
                    f"\n\n【实时搜索结果】\n{result}\n"
                    f"请基于以上搜索结果回答用户的问题，"
                    f"但保持瓦利的说话风格，不要照搬原文。"
                )

        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        return messages

    # ════════════════════════════════════════
    # 生成接口
    # ════════════════════════════════════════

    def stream(
        self,
        persona: Persona,
        history: list[dict],
        user_input: str,
        memory: UserMemory,
        emotion: Optional[EmotionResult] = None,
    ) -> Generator[str, None, None]:
        """
        流式生成回复（逐 token yield）
        调用方负责拼接结果
        """
        if not self._loaded:
            raise RuntimeError("请先调用 engine.load() 加载模型")

        if self._demo_mode:
            yield from self._demo_stream(user_input, persona, emotion)
            return

        messages = self._build_messages(persona, history, user_input, memory, emotion)

        import torch
        from transformers import TextIteratorStreamer
        from threading import Thread

        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        streamer = TextIteratorStreamer(
            self.tokenizer, skip_prompt=True, skip_special_tokens=True
        )
        gen_kwargs = dict(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            repetition_penalty=REPETITION_PENALTY,
            do_sample=True,
            streamer=streamer,
        )
        thread = Thread(target=self.model.generate, kwargs=gen_kwargs)
        thread.start()

        for chunk in streamer:
            yield chunk

        thread.join()

    def generate(
        self,
        persona: Persona,
        history: list[dict],
        user_input: str,
        memory: UserMemory,
        emotion: Optional[EmotionResult] = None,
    ) -> str:
        """非流式生成（供 API 调用）"""
        return "".join(self.stream(persona, history, user_input, memory, emotion))

    # ════════════════════════════════════════
    # 演示模式回复
    # ════════════════════════════════════════

    def _demo_stream(
        self, text: str, persona: Persona, emotion: Optional[EmotionResult]
    ) -> Generator[str, None, None]:
        import time, random

        templates = {
            "grandma_chen": [
                "哎呀，你来啦！陈奶奶正想着你呢，今天吃饭了没有呀？",
                "嗯嗯，奶奶听着呢。你说得对，慢慢来，别着急哟。",
                "这孩子真懂事。奶奶年轻那时候也遇过这种事，后来都过去了嘞。",
                "你要照顾好自己哦，吃好睡好，身体是本钱嘛！",
            ],
            "grandpa_li": [
                "哈哈，来了！最近身体咋样，有没有锻炼锻炼？",
                "您说得有道理！老话说得好，车到山前必有路，别担心。",
                "哈，这事儿李大爷年轻时候也碰过，甭急，慢慢来。",
                "行嘞！有什么新鲜事跟我说说，我这老头子也好长见识。",
            ],
            "sister_wang": [
                "哎呀，侬来了！我正想着跟你说件有趣的事情嘞！",
                "真的呀！这个我也有感触，我们社区里也有类似的事情……",
                "好额好额！侬说得对，生活嘛就是要开开心心的！",
            ],
        }

        care_prefix = {
            "孤独": "你不孤独的，我一直在这里陪着你。",
            "悲伤": "哎，听你说这些，心里也难受。不过别太伤心了，",
            "焦虑": "别担心哈，慢慢想，办法总比困难多。",
            "思念": "思念的感觉真的很难受。不过",
        }

        # 选择模板
        pool = templates.get(persona.id, list(templates.values())[0])
        response = random.choice(pool)

        # 如果需要情感关怀，加前缀
        if emotion and emotion.needs_care:
            prefix = care_prefix.get(emotion.emotion, "")
            if prefix:
                response = prefix + response[0].lower() + response[1:]

        # 模拟流式输出（每字间隔 40ms，像真人打字）
        for char in response:
            yield char
            time.sleep(0.04)
