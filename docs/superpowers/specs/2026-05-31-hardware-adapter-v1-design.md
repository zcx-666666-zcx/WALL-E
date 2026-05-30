# WALL-E 硬件适配 V1 设计

## 背景

本轮以 `Hardware-pi` 当前顶层代码作为事实来源，适配前端和后端，不修改硬件端代码。`Hardware-pi/reference/` 下的旧代码只作为参考，不作为当前运行协议。

当前硬件端真实行为：

- `config.py` 中 `DEV_NAME = "WALLE_1"`。
- `socketio_controller.py` 连接 Java 后端后加入 `robot_WALLE_1` 房间。
- `camera_pusher.py` 主动发送 `camera_frame`，payload 里 `deviceName = "WALLE_1"`。
- `mqtt_manager.py` 通过 HTTP 上传健康数据，默认 `DEVICE_ID = "kCx33ym0Dt"`，除非运行环境配置了 `HEALTH_DEVICE_ID`。
- `event_manager.py` 会同步提醒事件，但默认不带认证；事件同步认证兼容留到下一版单独处理。

## 目标

- 让后台远程监控能正确读取硬件端主动推送的摄像头帧。
- 让健康页在不改硬件端代码的情况下兼容真实硬件默认健康 `deviceId = "kCx33ym0Dt"`。
- 给后台提供最小可用的设备状态信息：最近摄像头帧时间、健康数据最近更新时间。
- 保持已有默认设备：显示名 `瓦力`，设备号 `WALLE_1`。
- 不放宽已经完成的用户数据隔离。

## 非目标

- 不修改 `Hardware-pi` 目录下任何代码。
- 不重构 WebRTC 视频通话。
- 不改 OneNET token 或真实硬件凭证。
- 不在本轮恢复硬件端提醒事件同步认证。
- 不做完整 UI 重设计。

## 方案

### 摄像头帧映射

硬件端推送的 `camera_frame` 使用 `deviceName = DEV_NAME = "WALLE_1"`。后端当前 `/api/robot/camera-frame/{machineId}` 使用 `machine.getMachines()` 读取缓存，而默认设备显示名是 `瓦力`，因此取不到 `WALLE_1` 缓存。

本轮改为：

- 查询设备时仍通过 `machineId` 获取设备。
- 读取摄像头帧时优先使用 `machine.getConnectionId()`。
- 如果 `connectionId` 为空，再兼容旧逻辑使用 `machine.getMachines()`。
- 摄像头接口也要校验当前用户拥有该设备，避免公开视频接口绕过隔离。

### 健康设备号兼容

硬件端健康上传默认 `deviceId = "kCx33ym0Dt"`，前端健康页和默认设备使用 `WALLE_1`。为了不改硬件端，后端在健康数据层做兼容。

本轮采用查询兼容，不修改历史写入值：

- 新增硬件健康别名配置：
  - 默认设备号：`WALLE_1`
  - 兼容健康设备号：`kCx33ym0Dt`
- 当用户查询 `WALLE_1` 的健康数据时，后端查询 `device_id in ("WALLE_1", "kCx33ym0Dt")`。
- 当用户查询其他设备号时，只查该设备号。
- 设备归属校验仍然基于 `WALLE_1` 对应的 `contract_machine.connectionId`，不因为别名绕过用户隔离。

这样真实硬件如果还没配置 `HEALTH_DEVICE_ID=WALLE_1`，后台也能显示健康数据。以后硬件端改成上传 `WALLE_1` 后，兼容逻辑仍然可用。

### 设备状态

后端新增一个轻量状态接口：

- `GET /api/robot/status/{machineId}`

返回：

- `connectionId`
- `cameraOnline`
- `lastCameraFrameAt`
- `lastCameraFrameAgeMs`
- `healthOnline`
- `lastHealthAt`
- `lastHealthAgeMs`

状态来源：

- 摄像头状态来自 `SignalingHandler.CAMERA_FRAME_TIMES`。
- 健康状态来自各健康表中该设备号或兼容别名的最新 `created_at`。

在线判断：

- 摄像头最近 10 秒内有帧，认为 `cameraOnline = true`。
- 健康数据最近 10 秒内有上传，认为 `healthOnline = true`。

### 前端展示

前端只做最小状态展示：

- 设备管理页或远程控制页显示设备在线状态。
- 健康页显示“健康数据最后更新时间”。
- 远程监控或控制页如果摄像头没有帧，显示“等待硬件推送画面”，而不是空白误导。

具体放置位置在实施计划里按现有页面结构选择，避免大改 UI。

## 测试策略

- 后端测试摄像头帧读取使用 `connectionId`，不是显示名。
- 后端测试摄像头帧接口会拒绝不属于当前用户的 `machineId`。
- 后端测试查询 `WALLE_1` 健康数据时会同时使用兼容别名 `kCx33ym0Dt`。
- 后端测试查询其他设备号时不会混入默认别名。
- 后端测试状态接口能返回摄像头和健康最近更新时间。
- 前端构建验证页面改动没有破坏打包。

## 验收标准

- 硬件端推送 `camera_frame` 后，后台按默认设备能取到 `WALLE_1` 的画面缓存。
- 健康页查询 `WALLE_1` 时能兼容硬件端默认上传的 `kCx33ym0Dt` 数据。
- 跨用户不能读取别人的摄像头帧或设备状态。
- 后端测试通过：`mvn -f Parent/pom.xml -pl ../cpnRobotManagement test`。
- 前端构建通过：`npm run build`。

## 风险

- 兼容 `kCx33ym0Dt` 是为了匹配当前硬件默认值；如果后续新增多台设备，需要把别名迁移成可配置的设备级字段。
- 摄像头在线状态依赖内存缓存，后端重启后状态会清空，直到硬件重新推帧。
- 健康在线状态依赖数据库 `created_at`，如果数据库时间和服务器时间差异过大，在线判断会不准确。
