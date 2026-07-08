# WALL-E 音色克隆接入说明

## 架构

当前实现按“台式机处理、树莓派播放”的方式设计：

```text
Web 上传参考音频
  -> Spring Boot 保存音色档案和样本路径
  -> D:\WALL-E\voice-service 调用 GPT-SoVITS 本地 API 合成 WAV
  -> Spring Boot 将 WAV 转成 PCM
  -> 推到树莓派 tts_stream_player.py:6007 播放
```

树莓派不跑模型，只负责播放。模型、样本、缓存默认都放在 `D:\WALL-E` 项目内。

## D 盘目录

- `D:\WALL-E\voice-service`：WALL-E 音色服务
- `D:\WALL-E\voice-service\.venv`：WALL-E 音色服务虚拟环境
- `D:\WALL-E\models\GPT-SoVITS`：GPT-SoVITS 代码、虚拟环境和权重
- `D:\WALL-E\models\huggingface`：Hugging Face 缓存
- `D:\WALL-E\models\torch`：PyTorch 缓存
- `D:\WALL-E\data\voice-profiles`：用户上传的参考音频
- `D:\WALL-E\logs\voice-service`：GPT-SoVITS API 和 voice-service 日志

## 安装

```powershell
cd D:\WALL-E
.\scripts\install-gpt-sovits-cpu.ps1
```

脚本只下载 GPT-SoVITS v2 中文零样本推理所需文件，不下载 UVR5、ASR、v3/v4/v2Pro 等附加模型。

## 启动

```powershell
cd D:\WALL-E
.\scripts\start-voice-service.ps1
```

启动后：

- `http://127.0.0.1:7862`：WALL-E voice-service
- `http://127.0.0.1:9880`：GPT-SoVITS API

Spring Boot 通过系统配置 `voice.service-url=http://127.0.0.1:7862` 调用 voice-service。

## Web 使用

1. 进入 Web 侧栏的“音色克隆”。
2. 上传 3-10 秒干净人声参考音频。
3. 填写参考音频对应文字稿。
4. 模型模式选择 `GPT-SoVITS`。
5. 保存音色后，可在页面试听，或发送到已绑定的树莓派设备。

本地开发时如果要让前端连接备用后端端口，例如 `18080`：

```powershell
cd D:\Projects\WALL-E\Software-web
$env:VITE_API_PROXY_TARGET='http://127.0.0.1:18080'
$env:VITE_API_BASE_URL='/api'
npm run dev -- --host 127.0.0.1 --port 5173
```

`VITE_API_BASE_URL=/api` 会强制浏览器走 Vite 代理，避免公共系统配置里的线上或旧后端地址覆盖本地验证地址。

## 约束

- 当前落地的是 GPT-SoVITS v2 零样本克隆，不对每个音色做耗时微调。
- 这台机器的 GTX 750 Ti 不适合作为 CUDA 推理/训练主力，所以脚本强制 CPU + fp32。
- CPU 合成会慢，短句更适合硬件实时播报。
- 如果参考音频不在 3-10 秒范围内，GPT-SoVITS 会拒绝合成。

## 安全建议

上线前建议增加：

- 上传音频授权确认。
- 音色创建者和使用者绑定。
- 删除音色时同步清理样本和档案目录。
- 合成日志只记录必要状态，不记录敏感文本。
