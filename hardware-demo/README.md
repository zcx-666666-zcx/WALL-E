# WALL-E Hardware Demo

这是比赛兜底用的电脑端硬件模拟器。它不替代真实树莓派代码，只在真实硬件临时出错时，模拟关键链路：

- Socket.IO 机器人在线、接收遥控指令、向后端推送 `camera_frame`
- WebRTC 视频通话：模拟树莓派接听网页端通话请求
- 体征数据上传：心率、呼吸、温度、湿度、跌倒
- 事件提醒轮询：从后端同步提醒，到点后在控制台打印
- 本地 MJPEG 摄像头：把电脑临时当作机器人 HTTP 摄像头源

## 快速开始

```bash
cd hardware-demo
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 常用环境变量

```bash
WALLE_PUBLIC_SERVER_URL=http://127.0.0.1:8088
WALLE_API_BASE_URL=http://127.0.0.1:8088/api
WALLE_SOCKETIO_SERVER_URL=http://127.0.0.1:8088
WALLE_DEVICE_NAME=WALLE_1
WALLE_HEALTH_DEVICE_ID=WALLE_1
WALLE_DEMO_USERNAME=admin
WALLE_DEMO_PASSWORD=admin123
```

如果你走 FRP 公网域名，把 `WALLE_PUBLIC_SERVER_URL` 改成你的 FRP HTTPS 域名即可，例如：

```bash
WALLE_PUBLIC_SERVER_URL=https://你的新域名
```

## 场景 A：摄像头坏了，但后端/Web 正常

启动 Socket.IO 视频帧模拟。这个会加入 `robot_WALLE_1` 房间，并持续向 Java 后端发送 `camera_frame`：

```bash
python -m hardware_demo.cli socket-camera
```

Web 控制台如果使用后端缓存帧接口 `/api/robot/camera-frame/{machineId}`，就能看到模拟画面。遥控、舵机、动画、设置指令也会在控制台打印出来，证明后端到“机器人”的命令链路没断。

## 场景 A2：WebRTC 视频通话兜底

如果演示的是“远程监护 / 视频通话”页面，安装额外依赖：

```bash
pip install -r requirements-webrtc.txt
python -m hardware_demo.cli webrtc-video
```

然后在 Web 的远程监护页面加入房间并请求监视，模拟器会像树莓派一样接听并发送演示画面。

## 场景 B：体征雷达坏了

只模拟体征数据：

```bash
python -m hardware_demo.cli health --mode normal
```

异常演示：

```bash
python -m hardware_demo.cli health --mode abnormal
python -m hardware_demo.cli health --mode fall
```

## 场景 C：事件提醒需要演示

```bash
python -m hardware_demo.cli events
```

它会用 `WALLE_DEMO_USERNAME/WALLE_DEMO_PASSWORD` 登录拿 token，然后读取该用户的事件提醒。到点后会在控制台打印提醒内容。

## 场景 D：想把电脑当作机器人 HTTP 摄像头

```bash
python -m hardware_demo.cli local-camera --port 5000
```

然后在 Web 的设备列表里，把该设备的机器人 IP 改成运行模拟器的电脑 IP，后端的 `robot.http-port` 保持 `5000`。

## 一起启动

```bash
python -m hardware_demo.cli all
```

如比赛账号不是 `admin/admin123`，先设置：

```bash
WALLE_DEMO_USERNAME=你的账号
WALLE_DEMO_PASSWORD=你的密码
python -m hardware_demo.cli all
```
