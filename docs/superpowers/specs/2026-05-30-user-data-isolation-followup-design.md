# WALL-E 用户数据隔离补齐设计

## 背景

上一轮已经把默认设备、设备管理主链路、机器人控制归属校验和健康数据模拟打通。当前后台仍有几条软件侧主链路会信任前端传来的 `userId` 或直接按 `deviceId` 查询数据：

- 联系人：`/api/contractUser/search/{userId}`、新增、删除。
- 事件：`/api/events/search/{userId}`、新增、删除、详情、更新。
- 健康查询：`/api/healthy/getRate/{deviceId}` 等查询接口。

本轮只补软件端用户隔离，不修改硬件端代码。硬件上报接口继续兼容现有模拟脚本和设备上报方式。

## 目标

- 后端以登录 token 中的当前用户 ID 作为联系人和事件数据的唯一归属来源。
- 前端传来的 `userId` 只作为旧接口兼容参数保留，不参与授权。
- 健康查询接口在返回数据前校验 `deviceId` 是否属于当前用户。
- 硬件上报接口继续允许无 token 调用，避免影响后续硬件端慢慢改进。
- 用后端测试覆盖伪造用户 ID、跨用户删除、跨设备健康查询等风险。

## 非目标

- 不修改 `Hardware-pi` 目录下的硬件端代码。
- 不做数据库结构迁移，不给健康数据表新增用户字段。
- 不重构小程序端。
- 不做完整后台 UI 重设计。
- 不改变 OneNET 回调或真实设备上报协议。

## 方案

采用主链路隔离补齐方案。

### 联系人

`ContractUserController` 使用 `CurrentHolder.getCurrentId()` 获取当前用户。查询接口保留原路径 `/search/{userId}`，但忽略路径里的 `userId`。新增联系人时覆盖请求体里的 `userId`，删除联系人时也覆盖为当前用户 ID，再交给 mapper 按 `contract_name + user_id` 删除。

这样前端即使传入别人的用户 ID，也只能操作自己的联系人。

### 事件

`EventController` 使用当前用户 ID 处理新增、查询、删除、详情和更新。

新增事件时覆盖请求体里的 `userId`。查询接口保留 `/search/{userId}` 兼容旧前端，但后端忽略路径参数。删除、详情和更新时覆盖为当前用户 ID，mapper 继续使用 `event_name + user_id` 作为归属边界。

这保持现有表结构不变，同时堵住前端伪造 `userId` 的风险。

### 健康查询

硬件上报接口保持公开：

- `POST /api/healthy/addRate`
- `POST /api/healthy/addHumidity`
- `POST /api/healthy/addBreathe`
- `POST /api/healthy/addTemperature`
- `POST /api/healthy/addFall`

健康查询接口需要 token：

- `GET /api/healthy/getRate/{deviceId}`
- `GET /api/healthy/getHumidity/{deviceId}`
- `GET /api/healthy/getBreathe/{deviceId}`
- `GET /api/healthy/getTemperature/{deviceId}`
- `GET /api/healthy/getFall/{deviceId}`

查询前通过 `ContractMachineMapper.findByUserIdAndConnectionId(currentUserId, deviceId)` 校验设备归属。设备不属于当前用户时，后端返回错误结果，不再泄露该设备健康数据。

`getFall` 当前 mapper 没有按 `deviceId` 过滤，会返回全表最新跌倒记录。本轮修正为按 `device_id = #{deviceId}` 查询最新记录。

### Token 过滤

`TokenFilter` 不再把整个 `/api/healthy` 和 `/api/events/search` 放行。

放行范围缩小为健康上报接口和登录、公开配置、视频帧等既有公开接口。健康查询和事件查询进入 token 校验流程。

### 前端兼容

前端调用可以保持现状，继续传 `localStorage` 里的 `Id`，但后端不再信任它。必要时只修正因 token 过滤变化导致的请求头或调用方式问题。

## 测试策略

- `ContractUserControllerTest`
  - 查询联系人时忽略路径里的伪造 `userId`。
  - 新增联系人时覆盖请求体里的 `userId`。
  - 删除联系人时只能删除当前用户的数据。

- `EventControllerTest`
  - 查询事件时忽略路径里的伪造 `userId`。
  - 新增、删除、详情、更新都覆盖为当前用户 ID。

- `HealthyDataControllerTest`
  - 当前用户查询自己设备时允许调用健康服务。
  - 当前用户查询别人设备时返回错误，不调用健康服务。
  - 跌倒查询按设备号过滤。

- `TokenFilterTest` 或现有控制器测试补充
  - 健康上报接口不需要 token。
  - 健康查询接口需要 token。

## 验收标准

- 联系人和事件接口不再依赖前端传来的 `userId` 做授权。
- 用户不能通过伪造 `userId` 查询、删除、更新别人的联系人或事件。
- 用户不能通过伪造 `deviceId` 查询不属于自己的健康数据。
- 健康上报接口仍可被模拟脚本调用。
- 后端测试通过：`mvn -f Parent/pom.xml -pl ../cpnRobotManagement test`。
- 前端构建通过：`npm run build`。

## 风险

- `TokenFilter` 白名单收窄后，如果前端某个页面没有携带 token，请求会变成 401，需要做少量前端兼容修正。
- 事件和联系人当前 mapper 主要用名称删除或更新，重名时行为仍受旧设计限制。本轮只补用户边界，不扩展为按主键操作。
- 健康数据没有用户字段，本轮隔离依赖设备归属表；如果多个用户共享同一个 `connectionId`，会按各自绑定关系允许查询。
