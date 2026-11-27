"""
情感检测模块（Emotion Detector）
────────────────────────────────────────────────────────────────
架构：
  · 轻量 Transformer 分类器（6 层 Encoder）
  · 输入：中文文本
  · 输出：情感类别 + 置信度 + 全类别概率

两种模式：
  1. 规则辅助模式（冷启动，无需训练）
  2. 训练模式（用对话数据微调，精度更高）

情感类别（8类，适合老年陪伴场景）：
  孤独 / 开心 / 悲伤 / 焦虑 / 平静 / 思念 / 愤怒 / 困惑
"""

from __future__ import annotations
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
from typing import NamedTuple
from config.settings import CHECKPOINT_DIR


# ════════════════════════════════════════════
# 输出结构
# ════════════════════════════════════════════

class EmotionResult(NamedTuple):
    emotion: str           # 主情感
    confidence: float      # 置信度 0~1
    all_scores: dict       # 全类别分布
    needs_care: bool       # 是否需要特别关怀

    def __str__(self):
        bar = "█" * int(self.confidence * 10) + "░" * (10 - int(self.confidence * 10))
        return (f"[情感] {self.emotion}  {bar} {self.confidence:.0%}"
                + ("  ⚠ 需关怀" if self.needs_care else ""))


# ════════════════════════════════════════════
# Transformer 情感分类模型
# ════════════════════════════════════════════

EMOTION_LABELS = ["孤独", "开心", "悲伤", "焦虑", "平静", "思念", "愤怒", "困惑"]
CARE_EMOTIONS  = {"孤独", "悲伤", "焦虑", "思念", "愤怒"}   # 需要主动关怀的情感


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 256):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(max_len).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d_model, 2).float() * (-torch.log(torch.tensor(10000.0)) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))  # (1, max_len, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1)]


class EmotionTransformer(nn.Module):
    """
    专为中文短文本情感分类设计的 Transformer
    参数量约 3M，可在 CPU 上流畅推理（< 50ms/条）
    """

    def __init__(
        self,
        vocab_size: int = 21128,   # BERT 中文词表大小
        d_model: int = 256,
        nhead: int = 8,
        num_layers: int = 4,
        dim_feedforward: int = 512,
        dropout: float = 0.1,
        num_classes: int = len(EMOTION_LABELS),
        max_len: int = 128,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_enc   = PositionalEncoding(d_model, max_len)
        self.dropout   = nn.Dropout(dropout)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
            norm_first=True,          # Pre-LN，训练更稳定
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # 分类头：[CLS] token → softmax
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, num_classes),
        )

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor | None = None) -> torch.Tensor:
        # input_ids: (B, L)
        x = self.embedding(input_ids)           # (B, L, D)
        x = self.pos_enc(x)
        x = self.dropout(x)

        # 构造 padding mask（True = 忽略）
        src_key_padding_mask = None
        if attention_mask is not None:
            src_key_padding_mask = (attention_mask == 0)

        x = self.encoder(x, src_key_padding_mask=src_key_padding_mask)  # (B, L, D)
        cls = x[:, 0, :]               # 取第一个 token 作为句子表示
        logits = self.classifier(cls)  # (B, num_classes)
        return logits


# ════════════════════════════════════════════
# 情感检测器（对外接口）
# ════════════════════════════════════════════

class EmotionDetector:
    """
    情感检测器
    自动选择：有模型权重 → 神经网络推理；无权重 → 规则辅助
    """

    CKPT_PATH = CHECKPOINT_DIR / "emotion_model.pt"
    THRESHOLD = 0.42   # 置信度低于此值视为"平静"

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: EmotionTransformer | None = None
        self.tokenizer = None
        self._use_rule_fallback = True
        self._try_load_model()

    def _try_load_model(self):
        """尝试加载已训练的模型权重"""
        if not self.CKPT_PATH.exists():
            return
        try:
            # 尝试使用 transformers BertTokenizer（更精准）
            from transformers import BertTokenizerFast
            self.tokenizer = BertTokenizerFast.from_pretrained(os.environ.get("WALLE_EMOTION_TOKENIZER", "bert-base-chinese"))

            self.model = EmotionTransformer().to(self.device)
            state = torch.load(self.CKPT_PATH, map_location=self.device)
            self.model.load_state_dict(state)
            self.model.eval()
            self._use_rule_fallback = False
            print(f"[情感] 已加载神经网络模型 ({self.device})")
        except Exception as e:
            print(f"[情感] 模型加载失败，使用规则模式：{e}")

    # ── 主入口 ───────────────────────────────
    def detect(self, text: str) -> EmotionResult:
        if self._use_rule_fallback or self.model is None:
            return self._rule_detect(text)
        return self._nn_detect(text)

    # ── 神经网络推理 ──────────────────────────
    def _nn_detect(self, text: str) -> EmotionResult:
        enc = self.tokenizer(
            text,
            max_length=128,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        input_ids = enc["input_ids"].to(self.device)
        attention_mask = enc["attention_mask"].to(self.device)

        with torch.no_grad():
            logits = self.model(input_ids, attention_mask)
            probs = F.softmax(logits, dim=-1)[0].cpu()

        idx = probs.argmax().item()
        confidence = probs[idx].item()
        emotion = EMOTION_LABELS[idx] if confidence >= self.THRESHOLD else "平静"
        all_scores = {e: round(p.item(), 3) for e, p in zip(EMOTION_LABELS, probs)}

        return EmotionResult(
            emotion=emotion,
            confidence=confidence,
            all_scores=all_scores,
            needs_care=emotion in CARE_EMOTIONS and confidence >= self.THRESHOLD,
        )

    # ── 规则辅助（冷启动）────────────────────
    def _rule_detect(self, text: str) -> EmotionResult:
        rules = {
            "孤独": ["孤独", "寂寞", "没人", "一个人", "冷清", "空荡荡", "没有伴"],
            "开心": ["开心", "高兴", "快乐", "好棒", "哈哈", "太好了", "不错", "满意"],
            "悲伤": ["难过", "伤心", "哭", "痛", "悲", "委屈", "心疼", "遗憾"],
            "焦虑": ["担心", "焦虑", "害怕", "紧张", "怎么办", "不知道", "慌"],
            "平静": ["还好", "挺好", "一般", "平常", "没什么", "都行"],
            "思念": ["想念", "思念", "想你", "想他", "想她", "好久不见", "怀念"],
            "愤怒": ["生气", "愤怒", "气死", "烦", "讨厌", "恼火", "不满"],
            "困惑": ["不明白", "困惑", "搞不懂", "为什么", "奇怪", "不理解"],
        }
        scores = {e: 0.05 for e in EMOTION_LABELS}
        for emotion, keywords in rules.items():
            for kw in keywords:
                if kw in text:
                    scores[emotion] += 0.25

        # 归一化
        total = sum(scores.values())
        probs = {e: round(s / total, 3) for e, s in scores.items()}
        top = max(probs, key=probs.get)
        confidence = probs[top]
        emotion = top if confidence >= self.THRESHOLD else "平静"

        return EmotionResult(
            emotion=emotion,
            confidence=confidence,
            all_scores=probs,
            needs_care=emotion in CARE_EMOTIONS and confidence >= self.THRESHOLD,
        )
