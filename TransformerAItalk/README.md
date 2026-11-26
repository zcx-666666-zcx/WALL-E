# 🌸 Elder AI — 适老化情感陪伴系统

纯 Python 实现，面向产品化，终端可直接调试，预留前端 API 接口。

---

## 📁 项目结构

```
elder_ai/
├── config/
│   └── settings.py              ← 所有配置集中管理（模型、路径、参数）
├── core/
│   ├── emotion.py               ← 情感检测 Transformer（8分类）
│   └── engine.py                ← 对话引擎（流式生成 + LoRA热切换）
├── personas/
│   └── persona_manager.py       ← 人设管理（内置3个 + 自定义）
├── memory/
│   └── user_memory.py           ← 用户长期记忆（持久化 JSON）
├── training/
│   └── trainer.py               ← 情感分类 & 人设 LoRA 微调训练器
├── cli/
│   └── terminal.py              ← 终端调试界面（彩色 + 流式）
├── api/
│   └── server.py                ← FastAPI REST + WebSocket（预留前端）
├── data/
│   ├── train/
│   │   ├── emotion_train.jsonl  ← 情感分类训练数据
│   │   └── grandma_chen.jsonl  ← 人设对话训练数据
│   ├── memory/                  ← 用户记忆（自动生成）
│   ├── personas/                ← 自定义人设（自动生成）
│   └── checkpoints/             ← 训练权重（自动生成）
└── requirements.txt
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动终端对话（演示模式，无需 GPU）

```bash
cd elder_ai
python -m cli.terminal --demo
```

### 启动终端对话（真实模型）

```bash
python -m cli.terminal --persona grandma_chen --user 用户001
```

### 可选参数

```
--demo          演示模式（无需GPU，使用规则回复）
--persona <id>  初始人设（默认 grandma_chen）
--user <id>     用户ID（用于记忆持久化）
--debug         显示情感检测等调试信息
```

---

## 💬 终端命令

| 命令 | 说明 |
|------|------|
| `/help` | 查看所有命令 |
| `/persona` | 列出所有可用人设 |
| `/persona <id>` | 切换人设 |
| `/new_persona` | 交互式创建自定义人设 |
| `/memory` | 查看用户记忆画像 |
| `/memory set` | 编辑用户信息（姓名/年龄/地区） |
| `/emotion` | 查看上一条消息的情感检测结果 |
| `/history` | 查看本轮对话历史 |
| `/clear` | 清空本轮对话历史 |
| `/stats` | 情感趋势统计图 |
| `/debug` | 切换调试信息显示 |
| `/user <id>` | 切换用户 |
| `/train emotion` | 触发情感模型训练 |
| `/train persona` | 触发人设 LoRA 微调 |
| `/quit` | 保存并退出 |

---

## 🤖 架构说明

### 情感检测（Transformer）
- 自定义 4 层 Transformer Encoder，参数量约 3M
- 输出 8 类情感：孤独 / 开心 / 悲伤 / 焦虑 / 平静 / 思念 / 愤怒 / 困惑
- 冷启动（无训练数据）时自动使用规则辅助模式
- 训练后自动加载神经网络模型

### 人设系统
- 每个人设包含：背景故事、性格、说话风格、口头禅、感兴趣话题、禁忌话题
- System Prompt 自动生成，无需手写
- 支持通过终端命令或 API 动态创建/删除

### 长期记忆
- 每用户独立 JSON 文件，永久保存
- 记录：姓名/年龄/家庭/健康/兴趣/情感历史/最近话题
- 自动提炼"记忆摘要"注入 Prompt，越聊越懂老人

### 对话引擎
- 基础模型：Qwen2.5（支持 4-bit 量化）
- LoRA 人设适配器热切换（不重加载基础模型）
- 无 GPU 自动降级演示模式

---

## 🎓 训练

### 训练情感分类模型

```bash
# 数据格式：{"text": "我很孤独", "label": "孤独"}
python -m training.trainer emotion \
  --data data/train/emotion_train.jsonl \
  --epochs 10
```

### 训练人设 LoRA 适配器

```bash
# 数据格式：{"instruction": "你好", "response": "哎呀你来啦！"}
python -m training.trainer persona \
  --persona grandma_chen \
  --data data/train/grandma_chen.jsonl \
  --epochs 3
```

也可以直接在终端里触发：
```
/train emotion --data data/train/emotion_train.jsonl
/train persona --persona grandma_chen --data data/train/grandma_chen.jsonl
```

---

## 🔌 启动 API 服务（前端对接）

```bash
python -m api.server
# 或
uvicorn api.server:app --reload --port 8000
```

API 文档自动生成：http://localhost:8000/docs

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/personas` | 获取所有人设 |
| `POST` | `/personas` | 创建自定义人设 |
| `POST` | `/chat/send` | 普通对话 |
| `POST` | `/chat/stream` | SSE 流式对话（Vue/React） |
| `WS` | `/ws/{user_id}` | WebSocket 实时对话 |
| `GET` | `/memory/{user_id}` | 获取用户记忆 |
| `PUT` | `/memory/{user_id}` | 更新用户信息 |
| `GET` | `/memory/{user_id}/stats` | 情感趋势统计 |

---

## ⚙️ 修改配置

所有核心参数集中在 `config/settings.py`：

```python
BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"  # 换模型改这里
USE_4BIT_QUANT = True                        # 显存不够开这个
MAX_NEW_TOKENS = 200                         # 回复长度
TEMPERATURE = 0.82                           # 创造性（越高越随机）
MAX_HISTORY_TURNS = 15                       # 记忆的对话轮数
```

---

## 📌 推荐模型

| 模型 | 显存 | 适用场景 |
|------|------|---------|
| `Qwen2.5-0.5B-Instruct` | CPU / 2GB | 调试验证 |
| `Qwen2.5-1.5B-Instruct` | 4GB VRAM | 开发测试（推荐） |
| `Qwen2.5-7B-Instruct` | 8GB VRAM | 产品上线 |
| `Qwen2.5-14B-Instruct` | 16GB VRAM | 高质量生产 |
