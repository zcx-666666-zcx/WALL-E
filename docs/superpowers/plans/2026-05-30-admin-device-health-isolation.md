# 后台设备、远程监控、健康数据与用户隔离实施计划

> **给执行代理：** 必须使用 `subagent-driven-development`（推荐）或 `executing-plans` 按任务逐项执行。步骤用 checkbox 跟踪。

**目标：** 实现默认设备 `瓦力 / WALLE_1`、硬件端拼写修正、健康数据模拟脚本、远程监控固定房间，以及设备主链路的用户数据隔离。

**架构：** 后端作为默认设备和数据归属的唯一可信来源。前端继续调用现有接口，但后端使用 JWT 中的当前用户 ID 进行隔离。硬件端和模拟脚本统一使用 `WALLE_1`。

**技术栈：** Spring Boot 3.2、MyBatis、Vue 3、Vite、Python 3 标准库。

---

## 文件结构

- 修改 `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/ContractMachineMapper.java`：增加默认设备查询、按用户和 ID 查询、保护删除。
- 修改 `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/ContractMachineService.java`：加入按当前用户操作的方法约定。
- 修改 `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/ContractMachineServiceImpl.java`：实现默认设备兜底、删除保护、IP 更新校验。
- 修改 `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/ContractMachineController.java`：改为从 token 取当前用户。
- 修改 `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyController.java`：发送命令前确认设备归属。
- 新增 `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Service/ContractMachineServiceImplTest.java`：覆盖默认设备和隔离行为。
- 新增 `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyControllerTest.java`：覆盖控制接口拒绝越权设备。
- 修改 `Hardware-pi/config.py`：把 `WALEE_1` 改为 `WALLE_1`，同步 topic 文本。
- 新增 `scripts/simulate_health_data.py`：模拟硬件发送健康数据。
- 修改 `Software-web/src/views/machines/machines.vue`：默认设备不可删除，表单示例更清晰。
- 修改 `Software-web/src/views/healthy/healthy.vue`：默认设备号改为 `WALLE_1`，加载时保持稳定状态。
- 修改 `Software-web/src/views/video/webrtc_video.vue`：房间号固定为常量 `0001`，页面只读展示。

---

## 任务 1：设备服务默认设备与隔离测试

**文件：**
- 新增测试：`Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Service/ContractMachineServiceImplTest.java`
- 修改：`Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/ContractMachineMapper.java`
- 修改：`Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/ContractMachineService.java`
- 修改：`Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/ContractMachineServiceImpl.java`

- [ ] **步骤 1：写失败测试**

创建测试文件，使用 Mockito 验证服务行为：

```java
package org.cpnrobot.cpnrobotmanagement.Service;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Service.impl.ContractMachineServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.ContractMachine;
import pojos.ListResult;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ContractMachineServiceImplTest {

    @Mock
    private ContractMachineMapper contractMachineMapper;

    @InjectMocks
    private ContractMachineServiceImpl service;

    @BeforeEach
    void setUp() {
        service.setDefaultRobotIpForTests("127.0.0.1");
    }

    @Test
    void searchForCurrentUserCreatesDefaultDeviceWhenMissing() {
        when(contractMachineMapper.findByUserIdAndConnectionId("7", "WALLE_1")).thenReturn(null);
        when(contractMachineMapper.add(any(ContractMachine.class))).thenReturn(1);
        when(contractMachineMapper.search("7")).thenReturn(List.of(defaultMachine(1, "7")));

        ListResult<ContractMachine> result = service.searchForCurrentUser(7);

        ArgumentCaptor<ContractMachine> captor = ArgumentCaptor.forClass(ContractMachine.class);
        verify(contractMachineMapper).add(captor.capture());
        assertThat(captor.getValue().getMachines()).isEqualTo("瓦力");
        assertThat(captor.getValue().getConnectionId()).isEqualTo("WALLE_1");
        assertThat(captor.getValue().getUserId()).isEqualTo("7");
        assertThat(captor.getValue().getRobotIp()).isEqualTo("127.0.0.1");
        assertThat(result.getRows()).hasSize(1);
    }

    @Test
    void searchForCurrentUserDoesNotCreateDuplicateDefaultDevice() {
        when(contractMachineMapper.findByUserIdAndConnectionId("7", "WALLE_1")).thenReturn(defaultMachine(1, "7"));
        when(contractMachineMapper.search("7")).thenReturn(List.of(defaultMachine(1, "7")));

        ListResult<ContractMachine> result = service.searchForCurrentUser(7);

        verify(contractMachineMapper, never()).add(any());
        assertThat(result.getRows()).extracting(ContractMachine::getConnectionId).containsExactly("WALLE_1");
    }

    @Test
    void deleteRejectsDefaultDevice() {
        ContractMachine request = new ContractMachine();
        request.setMachines("瓦力");
        request.setConnectionId("WALLE_1");
        request.setUserId("7");

        int deleted = service.deleteForCurrentUser(request, 7);

        assertThat(deleted).isZero();
        verify(contractMachineMapper, never()).delete(any());
    }

    @Test
    void updateRobotIpRequiresDeviceOwnedByCurrentUser() {
        ContractMachine request = new ContractMachine();
        request.setId(3);
        request.setRobotIp("192.168.1.20");
        when(contractMachineMapper.getByIdAndUserId(3, "7")).thenReturn(defaultMachine(3, "7"));
        when(contractMachineMapper.updateRobotIp(any())).thenReturn(1);

        int updated = service.updateRobotIpForCurrentUser(request, 7);

        assertThat(updated).isEqualTo(1);
        ArgumentCaptor<ContractMachine> captor = ArgumentCaptor.forClass(ContractMachine.class);
        verify(contractMachineMapper).updateRobotIp(captor.capture());
        assertThat(captor.getValue().getUserId()).isEqualTo("7");
    }

    @Test
    void updateRobotIpRejectsDeviceOwnedByOtherUser() {
        ContractMachine request = new ContractMachine();
        request.setId(3);
        request.setRobotIp("192.168.1.20");
        when(contractMachineMapper.getByIdAndUserId(3, "7")).thenReturn(null);

        int updated = service.updateRobotIpForCurrentUser(request, 7);

        assertThat(updated).isZero();
        verify(contractMachineMapper, never()).updateRobotIp(any());
    }

    private ContractMachine defaultMachine(Integer id, String userId) {
        ContractMachine machine = new ContractMachine();
        machine.setId(id);
        machine.setMachines("瓦力");
        machine.setConnectionId("WALLE_1");
        machine.setUserId(userId);
        machine.setRobotIp("127.0.0.1");
        return machine;
    }
}
```

- [ ] **步骤 2：运行测试确认失败**

运行：

```bash
cd Software-back
mvn -pl cpnRobotManagement -Dtest=ContractMachineServiceImplTest test
```

预期：编译失败，提示 `searchForCurrentUser`、`deleteForCurrentUser`、`updateRobotIpForCurrentUser`、`setDefaultRobotIpForTests` 或 mapper 方法不存在。

- [ ] **步骤 3：实现最小代码**

在 mapper 中增加方法：

```java
@Select("select * from contract_machine where user_id = #{userId} and connectionId = #{connectionId} limit 1")
ContractMachine findByUserIdAndConnectionId(@Param("userId") String userId, @Param("connectionId") String connectionId);

@Select("select * from contract_machine where id = #{id} and user_id = #{userId}")
ContractMachine getByIdAndUserId(@Param("id") Integer id, @Param("userId") String userId);
```

在 service 接口中增加：

```java
ListResult<ContractMachine> searchForCurrentUser(Integer currentUserId);
int addForCurrentUser(ContractMachine contractMachine, Integer currentUserId);
int deleteForCurrentUser(ContractMachine contractMachine, Integer currentUserId);
int updateRobotIpForCurrentUser(ContractMachine contractMachine, Integer currentUserId);
```

在实现类中增加常量和兜底逻辑：

```java
private static final String DEFAULT_DEVICE_NAME = "瓦力";
private static final String DEFAULT_DEVICE_ID = "WALLE_1";
private String defaultRobotIp = "127.0.0.1";

void setDefaultRobotIpForTests(String defaultRobotIp) {
    this.defaultRobotIp = defaultRobotIp;
}

public ListResult<ContractMachine> searchForCurrentUser(Integer currentUserId) {
    String userId = String.valueOf(currentUserId);
    ensureDefaultMachine(userId);
    return new ListResult<>(contractMachineMapper.search(userId));
}

private void ensureDefaultMachine(String userId) {
    ContractMachine existing = contractMachineMapper.findByUserIdAndConnectionId(userId, DEFAULT_DEVICE_ID);
    if (existing != null) {
        return;
    }
    ContractMachine machine = new ContractMachine();
    machine.setMachines(DEFAULT_DEVICE_NAME);
    machine.setConnectionId(DEFAULT_DEVICE_ID);
    machine.setUserId(userId);
    machine.setRobotIp(defaultRobotIp);
    contractMachineMapper.add(machine);
}
```

再把新增的 add/delete/update 方法实现为使用当前用户 ID。

- [ ] **步骤 4：运行测试确认通过**

运行同一个测试命令，预期全部通过。

- [ ] **步骤 5：提交**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/ContractMachineMapper.java \
        Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/ContractMachineService.java \
        Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/ContractMachineServiceImpl.java \
        Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Service/ContractMachineServiceImplTest.java
git commit -m "feat: ensure default device per user"
```

---

## 任务 2：设备 Controller 改为 token 用户

**文件：**
- 修改：`Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/ContractMachineController.java`

- [ ] **步骤 1：写失败测试**

如果不引入完整 MVC 测试，先在任务 1 的 service 测试已经覆盖核心隔离。此任务使用编译和手工 API 验证作为安全网。

- [ ] **步骤 2：实现 Controller 最小改动**

把 Controller 中的 `search/add/delete/updateRobotIp` 改成读取：

```java
Integer currentUserId = CurrentHolder.getCurrentId();
```

并调用任务 1 新增的 `*ForCurrentUser` 方法。前端传来的 `userId` 只作为兼容参数保留，不参与授权。

- [ ] **步骤 3：运行后端测试**

```bash
cd Software-back
mvn -pl cpnRobotManagement test
```

预期：测试通过。

- [ ] **步骤 4：提交**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/ContractMachineController.java
git commit -m "fix: use token user for machine endpoints"
```

---

## 任务 3：机器人控制接口校验设备归属

**文件：**
- 新增测试：`Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyControllerTest.java`
- 修改：`Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyController.java`

- [ ] **步骤 1：写失败测试**

新增测试，验证不属于当前用户的设备会被拒绝：

```java
package org.cpnrobot.cpnrobotmanagement.Controller;

import com.corundumstudio.socketio.SocketIOServer;
import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Service.RobotProxyService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.Result;
import util.CurrentHolder;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class RobotProxyControllerTest {

    @Mock
    private RobotProxyService robotProxyService;

    @Mock
    private SocketIOServer server;

    @Mock
    private ContractMachineMapper contractMachineMapper;

    @InjectMocks
    private RobotProxyController controller;

    @Test
    void motorRejectsMachineNotOwnedByCurrentUser() {
        CurrentHolder.setCurrentId(7);
        when(contractMachineMapper.getByIdAndUserId(99, "7")).thenReturn(null);

        Result result = controller.motor(Map.of("machineId", 99, "stickX", 0.1, "stickY", 0.2));

        assertThat(result.getCode()).isEqualTo(0);
        verifyNoInteractions(server);
        CurrentHolder.remove();
    }
}
```

- [ ] **步骤 2：运行测试确认失败**

```bash
cd Software-back
mvn -pl cpnRobotManagement -Dtest=RobotProxyControllerTest test
```

预期：失败或编译失败，因为控制器还没有按当前用户校验 `machineId`。

- [ ] **步骤 3：实现校验**

在 `RobotProxyController` 中增加：

```java
private ContractMachine requireOwnedMachine(Integer machineId) {
    Integer currentUserId = CurrentHolder.getCurrentId();
    if (currentUserId == null) {
        throw new RuntimeException("未登录或 token 无效");
    }
    ContractMachine machine = contractMachineMapper.getByIdAndUserId(machineId, String.valueOf(currentUserId));
    if (machine == null) {
        throw new RuntimeException("设备不存在或不属于当前用户");
    }
    return machine;
}
```

`getRoom` 和 `cameraFrame` 等按 `machineId` 操作的路径优先使用这个归属校验；公开视频流如果仍需免 token，需要在结果中标注残余风险。

- [ ] **步骤 4：运行测试确认通过**

```bash
cd Software-back
mvn -pl cpnRobotManagement -Dtest=RobotProxyControllerTest test
```

- [ ] **步骤 5：提交**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyController.java \
        Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyControllerTest.java
git commit -m "fix: protect robot commands by owner"
```

---

## 任务 4：硬件端设备名修正

**文件：**
- 修改：`Hardware-pi/config.py`

- [ ] **步骤 1：写验证命令**

运行：

```bash
rg -n "WALEE_1|WALLE_1" Hardware-pi/config.py Hardware-pi/socketio_controller.py Hardware-pi/camera_pusher.py
```

记录当前 `WALEE_1` 命中，作为待修正证据。

- [ ] **步骤 2：最小修改**

在 `Hardware-pi/config.py` 中把：

```python
DEV_NAME = "WALEE_1"
TOPIC_PUB = "$sys/kCx33ym0Dt/WALEE_1/dp/post/json"
```

改为：

```python
DEV_NAME = "WALLE_1"
TOPIC_PUB = "$sys/kCx33ym0Dt/WALLE_1/dp/post/json"
```

如果 `TOKEN` 字符串里也含 `WALEE_1`，只把资源路径文本改为 `WALLE_1`，同时在最终说明中提醒真实 OneNET token 可能需要平台重新生成。

- [ ] **步骤 3：验证**

```bash
rg -n "WALEE_1" Hardware-pi/config.py
python3 -m py_compile Hardware-pi/config.py Hardware-pi/socketio_controller.py Hardware-pi/camera_pusher.py
```

预期：`rg` 无输出，Python 编译通过。

- [ ] **步骤 4：提交**

```bash
git add Hardware-pi/config.py
git commit -m "fix: correct hardware device id"
```

---

## 任务 5：健康数据模拟脚本

**文件：**
- 新增：`scripts/simulate_health_data.py`

- [ ] **步骤 1：写脚本自测期望**

脚本应支持：

```bash
python3 scripts/simulate_health_data.py --base-url http://127.0.0.1:8080 --device-id WALLE_1 --once
```

如果后端未启动，预期打印连接失败但脚本退出码为非 0。

- [ ] **步骤 2：实现脚本**

使用 Python 标准库 `argparse`、`json`、`random`、`time`、`urllib.request`。每轮 POST 五个接口：

```python
endpoints = [
    ("/api/healthy/addRate", {"rate": rate}),
    ("/api/healthy/addHumidity", {"humidity": humidity}),
    ("/api/healthy/addBreathe", {"breathe": breathe}),
    ("/api/healthy/addTemperature", {"temperature": temperature}),
    ("/api/healthy/addFall", {"fall": fall}),
]
```

每个 payload 都补充：

```python
payload["deviceId"] = args.device_id
payload["timestamp"] = timestamp
payload["messageId"] = f"demo-{timestamp}"
```

- [ ] **步骤 3：语法验证**

```bash
python3 -m py_compile scripts/simulate_health_data.py
```

预期：无输出。

- [ ] **步骤 4：提交**

```bash
git add scripts/simulate_health_data.py
git commit -m "feat: add health data simulator"
```

---

## 任务 6：前端默认设备、健康页和固定房间

**文件：**
- 修改：`Software-web/src/views/machines/machines.vue`
- 修改：`Software-web/src/views/healthy/healthy.vue`
- 修改：`Software-web/src/views/video/webrtc_video.vue`

- [ ] **步骤 1：写修改前检查**

运行：

```bash
rg -n "kCx33ym0Dt|WALEE_1|WALLE_1|0001|roomId|删除|请输入设备号" Software-web/src/views/machines/machines.vue Software-web/src/views/healthy/healthy.vue Software-web/src/views/video/webrtc_video.vue
```

确认健康页仍有旧默认设备号，远程监控有多处 `0001`。

- [ ] **步骤 2：设备管理页最小改动**

增加默认设备判断：

```js
const DEFAULT_DEVICE_ID = 'WALLE_1'
const isDefaultMachine = (row) => row?.connectionId === DEFAULT_DEVICE_ID
```

删除按钮在默认设备上禁用或隐藏。新增设备占位改为 `备用机器人` 和 `WALLE_2`。

- [ ] **步骤 3：健康页最小改动**

把：

```js
const deviceId = ref('kCx33ym0Dt');
```

改为：

```js
const DEFAULT_DEVICE_ID = 'WALLE_1';
const deviceId = ref(DEFAULT_DEVICE_ID);
```

设备列表加载后优先选择 `connectionId === "WALLE_1"` 的设备；没有列表时仍保持 `WALLE_1`。

- [ ] **步骤 4：远程监控固定房间**

在 script 中增加：

```js
const FIXED_ROOM_ID = '0001';
```

所有 join、hangup、offer、answer、candidate 发送都用 `FIXED_ROOM_ID`。模板中房间号显示为只读，不再让用户输入。

- [ ] **步骤 5：构建验证**

```bash
cd Software-web
npm run build
```

预期：构建通过。

- [ ] **步骤 6：提交**

```bash
git add Software-web/src/views/machines/machines.vue Software-web/src/views/healthy/healthy.vue Software-web/src/views/video/webrtc_video.vue
git commit -m "fix: stabilize default device pages"
```

---

## 任务 7：整体验证

**文件：**
- 可能修改：`docs/` 下的使用说明，记录模拟脚本命令。

- [ ] **步骤 1：后端测试**

```bash
cd Software-back
mvn -pl cpnRobotManagement test
```

预期：测试通过。

- [ ] **步骤 2：前端构建**

```bash
cd Software-web
npm run build
```

预期：构建通过。

- [ ] **步骤 3：Python 脚本语法**

```bash
python3 -m py_compile scripts/simulate_health_data.py
```

预期：无输出。

- [ ] **步骤 4：最终状态检查**

```bash
git status --short
git log --oneline -5
```

确认只剩用户原本未提交的部署文档改动，或说明新增实现提交。
