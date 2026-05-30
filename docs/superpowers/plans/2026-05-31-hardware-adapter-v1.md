# WALL-E Hardware Adapter V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按 `Hardware-pi` 当前真实协议适配前端和后端，让摄像头帧、健康数据和设备状态与真实硬件行为对齐。

**Architecture:** 后端作为硬件协议适配层，不修改硬件端代码。摄像头帧读取从设备显示名改为优先使用 `connectionId`；健康查询在服务层把默认设备号 `WALLE_1` 扩展为兼容别名 `kCx33ym0Dt`；设备状态接口聚合 Socket.IO 摄像头帧缓存和健康表最新时间。前端只消费后端状态接口，不直接理解硬件别名。

**Tech Stack:** Java 25, Spring Boot 3.2, MyBatis annotation mapper, JUnit 5, Mockito, AssertJ, Vue 3, Vite.

---

## File Structure

- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyController.java`
  - 摄像头帧按 `connectionId` 取缓存；新增设备状态接口。
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/HealthyDataService.java`
  - 新增健康最新时间查询方法。
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/HealthyDataServiceImpl.java`
  - 默认设备 `WALLE_1` 查询兼容硬件默认 `kCx33ym0Dt`。
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapper.java`
  - 支持 `device_id in (...)` 查询和最新健康时间聚合。
- Modify: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyControllerTest.java`
  - 覆盖摄像头帧使用 `connectionId` 和跨用户拒绝。
- Create: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Service/HealthyDataServiceImplHardwareAliasTest.java`
  - 覆盖 `WALLE_1` 兼容 `kCx33ym0Dt`。
- Modify: `Software-web/src/api/users.js`
  - 新增 `RobotStatusApi(machineId)`。
- Modify: `Software-web/src/views/machines/machines.vue`
  - 设备列表显示摄像头和健康数据状态。

## Task 1: Camera Frame Uses Hardware Device Name

**Files:**
- Modify: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyControllerTest.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyController.java`

- [ ] **Step 1: Write failing tests**

Append these tests to `RobotProxyControllerTest`:

```java
@Test
void cameraFrameUsesConnectionIdFromOwnedMachine() {
    CurrentHolder.setCurrentId(7);
    ContractMachine machine = new ContractMachine();
    machine.setId(3);
    machine.setMachines("瓦力");
    machine.setConnectionId("WALLE_1");
    when(contractMachineMapper.getByIdAndUserId(3, "7")).thenReturn(machine);
    SignalingHandler.CAMERA_FRAMES.put("WALLE_1", new byte[]{1, 2, 3});

    ResponseEntity<byte[]> response = controller.cameraFrame(3);

    assertThat(response.getStatusCode().value()).isEqualTo(200);
    assertThat(response.getBody()).containsExactly(1, 2, 3);
}

@Test
void cameraFrameRejectsMachineNotOwnedByCurrentUser() {
    CurrentHolder.setCurrentId(7);
    when(contractMachineMapper.getByIdAndUserId(99, "7")).thenReturn(null);

    ResponseEntity<byte[]> response = controller.cameraFrame(99);

    assertThat(response.getStatusCode().value()).isEqualTo(404);
}
```

Also clear frame caches in `tearDown()`:

```java
SignalingHandler.CAMERA_FRAMES.clear();
SignalingHandler.CAMERA_FRAME_TIMES.clear();
```

- [ ] **Step 2: Run RED**

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=RobotProxyControllerTest test
```

Expected: FAIL because `cameraFrame` currently uses `getById` and `machine.getMachines()`.

- [ ] **Step 3: Implement camera frame ownership and key fix**

In `RobotProxyController.cameraFrame`, replace `getById` and display-name lookup with:

```java
ContractMachine machine = requireOwnedMachine(machineId);
String deviceName = machine.getConnectionId();
if (deviceName == null || deviceName.isEmpty()) {
    deviceName = machine.getMachines();
}
if (deviceName == null || deviceName.isEmpty()) {
    return ResponseEntity.notFound().build();
}
byte[] jpeg = SignalingHandler.CAMERA_FRAMES.get(deviceName);
```

- [ ] **Step 4: Run GREEN**

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=RobotProxyControllerTest test
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyController.java Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyControllerTest.java
git commit -m "fix: read camera frames by hardware device id"
```

## Task 2: Health Query Hardware Device Alias

**Files:**
- Create: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Service/HealthyDataServiceImplHardwareAliasTest.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapper.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/HealthyDataServiceImpl.java`

- [ ] **Step 1: Write failing service tests**

Create `HealthyDataServiceImplHardwareAliasTest.java`:

```java
package org.cpnrobot.cpnrobotmanagement.Service;

import org.cpnrobot.cpnrobotmanagement.Mapper.HealthyDataMapper;
import org.cpnrobot.cpnrobotmanagement.Service.impl.HealthyDataServiceImpl;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.SensorRate;

import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class HealthyDataServiceImplHardwareAliasTest {

    @Mock
    private HealthyDataMapper healthyDataMapper;

    @InjectMocks
    private HealthyDataServiceImpl service;

    @Test
    void defaultDeviceRateQueryIncludesHardwareProductAlias() {
        when(healthyDataMapper.getRateByDeviceIds(any(), any())).thenReturn(List.of(new SensorRate()));
        ArgumentCaptor<List<String>> captor = ArgumentCaptor.forClass(List.class);

        service.getRate("WALLE_1");

        verify(healthyDataMapper).getRateByDeviceIds(captor.capture(), any(LocalDateTime.class));
        assertThat(captor.getValue()).containsExactly("WALLE_1", "kCx33ym0Dt");
    }

    @Test
    void nonDefaultDeviceDoesNotIncludeHardwareAlias() {
        when(healthyDataMapper.getRateByDeviceIds(any(), any())).thenReturn(List.of());
        ArgumentCaptor<List<String>> captor = ArgumentCaptor.forClass(List.class);

        service.getRate("OTHER");

        verify(healthyDataMapper).getRateByDeviceIds(captor.capture(), any(LocalDateTime.class));
        assertThat(captor.getValue()).containsExactly("OTHER");
    }
}
```

- [ ] **Step 2: Run RED**

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=HealthyDataServiceImplHardwareAliasTest test
```

Expected: compile FAIL because `HealthyDataMapper.getRateByDeviceIds` does not exist.

- [ ] **Step 3: Add mapper methods**

Add `java.util.List` is already imported. Add these methods to `HealthyDataMapper`:

```java
@Select({
        "<script>",
        "SELECT * FROM sensor_rate",
        "WHERE device_id IN",
        "<foreach collection='deviceIds' item='deviceId' open='(' separator=',' close=')'>",
        "#{deviceId}",
        "</foreach>",
        "AND DATE(created_at) = DATE(#{time})",
        "ORDER BY timestamp ASC",
        "</script>"
})
List<SensorRate> getRateByDeviceIds(@Param("deviceIds") List<String> deviceIds, @Param("time") LocalDateTime time);
```

Add the remaining mapper methods:

```java
@Select({
        "<script>",
        "SELECT * FROM sensor_humidity",
        "WHERE device_id IN",
        "<foreach collection='deviceIds' item='deviceId' open='(' separator=',' close=')'>",
        "#{deviceId}",
        "</foreach>",
        "AND DATE(created_at) = DATE(#{time})",
        "ORDER BY timestamp ASC",
        "</script>"
})
List<SensorHumidity> getHumidityByDeviceIds(@Param("deviceIds") List<String> deviceIds, @Param("time") LocalDateTime time);

@Select({
        "<script>",
        "SELECT * FROM sensor_breathe",
        "WHERE device_id IN",
        "<foreach collection='deviceIds' item='deviceId' open='(' separator=',' close=')'>",
        "#{deviceId}",
        "</foreach>",
        "AND DATE(created_at) = DATE(#{time})",
        "ORDER BY timestamp ASC",
        "</script>"
})
List<SensorBreathe> getBreatheByDeviceIds(@Param("deviceIds") List<String> deviceIds, @Param("time") LocalDateTime time);

@Select({
        "<script>",
        "SELECT * FROM sensor_temperature",
        "WHERE device_id IN",
        "<foreach collection='deviceIds' item='deviceId' open='(' separator=',' close=')'>",
        "#{deviceId}",
        "</foreach>",
        "AND DATE(created_at) = DATE(#{time})",
        "ORDER BY timestamp ASC",
        "</script>"
})
List<SensorTemperature> getTemperatureByDeviceIds(@Param("deviceIds") List<String> deviceIds, @Param("time") LocalDateTime time);

@Select({
        "<script>",
        "SELECT * FROM sensor_fall",
        "WHERE device_id IN",
        "<foreach collection='deviceIds' item='deviceId' open='(' separator=',' close=')'>",
        "#{deviceId}",
        "</foreach>",
        "ORDER BY created_at DESC",
        "LIMIT 1",
        "</script>"
})
SensorFall getFallByDeviceIds(@Param("deviceIds") List<String> deviceIds);
```

- [ ] **Step 4: Use alias list in service**

Add constants and resolver to `HealthyDataServiceImpl`:

```java
private static final String DEFAULT_DEVICE_ID = "WALLE_1";
private static final String HARDWARE_HEALTH_ALIAS = "kCx33ym0Dt";

private List<String> resolveHealthDeviceIds(String deviceId) {
    if (DEFAULT_DEVICE_ID.equals(deviceId)) {
        return List.of(DEFAULT_DEVICE_ID, HARDWARE_HEALTH_ALIAS);
    }
    return List.of(deviceId);
}
```

Then use `resolveHealthDeviceIds(deviceId)` in `getRate`, `getHumidity`, `getBreathe`, `getTemperature`, and `getFall`.

- [ ] **Step 5: Run GREEN**

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=HealthyDataServiceImplHardwareAliasTest test
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapper.java Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/HealthyDataServiceImpl.java Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Service/HealthyDataServiceImplHardwareAliasTest.java
git commit -m "fix: support hardware health device alias"
```

## Task 3: Robot Status Endpoint

**Files:**
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyController.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/HealthyDataService.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/HealthyDataServiceImpl.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapper.java`
- Modify: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyControllerTest.java`

- [ ] **Step 1: Write failing status endpoint test**

Append to `RobotProxyControllerTest`:

```java
@Mock
private HealthyDataService healthyDataService;
```

Set it in `setUp()`:

```java
ReflectionTestUtils.setField(controller, "healthyDataService", healthyDataService);
```

Add test:

```java
@Test
void statusReturnsCameraAndHealthFreshnessForOwnedMachine() {
    CurrentHolder.setCurrentId(7);
    ContractMachine machine = new ContractMachine();
    machine.setId(3);
    machine.setConnectionId("WALLE_1");
    when(contractMachineMapper.getByIdAndUserId(3, "7")).thenReturn(machine);
    SignalingHandler.CAMERA_FRAME_TIMES.put("WALLE_1", System.currentTimeMillis());
    when(healthyDataService.getLatestHealthAt("WALLE_1")).thenReturn(LocalDateTime.now());

    Result result = controller.status(3);

    assertThat(result.getCode()).isEqualTo(1);
    Map<String, Object> data = (Map<String, Object>) result.getData();
    assertThat(data.get("connectionId")).isEqualTo("WALLE_1");
    assertThat(data.get("cameraOnline")).isEqualTo(true);
    assertThat(data.get("healthOnline")).isEqualTo(true);
}
```

- [ ] **Step 2: Run RED**

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=RobotProxyControllerTest test
```

Expected: compile FAIL because `RobotProxyController.status` and `HealthyDataService.getLatestHealthAt` do not exist.

- [ ] **Step 3: Add latest health mapper and service**

Add to `HealthyDataService`:

```java
LocalDateTime getLatestHealthAt(String deviceId);
```

Add to `HealthyDataMapper`:

```java
@Select({
        "<script>",
        "SELECT MAX(created_at) FROM (",
        "SELECT created_at FROM sensor_rate WHERE device_id IN",
        "<foreach collection='deviceIds' item='deviceId' open='(' separator=',' close=')'>#{deviceId}</foreach>",
        "UNION ALL SELECT created_at FROM sensor_humidity WHERE device_id IN",
        "<foreach collection='deviceIds' item='deviceId' open='(' separator=',' close=')'>#{deviceId}</foreach>",
        "UNION ALL SELECT created_at FROM sensor_breathe WHERE device_id IN",
        "<foreach collection='deviceIds' item='deviceId' open='(' separator=',' close=')'>#{deviceId}</foreach>",
        "UNION ALL SELECT created_at FROM sensor_temperature WHERE device_id IN",
        "<foreach collection='deviceIds' item='deviceId' open='(' separator=',' close=')'>#{deviceId}</foreach>",
        "UNION ALL SELECT created_at FROM sensor_fall WHERE device_id IN",
        "<foreach collection='deviceIds' item='deviceId' open='(' separator=',' close=')'>#{deviceId}</foreach>",
        ") latest_health",
        "</script>"
})
LocalDateTime getLatestHealthAt(@Param("deviceIds") List<String> deviceIds);
```

Implement in service:

```java
@Override
public LocalDateTime getLatestHealthAt(String deviceId) {
    return healthyDataMapper.getLatestHealthAt(resolveHealthDeviceIds(deviceId));
}
```

- [ ] **Step 4: Add status endpoint**

Inject `HealthyDataService` into `RobotProxyController`, then add:

```java
@GetMapping("/status/{machineId}")
public Result status(@PathVariable Integer machineId) {
    try {
        ContractMachine machine = requireOwnedMachine(machineId);
        String connectionId = machine.getConnectionId();
        if (connectionId == null || connectionId.isEmpty()) {
            connectionId = machine.getMachines();
        }
        long now = System.currentTimeMillis();
        Long lastCameraFrameAt = SignalingHandler.CAMERA_FRAME_TIMES.get(connectionId);
        Long cameraAge = lastCameraFrameAt == null ? null : now - lastCameraFrameAt;
        LocalDateTime lastHealthAt = healthyDataService.getLatestHealthAt(connectionId);
        Long healthAge = null;
        if (lastHealthAt != null) {
            healthAge = java.time.Duration.between(lastHealthAt, LocalDateTime.now()).toMillis();
        }
        Map<String, Object> data = new java.util.LinkedHashMap<>();
        data.put("connectionId", connectionId);
        data.put("cameraOnline", cameraAge != null && cameraAge <= 10_000);
        data.put("lastCameraFrameAt", lastCameraFrameAt);
        data.put("lastCameraFrameAgeMs", cameraAge);
        data.put("healthOnline", healthAge != null && healthAge <= 10_000);
        data.put("lastHealthAt", lastHealthAt);
        data.put("lastHealthAgeMs", healthAge);
        return Result.success(data);
    } catch (Exception e) {
        return Result.error(e.getMessage());
    }
}
```

- [ ] **Step 5: Run GREEN**

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=RobotProxyControllerTest test
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyController.java Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/HealthyDataService.java Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/HealthyDataServiceImpl.java Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapper.java Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/RobotProxyControllerTest.java
git commit -m "feat: expose robot hardware status"
```

## Task 4: Frontend Hardware Status Display

**Files:**
- Modify: `Software-web/src/api/users.js`
- Modify: `Software-web/src/views/machines/machines.vue`

- [ ] **Step 1: Add API helper**

Add to `Software-web/src/api/users.js`:

```javascript
export const RobotStatusApi = (machineId) => request.get(`/robot/status/${machineId}`)
```

- [ ] **Step 2: Update machines page status state**

In `machines.vue`, import `RobotStatusApi`, add:

```javascript
const statusMap = ref({})

const loadStatus = async (machine) => {
  if (!machine?.id) return
  try {
    const result = await RobotStatusApi(machine.id)
    if (result?.code === 1) {
      statusMap.value[machine.id] = result.data
    }
  } catch {
    statusMap.value[machine.id] = { cameraOnline: false, healthOnline: false }
  }
}
```

After loading machines, call:

```javascript
await Promise.all((tableData.value || []).map(loadStatus))
```

Keep the current `tableData` state name and do not rename unrelated state.

- [ ] **Step 3: Add minimal status columns**

Add two columns:

```vue
<el-table-column label="摄像头" align="center" width="110">
  <template #default="{ row }">
    <span class="status-dot" :class="{ online: statusMap[row.id]?.cameraOnline }"></span>
    {{ statusMap[row.id]?.cameraOnline ? '在线' : '等待' }}
  </template>
</el-table-column>

<el-table-column label="健康数据" align="center" width="120">
  <template #default="{ row }">
    <span class="status-dot" :class="{ online: statusMap[row.id]?.healthOnline }"></span>
    {{ statusMap[row.id]?.healthOnline ? '在线' : '等待' }}
  </template>
</el-table-column>
```

Add compact CSS:

```css
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  background: #c9b8ad;
}
.status-dot.online {
  background: #32b36b;
}
```

- [ ] **Step 4: Build frontend**

```bash
npm run build
```

Working directory: `Software-web`.

Expected: build succeeds; existing Vite warnings may remain.

- [ ] **Step 5: Commit**

```bash
git add Software-web/src/api/users.js Software-web/src/views/machines/machines.vue
git commit -m "feat: show hardware status on devices"
```

## Task 5: Final Verification and Push

**Files:**
- Verify only.

- [ ] **Step 1: Run backend tests**

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement test
```

Working directory: `Software-back`.

Expected: BUILD SUCCESS.

- [ ] **Step 2: Run frontend build**

```bash
npm run build
```

Working directory: `Software-web`.

Expected: build succeeds; existing Vite warnings may remain.

- [ ] **Step 3: Confirm hardware files were not modified**

```bash
git status --short Hardware-pi
```

Expected: no output.

- [ ] **Step 4: Push branch**

```bash
git push
```

Expected: existing PR branch updates successfully.
