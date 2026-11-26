"""
训练模块（Training）
────────────────────────────────────────────────────────────────
包含两个训练器：

1. EmotionTrainer   → 训练情感分类 Transformer
   · 数据格式：JSONL {"text": "我很孤独", "label": "孤独"}
   · 训练完保存到 data/checkpoints/emotion_model.pt

2. PersonaTrainer   → 用 LoRA 微调大语言模型的人设风格
   · 数据格式：JSONL {"instruction": "你好", "response": "哎呀你来啦！"}
   · 训练完保存到 data/checkpoints/{persona_id}/

使用方式：
    python -m training.trainer --task emotion --data data/train/emotion.jsonl
    python -m training.trainer --task persona --persona grandma_chen --data data/train/grandma.jsonl
"""

from __future__ import annotations
import json
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from core.emotion import EmotionTransformer, EMOTION_LABELS
from config.settings import CHECKPOINT_DIR, TRAIN_DIR


# ════════════════════════════════════════════
# 情感分类训练器
# ════════════════════════════════════════════

class EmotionDataset(Dataset):
    """
    情感分类数据集
    JSONL格式，每行：{"text": "...", "label": "孤独"}
    """
    def __init__(self, path: str | Path, tokenizer, max_len: int = 128):
        self.samples = []
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.label2id = {e: i for i, e in enumerate(EMOTION_LABELS)}

        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                if d.get("label") in self.label2id:
                    self.samples.append(d)

        print(f"[数据] 加载 {len(self.samples)} 条情感样本")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        enc = self.tokenizer(
            item["text"],
            max_length=self.max_len,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "label":          torch.tensor(self.label2id[item["label"]], dtype=torch.long),
        }


class EmotionTrainer:
    """情感分类 Transformer 训练器"""

    def __init__(
        self,
        data_path: str | Path,
        epochs: int = 10,
        batch_size: int = 32,
        lr: float = 2e-4,
    ):
        self.data_path = Path(data_path)
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.save_path = CHECKPOINT_DIR / "emotion_model.pt"

    def train(self):
        from transformers import BertTokenizerFast

        print(f"[情感训练] 设备：{self.device}")
        tokenizer = BertTokenizerFast.from_pretrained("bert-base-chinese")
        dataset = EmotionDataset(self.data_path, tokenizer)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True, num_workers=0)

        model = EmotionTransformer(vocab_size=tokenizer.vocab_size).to(self.device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=self.lr, weight_decay=0.01)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=self.epochs)
        criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

        best_acc = 0.0
        for epoch in range(1, self.epochs + 1):
            model.train()
            total_loss, correct, total = 0.0, 0, 0
            t0 = time.time()

            for batch in loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["label"].to(self.device)

                optimizer.zero_grad()
                logits = model(input_ids, attention_mask)
                loss = criterion(logits, labels)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

                total_loss += loss.item()
                preds = logits.argmax(dim=-1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

            scheduler.step()
            acc = correct / total
            avg_loss = total_loss / len(loader)
            elapsed = time.time() - t0
            print(f"  Epoch {epoch:02d}/{self.epochs}  loss={avg_loss:.4f}  acc={acc:.2%}  {elapsed:.1f}s")

            if acc > best_acc:
                best_acc = acc
                torch.save(model.state_dict(), self.save_path)
                print(f"  ✓ 模型已保存（acc={best_acc:.2%}）→ {self.save_path}")

        print(f"\n[情感训练] 完成！最佳准确率 {best_acc:.2%}")


# ════════════════════════════════════════════
# 人设 LoRA 微调训练器
# ════════════════════════════════════════════

class PersonaDataset(Dataset):
    """
    人设对话数据集
    JSONL格式：{"instruction": "你好", "response": "哎呀你来啦！"}
    """
    def __init__(self, path: str | Path, tokenizer, persona_system_prompt: str, max_len: int = 512):
        self.samples = []
        self.tokenizer = tokenizer
        self.system_prompt = persona_system_prompt
        self.max_len = max_len

        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.samples.append(json.loads(line))

        print(f"[数据] 加载 {len(self.samples)} 条人设对话样本")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        messages = [
            {"role": "system",    "content": self.system_prompt},
            {"role": "user",      "content": item["instruction"]},
            {"role": "assistant", "content": item["response"]},
        ]
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        enc = self.tokenizer(
            text, max_length=self.max_len, truncation=True,
            padding="max_length", return_tensors="pt"
        )
        input_ids = enc["input_ids"].squeeze(0)
        labels = input_ids.clone()

        # 只对 response 部分计算 loss
        resp_start = text.rfind(item["response"])
        if resp_start != -1:
            prefix_len = len(self.tokenizer(text[:resp_start])["input_ids"])
            labels[:prefix_len] = -100

        return {
            "input_ids": input_ids,
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": labels,
        }


@dataclass
class PersonaTrainConfig:
    persona_id: str
    data_path: str | Path
    model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"
    epochs: int = 3
    batch_size: int = 4
    lr: float = 2e-4
    grad_accum: int = 4
    max_len: int = 512
    warmup_ratio: float = 0.1


class PersonaTrainer:
    """人设 LoRA 微调训练器"""

    def __init__(self, config: PersonaTrainConfig):
        self.cfg = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.save_dir = CHECKPOINT_DIR / config.persona_id

    def train(self):
        from transformers import (
            AutoTokenizer, AutoModelForCausalLM,
            BitsAndBytesConfig, TrainingArguments, Trainer,
            DataCollatorForSeq2Seq,
        )
        from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
        from personas.persona_manager import PersonaManager

        # 获取人设的 system prompt
        pm = PersonaManager()
        persona = pm.get(self.cfg.persona_id)
        print(f"[人设训练] 人设：{persona.name}  设备：{self.device}")

        # Tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.cfg.model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # 数据集
        dataset = PersonaDataset(self.cfg.data_path, tokenizer, persona.system_prompt, self.cfg.max_len)

        # 模型 + 量化
        bnb = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.cfg.model_name, quantization_config=bnb,
            device_map="auto", trust_remote_code=True,
        )
        model = prepare_model_for_kbit_training(model)

        # LoRA
        from config.settings import LORA_R, LORA_ALPHA, LORA_DROPOUT, LORA_TARGET_MODULES
        lora_cfg = LoraConfig(
            task_type=TaskType.CAUSAL_LM, r=LORA_R, lora_alpha=LORA_ALPHA,
            lora_dropout=LORA_DROPOUT, target_modules=LORA_TARGET_MODULES, bias="none",
        )
        model = get_peft_model(model, lora_cfg)
        model.print_trainable_parameters()

        # 训练参数
        total_steps = len(dataset) // (self.cfg.batch_size * self.cfg.grad_accum) * self.cfg.epochs
        args = TrainingArguments(
            output_dir=str(self.save_dir),
            num_train_epochs=self.cfg.epochs,
            per_device_train_batch_size=self.cfg.batch_size,
            gradient_accumulation_steps=self.cfg.grad_accum,
            learning_rate=self.cfg.lr,
            warmup_steps=int(total_steps * self.cfg.warmup_ratio),
            lr_scheduler_type="cosine",
            fp16=True,
            logging_steps=5,
            save_steps=50,
            save_total_limit=2,
            report_to="none",
        )

        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=dataset,
            data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8),
        )

        print("[人设训练] 开始训练…")
        trainer.train()
        model.save_pretrained(str(self.save_dir))
        tokenizer.save_pretrained(str(self.save_dir))
        print(f"[人设训练] 完成！权重已保存 → {self.save_dir}")


# ════════════════════════════════════════════
# CLI 入口
# ════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Elder AI 训练工具")
    subparsers = parser.add_subparsers(dest="task")

    # 情感分类训练
    ep = subparsers.add_parser("emotion", help="训练情感分类模型")
    ep.add_argument("--data",    required=True, help="训练数据 JSONL 路径")
    ep.add_argument("--epochs",  type=int, default=10)
    ep.add_argument("--batch",   type=int, default=32)
    ep.add_argument("--lr",      type=float, default=2e-4)

    # 人设微调训练
    pp = subparsers.add_parser("persona", help="人设 LoRA 微调")
    pp.add_argument("--persona", required=True, help="人设 ID")
    pp.add_argument("--data",    required=True, help="训练数据 JSONL 路径")
    pp.add_argument("--model",   default="Qwen/Qwen2.5-1.5B-Instruct")
    pp.add_argument("--epochs",  type=int, default=3)
    pp.add_argument("--batch",   type=int, default=4)

    args = parser.parse_args()

    if args.task == "emotion":
        EmotionTrainer(args.data, args.epochs, args.batch, args.lr).train()

    elif args.task == "persona":
        cfg = PersonaTrainConfig(
            persona_id=args.persona,
            data_path=args.data,
            model_name=args.model,
            epochs=args.epochs,
            batch_size=args.batch,
        )
        PersonaTrainer(cfg).train()

    else:
        parser.print_help()
