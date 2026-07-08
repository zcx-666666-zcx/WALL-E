# WALL-E voice-service

这个服务运行在台式机上，负责音色档案预处理和语音合成。Java 后端保存音色档案，并调用这里的 HTTP API；树莓派只负责播放台式机推过去的 PCM 音频。

默认目录都在 D 盘项目内：

- 样本和合成缓存：`D:/WALL-E/data`
- Python 服务：`D:/WALL-E/voice-service`
- GPT-SoVITS 代码和模型：`D:/WALL-E/models/GPT-SoVITS`
- Hugging Face / PyTorch / pip 缓存：`D:/WALL-E/models`

## 安装 GPT-SoVITS CPU 推理环境

```powershell
cd D:\WALL-E
.\scripts\install-gpt-sovits-cpu.ps1
```

这个脚本只安装 v2 中文零样本推理所需的依赖和权重，不下载 UVR5、ASR、v3/v4/v2Pro 等暂时不参与硬件朗读的模型。

## 启动

```powershell
cd D:\WALL-E
.\scripts\start-voice-service.ps1
```

默认会启动两个本地服务：

- WALL-E voice-service：`http://127.0.0.1:7862`
- GPT-SoVITS API：`http://127.0.0.1:9880`

日志写到 `D:/WALL-E/logs/voice-service`。

## 引擎

- `gpt_sovits`：默认引擎，调用本机 GPT-SoVITS API 做零样本音色克隆。
- `zero_shot`：开发占位，用于只验证 Web/Java/树莓派链路。
- `voxcpm`：保留入口，当前机器不适合作为主方案。

GPT-SoVITS v2 参考音频建议使用 3-10 秒干净人声，并填写对应文字稿。
