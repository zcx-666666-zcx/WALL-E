from pathlib import Path
import os

# ────────────────────────────────────────────
# 路径
# ────────────────────────────────────────────
ROOT_DIR      = Path(__file__).resolve().parent.parent
DATA_DIR      = ROOT_DIR / "data"
MEMORY_DIR    = DATA_DIR / "memory"          # 用户长期记忆存储
PERSONA_DIR   = DATA_DIR / "personas"        # 自定义人设存储
CHECKPOINT_DIR= DATA_DIR / "checkpoints"     # LoRA 微调权重
TRAIN_DIR     = DATA_DIR / "train"           # 训练数据

for d in [MEMORY_DIR, PERSONA_DIR, CHECKPOINT_DIR, TRAIN_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ────────────────────────────────────────────
# 模型
# ────────────────────────────────────────────
#   "Qwen/Qwen2.5-0.5B-Instruct"   → CPU / 2GB RAM，速度较慢
#   "Qwen/Qwen2.5-1.5B-Instruct"   → 4-bit GPU，4GB VRAM，推荐调试
#   "Qwen/Qwen2.5-7B-Instruct"     → 4-bit GPU，8GB VRAM，产品质量
#   "Qwen/Qwen2.5-14B-Instruct"     → 4-bit GPU，14GB VRAM，高级推理
BASE_MODEL = os.environ.get("WALLE_BASE_MODEL", "Qwen/Qwen2.5-14B-Instruct")
STT_MODEL = os.environ.get("WALLE_STT_MODEL", "iic/SenseVoiceSmall")

USE_4BIT_QUANT  = os.environ.get("WALLE_USE_4BIT", "1") == "1"
USE_FLASH_ATTN  = False   # Flash Attention 2（需要 A100/H100）
MAX_NEW_TOKENS  = 250     # 每次回复最大 token 数
TEMPERATURE     = 0.82    # 温度（越高越随机，老人陪伴建议 0.8-0.9）
TOP_P           = 0.90
REPETITION_PENALTY = 1.12

# ────────────────────────────────────────────
# 联网API
# ────────────────────────────────────────────
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
SEARCH_ENABLED = bool(TAVILY_API_KEY)
SEARCH_TRIGGER_KEYWORDS = [    # 触发联网的关键词
    "新闻", "动态", "简报", "头条", "发生", "进展", "比赛结果", 
    "股价", "汇率", "天气", "气温", "预报", "油价", "金价", "报道",
    "多少钱", "价格", "怎么走", "地图", "地址", "电话", "导航", "股票"
    "挂号", "医保政策", "最新规定", "养老金", "补漏", "药效", "副作用",
    "几号", "星期几", "年份", "几点", "什么时候", "节气", "节日", "世界杯"
]

# ────────────────────────────────────────────
# LoRA 微调
# ────────────────────────────────────────────
LORA_R          = 16
LORA_ALPHA      = 32
LORA_DROPOUT    = 0.05
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"]

# ────────────────────────────────────────────
# 对话管理
# ────────────────────────────────────────────
MAX_HISTORY_TURNS = 50    # 保留最近 N 轮对话作为上下文
EMOTION_THRESHOLD = 0.42  # 情感置信度超过此值才触发干预提示

# ────────────────────────────────────────────
# 活体检测
# ────────────────────────────────────────────
LIVENESS_MODEL_PATH = CHECKPOINT_DIR / "liveness" / "global_min_acer_model.pth"
LIVENESS_IMAGE_SIZE = 48
LIVENESS_THRESHOLD  = 0.99

# ────────────────────────────────────────────
# API 服务（预留）
# ────────────────────────────────────────────
API_HOST = "0.0.0.0"
API_PORT = 6006

# ────────────────────────────────────────────
# TTS 语音合成（GPT-SoVITS）
# ────────────────────────────────────────────
# TTS 模型位于 TransformerAItalk 内部的 TTS/ 目录下
# 部署时须将 GPT-SoVITS 放入此目录（或设置 TTS_ROOT 环境变量）
TTS_ROOT          = Path(os.environ.get("TTS_ROOT", ROOT_DIR / "TTS"))
TTS_CONFIG_YAML   = TTS_ROOT / "GPT_SoVITS" / "configs" / "tts_infer.yaml"
TTS_VERSION       = os.environ.get("TTS_VERSION", "v2")
TTS_DEVICE        = os.environ.get("TTS_DEVICE", "cuda")
TTS_IS_HALF       = os.environ.get("TTS_IS_HALF", "1") == "1"

# 参考音频（人设专属 > 默认）
REF_AUDIO_DIR     = DATA_DIR / "ref_audio"
DEFAULT_REF_AUDIO = REF_AUDIO_DIR / "default_ref.wav"
DEFAULT_REF_TEXT  = "大家好，我是你的智能陪伴助手，有什么可以帮你的吗？"

# TTS 输出目录
TTS_OUTPUT_DIR    = DATA_DIR / "tts_output"

for d in [REF_AUDIO_DIR, TTS_OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)
