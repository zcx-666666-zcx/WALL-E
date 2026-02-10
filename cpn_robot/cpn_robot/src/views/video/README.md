# VideoCallProject - WebRTC 视频通话系统

## 项目概述

VideoCallProject 是一个基于 WebRTC 技术的实时视频通话系统，包含信令服务器、Web 客户端和树莓派客户端。该项目实现了点对点的视频通话功能，支持多房间管理和 NAT 穿透。

## 项目架构

### 1. 信令服务器 (server.py)
- 基于 `aiohttp` 和 `python-socketio` 构建
- 提供 WebSocket 连接和消息转发功能
- 支持多房间管理，通过手动维护用户房间映射实现
- 处理用户连接、断开、加入房间和消息转发逻辑

### 2. 树莓派客户端 (pi_client.py)
- 专为树莓派摄像头设计的视频通话客户端
- 使用 `aiortc` 库实现 WebRTC 功能
- 自动捕获摄像头视频流并传输到远端
- 支持 STUN 服务器以实现 NAT 穿透
- 包含自动重连和错误处理机制

### 3. Web 视频客户端 (video_client.html)
- 基于浏览器的视频通话界面
- 提供本地和远程视频预览功能
- 支持用户加入房间、发起视频通话
- 包含完整的 WebRTC 信令流程实现
- 具备日志输出功能便于调试

### 4. 测试客户端 (test_client.html)
- 信令流程测试工具
- 模拟双端通信场景（A 端模拟树莓派，B 端模拟手机）
- 包含自动重连机制，防止因连接断开导致的房间状态丢失
- 提供详细的日志输出功能

## 核心功能

### 房间管理
- 支持多房间视频通话
- 手动维护房间-用户映射关系
- 自动清理断开连接的用户

### 信令协议
- `join`: 加入指定房间
- `joined`: 加入成功确认
- `message`: 传递 WebRTC 信令数据 (offer/answer/candidate)
- `connect/disconnect`: 连接生命周期事件

### WebRTC 实现
- 使用 STUN 服务器实现 NAT 穿透
- 完整的 Offer/Answer 交换流程
- ICE 候选收集和交换
- 双向视频流传输

## 运行说明

### 1. 启动信令服务器
```bash
cd VideoCallProject
python server.py
```
服务器将在 `http://localhost:8080` 上启动

### 2. 配置树莓派客户端
修改 [pi_client.py](file:///Users/zhangchenxi/Desktop/WALL-E-PI/VideoCallProject/pi_client.py) 中的配置参数：
```python
SERVER_URL = "http://<服务器IP>:8080"  # 修改为实际服务器地址
ROOM_ID = "0001"  # 指定房间号
CAMERA_DEVICE = '/dev/video0'  # 摄像头设备路径
```

### 3. 使用 Web 客户端
打开 [video_client.html](file:///Users/zhangchenxi/Desktop/WALL-E-PI/VideoCallProject/video_client.html) 文件，在浏览器中运行：
- 输入房间号并点击"加入房间"
- 授权摄像头和麦克风访问权限
- 点击"发起视频通话"开始通话

## 技术栈

- **后端**: Python, aiohttp, python-socketio
- **前端**: JavaScript, Socket.IO Client, WebRTC API
- **视频处理**: aiortc, MediaPlayer
- **协议**: WebRTC, WebSocket, STUN

## 特色功能

1. **手动房间管理**: 通过自定义数据结构管理用户房间关系，避免依赖库的潜在问题
2. **自动故障恢复**: 包含完善的错误处理和自动重连机制
3. **跨平台兼容**: 同时支持树莓派设备和网页浏览器
4. **NAT穿透**: 使用STUN服务器实现P2P连接
5. **实时日志**: 详细的调试信息便于开发和故障排查

## 应用场景

- 远程监控系统
- IoT 设备远程控制
- 实时视频通讯
- 嵌入式设备视频通话