"""
DPO 训练模块（Direct Preference Optimization，直接偏好优化）
────────────────────────────────────────────────────────────────
DPO 是 RLHF 的简化版：
  · 不需要单独训练奖励模型
  · 不需要跑 PPO
  · 只需要"好回复 vs 坏回复"的对比数据
  · 用数学方法直接把偏好信息编进语言模型

训练数据格式（JSONL，每行一条）：
{
  "instruction": "我今天很孤独",
  "chosen":   "找我嘛，我陪你。",        ← 好回复（你希望模型说的）
  "rejected": "孤独是正常的，每个人都会有。"  ← 坏回复（你不希望说的）
}

使用方式：
    python -m training.dpo_trainer --persona well_E --data data/train/well_E_dpo.jsonl
    python -m training.dpo_trainer --persona well_E --data data/train/well_E_dpo.jsonl --epochs 2 --beta 0.1
"""

from __future__ import annotations
import json
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from config.settings import CHECKPOINT_DIR, BASE_MODEL
from personas.persona_manager import PersonaManager


# ════════════════════════════════════════════
# DPO 数据集
# ════════════════════════════════════════════

class DPODataset(Dataset):
    """
    DPO 偏好数据集
    每条样本包含：instruction + chosen（好回复）+ rejected（坏回复）
    """

    def __init__(
        self,
        path: str | Path,
        tokenizer,
        system_prompt: str,
        max_len: int = 512,
    ):
        self.tokenizer = tokenizer
        self.system_prompt = system_prompt
        self.max_len = max_len
        self.samples = []

        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                # 验证字段完整
                if all(k in d for k in ("instruction", "chosen", "rejected")):
                    self.samples.append(d)

        print(f"[DPO数据] 加载 {len(self.samples)} 条偏好样本")

    def __len__(self):
        return len(self.samples)

    def _encode(self, instruction: str, response: str):
        """将 instruction+response 编码为 token ids，返回 input_ids 和 labels"""
        messages = [
            {"role": "system",    "content": self.system_prompt},
            {"role": "user",      "content": instruction},
            {"role": "assistant", "content": response},
        ]
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        enc = self.tokenizer(
            text,
            max_length=self.max_len,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        input_ids = enc["input_ids"].squeeze(0)
        attention_mask = enc["attention_mask"].squeeze(0)

        # labels：只对 response 部分计算 loss，其余设为 -100
        labels = input_ids.clone()
        resp_start = text.rfind(response)
        if resp_start != -1:
            prefix_ids = self.tokenizer(
                text[:resp_start], add_special_tokens=False
            )["input_ids"]
            labels[: len(prefix_ids)] = -100

        return input_ids, attention_mask, labels

    def __getitem__(self, idx):
        item = self.samples[idx]
        chosen_ids,  chosen_mask,  chosen_labels  = self._encode(item["instruction"], item["chosen"])
        rejected_ids, rejected_mask, rejected_labels = self._encode(item["instruction"], item["rejected"])
        return {
            "chosen_input_ids":      chosen_ids,
            "chosen_attention_mask": chosen_mask,
            "chosen_labels":         chosen_labels,
            "rejected_input_ids":    rejected_ids,
            "rejected_attention_mask": rejected_mask,
            "rejected_labels":       rejected_labels,
        }


# ════════════════════════════════════════════
# DPO Loss 计算
# ════════════════════════════════════════════

def dpo_loss(
    policy_chosen_logps:   torch.Tensor,
    policy_rejected_logps: torch.Tensor,
    ref_chosen_logps:      torch.Tensor,
    ref_rejected_logps:    torch.Tensor,
    beta: float = 0.1,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    DPO 损失函数
    ────────────────────────────────────────
    核心公式：
        loss = -log σ( β * (log π(chosen)/π_ref(chosen)
                          - log π(rejected)/π_ref(rejected)) )

    直觉解释：
        - 让模型对"好回复"的概率 相对于参考模型 提高
        - 让模型对"坏回复"的概率 相对于参考模型 降低
        - β 控制偏离参考模型的程度，越小越保守

    返回：loss, chosen_reward, rejected_reward
    """
    chosen_reward   = beta * (policy_chosen_logps   - ref_chosen_logps)
    rejected_reward = beta * (policy_rejected_logps - ref_rejected_logps)

    loss = -F.logsigmoid(chosen_reward - rejected_reward).mean()

    return loss, chosen_reward.mean(), rejected_reward.mean()


def compute_logps(
    model,
    input_ids:      torch.Tensor,
    attention_mask: torch.Tensor,
    labels:         torch.Tensor,
) -> torch.Tensor:
    """
    计算模型对特定回复的 log 概率（取 response 部分 token 的平均 log prob）
    """
    with torch.no_grad() if not model.training else torch.enable_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits  = outputs.logits  # (B, L, V)

    # shift: logits[:-1] 预测 labels[1:]
    shift_logits = logits[:, :-1, :]
    shift_labels = labels[:, 1:]

    log_probs = F.log_softmax(shift_logits, dim=-1)

    # 取实际 token 的 log prob
    token_log_probs = log_probs.gather(
        dim=-1,
        index=shift_labels.clamp(min=0).unsqueeze(-1)
    ).squeeze(-1)

    # mask 掉 -100 的位置（非 response 部分）
    valid_mask = (shift_labels != -100).float()
    per_sample_logps = (token_log_probs * valid_mask).sum(-1) / valid_mask.sum(-1).clamp(min=1)

    return per_sample_logps


# ════════════════════════════════════════════
# DPO 训练配置
# ════════════════════════════════════════════

@dataclass
class DPOTrainConfig:
    persona_id:  str
    data_path:   str | Path
    model_name:  str   = BASE_MODEL
    epochs:      int   = 2         # DPO 一般不需要太多 epoch
    batch_size:  int   = 2         # DPO 显存占用是 SFT 的 2 倍（policy + ref）
    lr:          float = 1e-5      # DPO 学习率要比 SFT 小
    beta:        float = 0.1       # 偏好强度，0.05-0.2 为合理范围
    max_len:     int   = 512
    grad_accum:  int   = 8


# ════════════════════════════════════════════
# DPO 训练器
# ════════════════════════════════════════════

class DPOTrainer:
    """
    DPO 训练器

    工作流程：
    1. 加载已有的 SFT LoRA 权重（作为 policy model）
    2. 复制一份冻结的参考模型（ref model）
    3. 用 DPO loss 优化 policy model，使其向偏好数据靠拢
    4. 保存更新后的 LoRA 权重（覆盖或另存）
    """

    def __init__(self, config: DPOTrainConfig):
        self.cfg = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sft_dir = CHECKPOINT_DIR / config.persona_id       # SFT 权重目录
        self.save_dir = CHECKPOINT_DIR / f"{config.persona_id}_dpo"  # DPO 权重目录

    def train(self):
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
        from peft import PeftModel, get_peft_model, LoraConfig, TaskType, prepare_model_for_kbit_training
        import copy

        # ── 检查 SFT 权重是否存在 ───────────────────
        if not self.sft_dir.exists():
            print(f"[DPO] ⚠ 未找到 SFT 权重 {self.sft_dir}")
            print("[DPO]   将从基础模型开始 DPO 训练（效果不如先跑 SFT）")

        pm = PersonaManager()
        persona = pm.get(self.cfg.persona_id)
        print(f"[DPO] 人设：{persona.name}  设备：{self.device}  β={self.cfg.beta}")

        # ── 加载 tokenizer ───────────────────────────
        tokenizer = AutoTokenizer.from_pretrained(self.cfg.model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # ── 加载数据集 ───────────────────────────────
        dataset = DPODataset(
            self.cfg.data_path, tokenizer,
            persona.system_prompt, self.cfg.max_len
        )
        if len(dataset) == 0:
            raise ValueError("数据集为空，请检查数据格式是否正确")

        loader = DataLoader(dataset, batch_size=self.cfg.batch_size, shuffle=True, num_workers=0)

        # ── 加载基础模型（4-bit 量化）────────────────
        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        base_model = AutoModelForCausalLM.from_pretrained(
            self.cfg.model_name,
            quantization_config=bnb,
            device_map="auto",
            trust_remote_code=True,
        )

        # ── Policy Model（带 LoRA，可训练）──────────
        if self.sft_dir.exists():
            print(f"[DPO] 加载 SFT 权重作为初始 policy → {self.sft_dir}")
            policy_model = PeftModel.from_pretrained(
                base_model, str(self.sft_dir), is_trainable=True
            )
        else:
            policy_model = prepare_model_for_kbit_training(base_model)
            from config.settings import LORA_R, LORA_ALPHA, LORA_DROPOUT, LORA_TARGET_MODULES
            lora_cfg = LoraConfig(
                task_type=TaskType.CAUSAL_LM, r=LORA_R, lora_alpha=LORA_ALPHA,
                lora_dropout=LORA_DROPOUT, target_modules=LORA_TARGET_MODULES, bias="none",
            )
            policy_model = get_peft_model(base_model, lora_cfg)

        # ── Reference Model（冻结，不更新）──────────
        # 使用相同的 SFT 权重，但完全冻结
        ref_base = AutoModelForCausalLM.from_pretrained(
            self.cfg.model_name,
            quantization_config=bnb,
            device_map="auto",
            trust_remote_code=True,
        )
        if self.sft_dir.exists():
            ref_model = PeftModel.from_pretrained(
                ref_base, str(self.sft_dir), is_trainable=False
            )
        else:
            ref_model = ref_base

        # 冻结参考模型所有参数
        for p in ref_model.parameters():
            p.requires_grad = False
        ref_model.eval()

        policy_model.train()
        print(f"[DPO] Policy 可训练参数：", end="")
        total = sum(p.numel() for p in policy_model.parameters() if p.requires_grad)
        print(f"{total:,}")

        # ── 优化器 ───────────────────────────────────
        optimizer = torch.optim.AdamW(
            [p for p in policy_model.parameters() if p.requires_grad],
            lr=self.cfg.lr,
            weight_decay=0.01,
        )
        total_steps = len(loader) * self.cfg.epochs // self.cfg.grad_accum
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_steps)

        # ── 训练循环 ─────────────────────────────────
        print(f"\n[DPO] 开始训练，共 {self.cfg.epochs} 个 epoch，{len(dataset)} 条样本")
        best_loss = float("inf")

        for epoch in range(1, self.cfg.epochs + 1):
            total_loss = 0.0
            total_chosen_r  = 0.0
            total_rejected_r = 0.0
            optimizer.zero_grad()
            t0 = time.time()

            for step, batch in enumerate(loader, 1):
                # 移动到设备
                chosen_ids    = batch["chosen_input_ids"].to(self.device)
                chosen_mask   = batch["chosen_attention_mask"].to(self.device)
                chosen_labels = batch["chosen_labels"].to(self.device)
                rejected_ids    = batch["rejected_input_ids"].to(self.device)
                rejected_mask   = batch["rejected_attention_mask"].to(self.device)
                rejected_labels = batch["rejected_labels"].to(self.device)

                # Policy model 的 log prob（需要梯度）
                policy_chosen_logps   = compute_logps(policy_model, chosen_ids,   chosen_mask,   chosen_labels)
                policy_rejected_logps = compute_logps(policy_model, rejected_ids, rejected_mask, rejected_labels)

                # Reference model 的 log prob（不需要梯度）
                with torch.no_grad():
                    ref_chosen_logps   = compute_logps(ref_model, chosen_ids,   chosen_mask,   chosen_labels)
                    ref_rejected_logps = compute_logps(ref_model, rejected_ids, rejected_mask, rejected_labels)

                # DPO loss
                loss, chosen_r, rejected_r = dpo_loss(
                    policy_chosen_logps, policy_rejected_logps,
                    ref_chosen_logps,    ref_rejected_logps,
                    beta=self.cfg.beta,
                )

                (loss / self.cfg.grad_accum).backward()
                total_loss += loss.item()
                total_chosen_r  += chosen_r.item()
                total_rejected_r += rejected_r.item()

                if step % self.cfg.grad_accum == 0:
                    nn.utils.clip_grad_norm_(policy_model.parameters(), 1.0)
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()

                # 进度显示
                if step % 10 == 0:
                    print(f"  epoch {epoch} step {step}/{len(loader)}"
                          f"  loss={loss.item():.4f}"
                          f"  chosen_r={chosen_r.item():.3f}"
                          f"  rejected_r={rejected_r.item():.3f}")

            avg_loss = total_loss / len(loader)
            avg_cr   = total_chosen_r  / len(loader)
            avg_rr   = total_rejected_r / len(loader)
            elapsed  = time.time() - t0

            print(f"\n  ✦ Epoch {epoch}/{self.cfg.epochs}"
                  f"  avg_loss={avg_loss:.4f}"
                  f"  chosen_reward={avg_cr:.3f}"
                  f"  rejected_reward={avg_rr:.3f}"
                  f"  {elapsed:.1f}s")

            # 判断训练是否正常：chosen_reward 应该 > rejected_reward
            if avg_cr > avg_rr:
                print(f"  ✓ 偏好方向正确（chosen_r > rejected_r）")
            else:
                print(f"  ⚠ 偏好方向异常，可能需要检查数据或调小 beta")

            if avg_loss < best_loss:
                best_loss = avg_loss
                policy_model.save_pretrained(str(self.save_dir))
                tokenizer.save_pretrained(str(self.save_dir))
                print(f"  ✓ 权重已保存 → {self.save_dir}")

        print(f"\n[DPO] 训练完成！最终权重保存在 {self.save_dir}")
        print(f"[DPO] 提示：如需替换原 SFT 权重，将 {self.save_dir} 内容复制到 {self.sft_dir}")


# ════════════════════════════════════════════
# CLI 入口
# ════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DPO 偏好训练")
    parser.add_argument("--persona", required=True,  help="人设 ID（如 well_E）")
    parser.add_argument("--data",    required=True,  help="DPO 数据路径（JSONL）")
    parser.add_argument("--model",   default=BASE_MODEL, help="基础模型")
    parser.add_argument("--epochs",  type=int,   default=2)
    parser.add_argument("--batch",   type=int,   default=2)
    parser.add_argument("--beta",    type=float, default=0.1,
                        help="偏好强度，越大越激进（建议 0.05-0.2）")
    parser.add_argument("--lr",      type=float, default=1e-5)
    args = parser.parse_args()

    cfg = DPOTrainConfig(
        persona_id=args.persona,
        data_path=args.data,
        model_name=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        beta=args.beta,
        lr=args.lr,
    )
    DPOTrainer(cfg).train()
