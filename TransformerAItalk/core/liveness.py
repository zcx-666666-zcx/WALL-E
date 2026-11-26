"""
面部活体检测模块（Face Liveness Detection）
────────────────────────────────────────────────────────────────
架构：
  · DACAN 模型（ResNeXt + DACA 通道注意力）
  · 输入：BGR 人脸图片
  · 输出：is_real (bool) + confidence (float)

两种状态：
  1. 权重未就绪 → predict() 返回 error 状态
  2. 权重已加载 → 正常推理

模型权重放在 data/checkpoints/liveness/ 目录下。
"""

from __future__ import annotations
import os
import sys
import numpy as np
import cv2
import torch
import torch.nn.functional as F
from pathlib import Path
from typing import NamedTuple
from config.settings import LIVENESS_MODEL_PATH, LIVENESS_IMAGE_SIZE, LIVENESS_THRESHOLD


RESIZE_SIZE = 112


class LivenessResult(NamedTuple):
    ok: bool              # 推理是否成功
    is_real: bool         # 是否真人
    confidence: float     # 置信度 0~1
    threshold: float      # 判定阈值
    error: str = ""       # 错误信息（ok=False 时）

    def to_dict(self) -> dict:
        if not self.ok:
            return {"status": "no_model", "detail": self.error}
        return {
            "is_real": self.is_real,
            "confidence": round(self.confidence, 6),
            "threshold": self.threshold,
        }


# ════════════════════════════════════════════
# 图像预处理（来自 RGB2 inference.py）
# ════════════════════════════════════════════

def _center_crop(image, target_size):
    h, w = image.shape[:2]
    start_x = (w - target_size) // 2
    start_y = (h - target_size) // 2
    return image[start_y:start_y + target_size, start_x:start_x + target_size]


def _nine_crops(image, target_size):
    h, w = image.shape[:2]
    cx, cy = (w - target_size) // 2, (h - target_size) // 2
    offsets = [
        (0, 0),
        (w - target_size, 0),
        (0, h - target_size),
        (w - target_size, h - target_size),
        (cx, cy),
    ]
    crops = []
    for ox, oy in offsets:
        ox = max(0, min(ox, w - target_size))
        oy = max(0, min(oy, h - target_size))
        crop = image[oy:oy + target_size, ox:ox + target_size]
        crops.append(crop)
        crops.append(cv2.flip(crop, 1))
    return np.stack(crops, axis=0)


def _preprocess(image_bgr, image_size, use_tta=False):
    image = cv2.resize(image_bgr, (RESIZE_SIZE, RESIZE_SIZE))
    if use_tta:
        crops = _nine_crops(image, image_size)
    else:
        crop = _center_crop(image, image_size)
        crops = np.expand_dims(crop, axis=0)
    crops = np.transpose(crops, (0, 3, 1, 2)).astype(np.float32) / 255.0
    return torch.FloatTensor(crops)


# ════════════════════════════════════════════
# 活体检测器
# ════════════════════════════════════════════

class LivenessDetector:
    """
    面部活体检测器
    自动选择：有权重 → 神经网络推理；无权重 → 返回错误
    """

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self._ready = False
        self._error = ""
        self._try_load_model()

    def _try_load_model(self):
        model_path = LIVENESS_MODEL_PATH
        if not os.path.exists(str(model_path)):
            self._error = (
                f"Checkpoint not found: {model_path}\n"
                "Train the model first:\n"
                "  python train_single.py --model DACAN --image_mode color --image_size 48\n"
                "Or place a trained .pth file at the path above."
            )
            print(f"[活体检测] {self._error}")
            return

        try:
            from models.dacan import Net
            self.model = Net(num_class=2, type='D')
            state_dict = torch.load(str(model_path), map_location=self.device)

            if any(k.startswith("module.") for k in state_dict):
                from collections import OrderedDict
                new_state = OrderedDict()
                for k, v in state_dict.items():
                    new_state[k.replace("module.", "")] = v
                state_dict = new_state

            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            self._ready = True
            print(f"[活体检测] 已加载模型权重 ({self.device})")
        except Exception as e:
            self._error = f"Failed to load model: {e}"
            print(f"[活体检测] {self._error}")

    def predict(self, image, use_tta=False) -> LivenessResult:
        """
        对输入图片进行活体检测。

        Args:
            image: 文件路径(str)、numpy数组(H,W,3 BGR)、或 bytes
            use_tta: 是否使用 10-crop 测试时增强

        Returns:
            LivenessResult
        """
        if not self._ready:
            return LivenessResult(ok=False, is_real=False, confidence=0.,
                                  threshold=LIVENESS_THRESHOLD, error=self._error)

        if isinstance(image, str):
            img = cv2.imread(image, 1)
            if img is None:
                return LivenessResult(ok=False, is_real=False, confidence=0.,
                                      threshold=LIVENESS_THRESHOLD,
                                      error=f"Cannot read image: {image}")
        elif isinstance(image, bytes):
            arr = np.frombuffer(image, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        elif isinstance(image, np.ndarray):
            img = image.copy()
        else:
            return LivenessResult(ok=False, is_real=False, confidence=0.,
                                  threshold=LIVENESS_THRESHOLD,
                                  error=f"Unsupported image type: {type(image)}")

        tensor = _preprocess(img, LIVENESS_IMAGE_SIZE, use_tta=use_tta)
        tensor = tensor.to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            logits = torch.mean(logits, dim=0, keepdim=True)
            probs = F.softmax(logits, dim=1)
            confidence = probs[0, 1].item()

        return LivenessResult(
            ok=True,
            is_real=confidence >= LIVENESS_THRESHOLD,
            confidence=confidence,
            threshold=LIVENESS_THRESHOLD,
        )
