# 🌸 Elder AI — 老年人情感陪护系统

基于 Transformer + LoRA 微调 + FastAPI + Vue 3 构建的老年人情感陪护 AI。

---

## 📁 项目结构

```
elder-ai/
├── backend/
│   ├── main.py                    # FastAPI 主入口 + WebSocket
│   ├── requirements.txt           # Python 依赖
│   ├── train.py                   # 人设微调训练脚本
│   ├── api/
│   │   ├── chat.py                # 对话 REST/SSE 接口
│   │   └── persona.py             # 人设管理接口
│   ├── models/
│   │   ├── ai_model.py            # 核心模型（Transformer + 情感检测 + 记忆）
│   │   └── conversation_manager.py # 对话会话管理
│   └── data/
│       └── train_data.jsonl       # 示例训练数据
└── frontend/
    └── src/
        └── components/
            └── ElderChat.vue      # Vue 3 聊天界面
```

---

## 🚀 快速启动

### 后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务（演示模式，无需 GPU）
python main.py

# 服务地址：http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 前端（Vue 3）

```bash
cd frontend

# 新建 Vue 项目（如果还没有）
npm create vue@latest . -- --yes

# 将 ElderChat.vue 放入 src/components/
# 在 App.vue 中引入：
# <ElderChat />

npm install
npm run dev
# 访问：http://localhost:5173
```

---

## 🤖 核心架构

### 1. 情感感知对话（ai_model.py）

```
用户输入
  ↓
EmotionDetector（Transformer 情感分类）
  ↓
情感标签 → 注入 System Prompt
  ↓
LLM 生成（Qwen / DeepSeek）
  ↓
流式输出 → WebSocket → Vue 前端
```

### 2. 人设系统

- **内置人设**：陈奶奶（温柔型）、李大爷（幽默型）
- **自定义人设**：通过 API 创建，自动生成 System Prompt
- **人设微调**：LoRA 训练，让模型深度学习特定说话风格

### 3. 长期记忆（UserMemory）

每个用户有独立的 JSON 记忆文件，记录：
- 姓名、年龄、家庭成员
- 兴趣爱好、健康备注
- 近期情感历史（用于个性化回复）
- 重要日期（生日等）

---

## 🎓 人设微调训练

```bash
# 准备训练数据（data/train_data.jsonl）：
# {"instruction": "你好", "response": "哎呀，你来啦！..."}

# 运行训练
python train.py \
  --persona grandma_chen \
  --data ./data/train_data.jsonl \
  --model Qwen/Qwen2.5-1.5B-Instruct \
  --epochs 3

# 训练好的 LoRA 权重保存在 ./checkpoints/grandma_chen/
```

---

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| WebSocket | `/ws/{user_id}` | 实时流式对话 |
| POST | `/api/chat/send` | 普通对话（完整返回） |
| POST | `/api/chat/stream` | SSE 流式对话 |
| GET  | `/api/chat/history/{user_id}` | 获取历史 |
| GET  | `/api/persona/list` | 列出所有人设 |
| POST | `/api/persona/create` | 创建自定义人设 |

---

## 🔧 生产部署建议

### 模型选择

| 场景 | 推荐模型 | 显存需求 |
|------|---------|---------|
| 轻量/CPU | Qwen2.5-0.5B-Instruct | 2GB RAM |
| 普通 GPU | Qwen2.5-1.5B-Instruct + 4-bit | 4GB VRAM |
| 高质量 | Qwen2.5-7B-Instruct + 4-bit | 8GB VRAM |

### 开启真实模型

在 `models/conversation_manager.py` 中取消注释：
```python
_model_instance.initialize(use_quantization=True)
```

### 接入大型对话数据集

推荐数据集：
- **LCCC**（中文对话）：https://github.com/thu-coai/CDial-GPT
- **BELLE**（指令对话）：https://github.com/LianjiaTech/BELLE
- **自建数据**：收集真实老年人对话，效果最佳

---

## 💡 扩展方向

- [ ] 语音输入/输出（老人更习惯语音）
- [ ] 接入家属端（家人可查看情感状态报告）
- [ ] 提醒功能（吃药、体检等）
- [ ] 多模态（识别老人表情/状态）
- [ ] 紧急情况检测（检测到异常情绪自动通知家属）
