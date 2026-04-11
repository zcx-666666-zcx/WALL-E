"""
人设微调训练脚本
使用 LoRA + SFT（监督微调）训练特定人设的说话风格
数据集格式：JSONL，每行一个对话样本
"""

import json
import torch
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrainConfig:
    """训练配置"""
    model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"
    persona_id: str = "grandma_chen"
    data_path: str = "./data/train_data.jsonl"   # 训练数据路径
    output_dir: str = "./checkpoints"
    
    # LoRA 参数
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    
    # 训练参数
    num_epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 2e-4
    max_length: int = 512
    warmup_ratio: float = 0.1
    save_steps: int = 100
    
    # 量化
    use_4bit: bool = True


def load_dataset_from_jsonl(data_path: str) -> Dataset:
    """
    加载训练数据
    
    数据格式示例（data/train_data.jsonl）:
    {"instruction": "你好", "response": "哎呀，你来啦！今天吃饭了没有呀？"}
    {"instruction": "我最近心情不好", "response": "嗯，奶奶听着呢，跟我说说发生什么事了？"}
    """
    data = []
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    
    logger.info(f"加载训练数据 {len(data)} 条")
    return Dataset.from_list(data)


def format_sample(sample: dict, tokenizer, persona_system_prompt: str, max_length: int):
    """将训练样本格式化为模型输入"""
    messages = [
        {"role": "system", "content": persona_system_prompt},
        {"role": "user", "content": sample["instruction"]},
        {"role": "assistant", "content": sample["response"]},
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )
    
    encoded = tokenizer(
        text,
        truncation=True,
        max_length=max_length,
        padding="max_length",
        return_tensors="pt"
    )
    
    input_ids = encoded["input_ids"][0]
    labels = input_ids.clone()
    
    # 只对 assistant 的回复部分计算 loss
    # 找到 assistant 回复的起始位置
    response_start = text.find(sample["response"])
    if response_start != -1:
        response_tokens = tokenizer(text[:response_start], return_tensors="pt")["input_ids"].shape[1]
        labels[:response_tokens] = -100  # 忽略 instruction 部分的 loss
    
    return {
        "input_ids": input_ids,
        "attention_mask": encoded["attention_mask"][0],
        "labels": labels
    }


def train(config: TrainConfig):
    """主训练函数"""
    
    # 1. 加载人设配置
    from models.ai_model import PersonaConfig
    persona = PersonaConfig.get(config.persona_id)
    system_prompt = persona["system_prompt"]
    logger.info(f"训练人设: {persona['name']}")
    
    # 2. 加载 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_name,
        trust_remote_code=True,
        padding_side="right"
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # 3. 加载数据集
    raw_dataset = load_dataset_from_jsonl(config.data_path)
    
    # 4. 数据预处理
    def preprocess(sample):
        return format_sample(sample, tokenizer, system_prompt, config.max_length)
    
    dataset = raw_dataset.map(preprocess, remove_columns=raw_dataset.column_names)
    
    # 5. 加载基础模型（4-bit 量化）
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=config.use_4bit,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    ) if config.use_4bit else None
    
    model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    if config.use_4bit:
        model = prepare_model_for_kbit_training(model)
    
    # 6. 应用 LoRA
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # 7. 训练参数
    output_path = f"{config.output_dir}/{config.persona_id}"
    training_args = TrainingArguments(
        output_dir=output_path,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=4,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        lr_scheduler_type="cosine",
        fp16=True,
        logging_steps=10,
        save_steps=config.save_steps,
        save_total_limit=3,
        report_to="none",
        dataloader_num_workers=2,
    )
    
    # 8. 开始训练
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8),
    )
    
    logger.info("开始训练...")
    trainer.train()
    
    # 9. 保存 LoRA 权重
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    logger.info(f"训练完成！模型已保存至 {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="人设微调训练")
    parser.add_argument("--persona", default="grandma_chen", help="人设 ID")
    parser.add_argument("--data", default="./data/train_data.jsonl", help="训练数据路径")
    parser.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct", help="基础模型")
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()
    
    config = TrainConfig(
        model_name=args.model,
        persona_id=args.persona,
        data_path=args.data,
        num_epochs=args.epochs,
    )
    train(config)
