# WALL-E 居家陪护机器人

WALL-E 是一套面向**居家陪护场景**的机器人系统，围绕「**监测 → 告警 → 联系 → 遥控**」闭环工作：机器人端采集心率、体温、湿度、呼吸、跌倒等体征与环境数据，家属通过微信小程序 / Web 控制台远程查看健康数据、管理日程提醒、发起视频通话并遥控机器人，同时具备 AI 陪伴与语音合成能力。

## 整体架构

| 模块 | 目录 | 说明 | 主要技术 |
|------|------|------|----------|
| 机器人端 | [`Hardware-pi/`](Hardware-pi) | 运行在树莓派上：体征/环境传感器采集、MQTT 消息、摄像头推流与 WebRTC 视频通话、TTS 音频播放、本地 UI 与远程控制 | Python |
| 后端服务 | [`Software-back/`](Software-back) | 用户、事件、联系人、设备、指令的管理 API；本地开发使用 Docker MySQL | Spring Boot |
| Web 控制台 | [`Software-web/`](Software-web) | 浏览器端管理界面（Vite 开发代理默认转发到后端 8080 端口） | Vue 3 + Vite |
| 微信小程序 | [`Software-miniprogram/`](Software-miniprogram) | 家属/监护人的移动端控制台：查看体征、日程提醒、视频通话、遥控与 AI 陪伴调试 | 微信小程序 |
| 语音服务 | [`voice-service/`](voice-service) | 运行在台式机上：音色档案预处理与 GPT-SoVITS 语音合成，对外提供 HTTP API，树莓派只负责播放 | Python + GPT-SoVITS |
| 硬件演示 | [`hardware-demo/`](hardware-demo) | 硬件功能演示程序 | — |
| 脚本工具 | [`scripts/`](scripts) | 环境安装、服务启动等 PowerShell 脚本 | PowerShell |

## 快速开始

### 后端（Software-back）

```bash
cd Software-back
docker compose up -d mysql   # 默认创建 cpnrobot 库，管理员账号 admin / admin123
```

后端默认连接 `jdbc:mysql://localhost:3307/cpnrobot`，端口或密码不同时通过环境变量覆盖，无需改代码。详见 [Software-back/README.md](Software-back/README.md)。

### Web 控制台（Software-web）

```bash
cd Software-web
npm install
npm run dev   # 如后端不在本机：VITE_API_PROXY_TARGET=http://后端地址:8080 npm run dev
```

### 语音服务（voice-service）

```powershell
.\scripts\install-gpt-sovits-cpu.ps1   # 安装 GPT-SoVITS CPU 推理环境（仅 v2 中文零样本所需）
.\scripts\start-voice-service.ps1      # 启动，服务地址 http://127.0.0.1:7862
```

详见 [voice-service/README.md](voice-service/README.md)。

## 更多文档

- [doc/项目功能说明.md](doc/项目功能说明.md) — 功能列表与数据库表结构
- [doc/接口文档.md](doc/接口文档.md) — API 接口文档
- [doc/后端开发日志.md](doc/后端开发日志.md) / [doc/前端说明.md](doc/前端说明.md)
- [doc/Windows日常部署.md](doc/Windows日常部署.md) — 部署指南
- [doc/西门子杯规划/](doc/西门子杯规划)、[doc/比赛硬件兜底模拟器.md](doc/比赛硬件兜底模拟器.md) — 比赛相关
- [docs/voice-clone.md](docs/voice-clone.md) — 音色克隆说明
