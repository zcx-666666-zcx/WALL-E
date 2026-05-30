# WALL-E User Data Isolation Follow-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 补齐联系人、事件、健康查询的软件端用户数据隔离，不修改硬件端代码。

**Architecture:** 控制器层从 `CurrentHolder.getCurrentId()` 获取 token 用户，覆盖请求体和路径中的用户字段。健康查询在调用健康数据服务前通过 `ContractMachineMapper` 校验 `deviceId` 是否属于当前用户。`TokenFilter` 只放行健康上报接口，健康查询和事件查询进入 token 校验。

**Tech Stack:** Java 25, Spring Boot 3.2, MyBatis annotation mapper, JUnit 5, Mockito, AssertJ, Vue 3/Vite.

---

## File Structure

- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/ContractUserController.java`
  - 使用当前 token 用户处理联系人查询、新增、删除。
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/EventController.java`
  - 使用当前 token 用户处理事件新增、查询、删除、详情、更新。
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/HealthyDataController.java`
  - 对健康查询增加设备归属校验，健康上报保持公开兼容。
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapper.java`
  - 修正 `getFall` 为按 `device_id` 查询最新跌倒记录。
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Filter/TokenFilter.java`
  - 收窄 `/api/healthy` 和 `/api/events/search` 白名单。
- Create: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/ContractUserControllerTest.java`
  - 覆盖联系人接口忽略伪造用户 ID。
- Create: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/EventControllerTest.java`
  - 覆盖事件接口忽略伪造用户 ID。
- Create: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/HealthyDataControllerTest.java`
  - 覆盖健康查询设备归属校验。
- Create: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapperSqlTest.java`
  - 使用字符串检查防止 `getFall` 再次退化为全表最新。

## Task 1: Contract User Controller Isolation

**Files:**
- Create: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/ContractUserControllerTest.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/ContractUserController.java`

- [ ] **Step 1: Write the failing controller test**

```java
package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.ContractUserService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.ContractUser;
import pojos.ListResult;
import pojos.Result;
import util.CurrentHolder;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ContractUserControllerTest {

    @Mock
    private ContractUserService contractUserService;

    @InjectMocks
    private ContractUserController controller;

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
    }

    @Test
    void searchUsesCurrentTokenUserInsteadOfPathUser() {
        CurrentHolder.setCurrentId(7);
        when(contractUserService.search("7")).thenReturn(new ListResult<>(List.of()));

        Result result = controller.search("999");

        assertThat(result.getCode()).isEqualTo(1);
        verify(contractUserService).search("7");
    }

    @Test
    void addForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        ContractUser request = new ContractUser();
        request.setContractName("家属");
        request.setContractPhoneNumber("13800000000");
        request.setUserId(999);
        when(contractUserService.add(argThat(user -> user.getUserId() == 7))).thenReturn(1);

        Result result = controller.add(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(contractUserService).add(argThat(user -> user.getUserId() == 7));
    }

    @Test
    void deleteForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        ContractUser request = new ContractUser();
        request.setContractName("家属");
        request.setUserId(999);
        when(contractUserService.delete(argThat(user -> user.getUserId() == 7))).thenReturn(1);

        Result result = controller.delete(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(contractUserService).delete(argThat(user -> user.getUserId() == 7));
    }
}
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=ContractUserControllerTest test
```

Expected: FAIL because `ContractUserController.search("999")` still calls `contractUserService.search("999")`, and add/delete still pass request user ID `999`.

- [ ] **Step 3: Implement minimal controller change**

In `ContractUserController.java`, add `import util.CurrentHolder;` and change methods to:

```java
@GetMapping("/search/{userId}")
public Result search(@PathVariable("userId") String userId){
    Integer currentUserId = CurrentHolder.getCurrentId();
    ListResult<ContractUser> listResult = contractUserService.search(String.valueOf(currentUserId));
    return Result.success(listResult);
}

@PostMapping("/add")
public Result add(@RequestBody ContractUser contractUser){
    Integer currentUserId = CurrentHolder.getCurrentId();
    contractUser.setUserId(currentUserId);
    int num = contractUserService.add(contractUser);
    if(num!=0){
        return Result.success();
    }
    return Result.error("添加失败");
}

@DeleteMapping("/delete")
public Result delete(@RequestBody ContractUser contractUser){
    Integer currentUserId = CurrentHolder.getCurrentId();
    contractUser.setUserId(currentUserId);
    int num = contractUserService.delete(contractUser);
    if(num!=0){
        return Result.success();
    }
    return Result.error("删除失败");
}
```

- [ ] **Step 4: Run the test and verify GREEN**

Run:

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=ContractUserControllerTest test
```

Expected: PASS, `Tests run: 3, Failures: 0, Errors: 0`.

- [ ] **Step 5: Commit**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/ContractUserController.java Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/ContractUserControllerTest.java
git commit -m "fix: isolate contract user endpoints"
```

## Task 2: Event Controller Isolation

**Files:**
- Create: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/EventControllerTest.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/EventController.java`

- [ ] **Step 1: Write the failing controller test**

```java
package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.EventService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.Event;
import pojos.ListResult;
import pojos.Result;
import util.CurrentHolder;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class EventControllerTest {

    @Mock
    private EventService eventservice;

    @InjectMocks
    private EventController controller;

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
    }

    @Test
    void searchUsesCurrentTokenUserInsteadOfPathUser() {
        CurrentHolder.setCurrentId(7);
        when(eventservice.searchEvent("7")).thenReturn(new ListResult<>(List.of()));

        Result result = controller.searchEvent("999");

        assertThat(result.getCode()).isEqualTo(1);
        verify(eventservice).searchEvent("7");
    }

    @Test
    void addForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        Event request = new Event();
        request.setEventName("吃药");
        request.setUserId("999");
        when(eventservice.addEvent(argThat(event -> "7".equals(event.getUserId())))).thenReturn(1);

        Result result = controller.addEvent(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(eventservice).addEvent(argThat(event -> "7".equals(event.getUserId())));
    }

    @Test
    void deleteForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        Event request = new Event();
        request.setEventName("吃药");
        request.setUserId("999");
        when(eventservice.deleteEvent(argThat(event -> "7".equals(event.getUserId())))).thenReturn(1);

        Result result = controller.deleteEvent(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(eventservice).deleteEvent(argThat(event -> "7".equals(event.getUserId())));
    }

    @Test
    void searchOneForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        Event request = new Event();
        request.setEventName("吃药");
        request.setUserId("999");
        Event owned = new Event();
        owned.setEventName("吃药");
        owned.setUserId("7");
        when(eventservice.searchOne(argThat(event -> "7".equals(event.getUserId())))).thenReturn(owned);

        Result result = controller.searchOne(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(eventservice).searchOne(argThat(event -> "7".equals(event.getUserId())));
    }

    @Test
    void updateForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        Event request = new Event();
        request.setEventName("吃药");
        request.setUserId("999");
        when(eventservice.updateEvent(argThat(event -> "7".equals(event.getUserId())))).thenReturn(1);

        Result result = controller.updateEvent(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(eventservice).updateEvent(argThat(event -> "7".equals(event.getUserId())));
    }
}
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=EventControllerTest test
```

Expected: FAIL because controller still trusts path/request `userId`.

- [ ] **Step 3: Implement minimal controller change**

In `EventController.java`, add `import util.CurrentHolder;` and a helper:

```java
private String currentUserId() {
    return String.valueOf(CurrentHolder.getCurrentId());
}
```

Then update methods:

```java
@PostMapping("/add")
public Result addEvent(@RequestBody Event event){
    event.setUserId(currentUserId());
    int num = eventservice.addEvent(event);
    if(num!=0){
        return Result.success();
    }
    return Result.error("添加失败");
}

@GetMapping("/search/{userId}")
public Result searchEvent(@PathVariable("userId") String userId){
    ListResult<Event> listResult = eventservice.searchEvent(currentUserId());
    return Result.success(listResult);
}

@DeleteMapping("/delete")
public Result deleteEvent(@RequestBody Event event){
    event.setUserId(currentUserId());
    int num = eventservice.deleteEvent(event);
    if(num!=0){
        return Result.success();
    }
    return Result.error("删除失败");
}

@PostMapping("/searchOne")
public Result searchOne(@RequestBody Event event){
    event.setUserId(currentUserId());
    Event e = eventservice.searchOne(event);
    if(e!=null){
        return Result.success(e);
    }
    return Result.error("未找到该事件");
}

@PutMapping("/update")
public Result updateEvent(@RequestBody Event event){
    event.setUserId(currentUserId());
    int num = eventservice.updateEvent(event);
    if(num!=0){
        return Result.success();
    }
    return Result.error("更新失败");
}
```

- [ ] **Step 4: Run the test and verify GREEN**

Run:

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=EventControllerTest test
```

Expected: PASS, `Tests run: 5, Failures: 0, Errors: 0`.

- [ ] **Step 5: Commit**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/EventController.java Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/EventControllerTest.java
git commit -m "fix: isolate event endpoints"
```

## Task 3: Healthy Query Device Ownership

**Files:**
- Create: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/HealthyDataControllerTest.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/HealthyDataController.java`

- [ ] **Step 1: Write the failing controller test**

```java
package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Service.HealthyDataService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorBreatheService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorFallService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorHumidityService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorRateService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorTemperatureService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import pojos.ContractMachine;
import pojos.ListResult;
import pojos.Result;
import pojos.SensorRate;
import util.CurrentHolder;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class HealthyDataControllerTest {

    @Mock private HealthyDataService healthyDataService;
    @Mock private SensorTemperatureService sensorTemperatureService;
    @Mock private SensorHumidityService sensorHumidityService;
    @Mock private SensorRateService sensorRateService;
    @Mock private SensorBreatheService sensorBreatheService;
    @Mock private SensorFallService sensorFallService;
    @Mock private ContractMachineMapper contractMachineMapper;

    private HealthyDataController controller;

    @BeforeEach
    void setUp() {
        controller = new HealthyDataController();
        ReflectionTestUtils.setField(controller, "healthyDataService", healthyDataService);
        ReflectionTestUtils.setField(controller, "sensorTemperatureService", sensorTemperatureService);
        ReflectionTestUtils.setField(controller, "sensorHumidityService", sensorHumidityService);
        ReflectionTestUtils.setField(controller, "sensorRateService", sensorRateService);
        ReflectionTestUtils.setField(controller, "sensorBreatheService", sensorBreatheService);
        ReflectionTestUtils.setField(controller, "sensorFallService", sensorFallService);
        ReflectionTestUtils.setField(controller, "contractMachineMapper", contractMachineMapper);
    }

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
    }

    @Test
    void rateQueryAllowsOwnedDevice() {
        CurrentHolder.setCurrentId(7);
        when(contractMachineMapper.findByUserIdAndConnectionId("7", "WALLE_1")).thenReturn(new ContractMachine());
        when(healthyDataService.getRate("WALLE_1")).thenReturn(new ListResult<>(List.of(new SensorRate())));

        Result result = controller.getRate("WALLE_1");

        assertThat(result.getCode()).isEqualTo(1);
        verify(healthyDataService).getRate("WALLE_1");
    }

    @Test
    void rateQueryRejectsDeviceNotOwnedByCurrentUser() {
        CurrentHolder.setCurrentId(7);
        when(contractMachineMapper.findByUserIdAndConnectionId("7", "OTHER")).thenReturn(null);

        Result result = controller.getRate("OTHER");

        assertThat(result.getCode()).isEqualTo(0);
        assertThat(result.getMsg()).contains("设备不存在或不属于当前用户");
        verify(healthyDataService, never()).getRate("OTHER");
    }
}
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=HealthyDataControllerTest test
```

Expected: FAIL because `HealthyDataController` does not have `contractMachineMapper` and does not check ownership.

- [ ] **Step 3: Implement minimal ownership check**

In `HealthyDataController.java`, add imports and field:

```java
import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import util.CurrentHolder;
```

```java
@Autowired
private ContractMachineMapper contractMachineMapper;
```

Add helper:

```java
private Result rejectIfNotOwned(String deviceId) {
    Integer currentUserId = CurrentHolder.getCurrentId();
    if (currentUserId == null ||
            contractMachineMapper.findByUserIdAndConnectionId(String.valueOf(currentUserId), deviceId) == null) {
        return Result.error("设备不存在或不属于当前用户");
    }
    return null;
}
```

Apply it to every query method:

```java
@GetMapping("/getRate/{deviceId}")
public Result getRate(@PathVariable("deviceId") String deviceId){
    Result rejected = rejectIfNotOwned(deviceId);
    if (rejected != null) {
        return rejected;
    }
    ListResult<SensorRate> rateList = healthyDataService.getRate(deviceId);
    return Result.success(rateList);
}
```

Use the same first three lines for `getHumidity`, `getBreathe`, `getTemperature`, and `getFall`, then call the existing service method.

- [ ] **Step 4: Run the test and verify GREEN**

Run:

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=HealthyDataControllerTest test
```

Expected: PASS, `Tests run: 2, Failures: 0, Errors: 0`.

- [ ] **Step 5: Commit**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/HealthyDataController.java Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/HealthyDataControllerTest.java
git commit -m "fix: protect healthy queries by device owner"
```

## Task 4: Healthy Fall Query SQL

**Files:**
- Create: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapperSqlTest.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapper.java`

- [ ] **Step 1: Write the failing SQL annotation test**

```java
package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Select;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

import static org.assertj.core.api.Assertions.assertThat;

class HealthyDataMapperSqlTest {

    @Test
    void getFallFiltersByDeviceId() throws Exception {
        Method method = HealthyDataMapper.class.getMethod("getFall", String.class);
        Select select = method.getAnnotation(Select.class);
        String sql = String.join(" ", select.value()).toLowerCase();

        assertThat(sql).contains("where device_id = #{deviceid}");
        assertThat(sql).contains("order by created_at desc");
        assertThat(sql).contains("limit 1");
    }
}
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=HealthyDataMapperSqlTest test
```

Expected: FAIL because current `getFall` SQL has no `WHERE device_id = #{deviceId}`.

- [ ] **Step 3: Fix mapper SQL**

Change `HealthyDataMapper.getFall` to:

```java
@Select("SELECT * FROM sensor_fall " +
        "WHERE device_id = #{deviceId} " +
        "ORDER BY created_at DESC " +
        "LIMIT 1")
SensorFall getFall(String deviceId);
```

- [ ] **Step 4: Run the test and verify GREEN**

Run:

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=HealthyDataMapperSqlTest test
```

Expected: PASS, `Tests run: 1, Failures: 0, Errors: 0`.

- [ ] **Step 5: Commit**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapper.java Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Mapper/HealthyDataMapperSqlTest.java
git commit -m "fix: filter fall data by device"
```

## Task 5: Token Filter Whitelist Tightening

**Files:**
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Filter/TokenFilter.java`

- [ ] **Step 1: Inspect current whitelist**

Run:

```bash
sed -n '25,55p' Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Filter/TokenFilter.java
```

Expected: current whitelist includes broad `requestURI.startsWith("/api/healthy")` and `requestURI.startsWith("/api/events/search")`.

- [ ] **Step 2: Replace broad healthy/event whitelist with write-only healthy endpoints**

Change the first whitelist block to:

```java
boolean publicHealthyIngest =
        requestURI.equals("/api/healthy/addRate") ||
        requestURI.equals("/api/healthy/addHumidity") ||
        requestURI.equals("/api/healthy/addBreathe") ||
        requestURI.equals("/api/healthy/addTemperature") ||
        requestURI.equals("/api/healthy/addFall");

if (!requestURI.startsWith("/api/") ||
        publicHealthyIngest ||
        requestURI.startsWith("/api/robot/video-feed/") ||
        requestURI.startsWith("/api/robot/video-feed-low/") ||
        requestURI.startsWith("/api/robot/camera-frame/") ||
        requestURI.startsWith("/api/users/getId") ||
        requestURI.startsWith("/api/system-config/public")
) {
    System.out.println("[TokenFilter] 公开路径，直接放行");
    filterChain.doFilter(request, response);
    return;
}
```

- [ ] **Step 3: Run a focused compile/test check**

Run:

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement -Dtest=ContractUserControllerTest,EventControllerTest,HealthyDataControllerTest,HealthyDataMapperSqlTest test
```

Expected: PASS, all focused tests green.

- [ ] **Step 4: Commit**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Filter/TokenFilter.java
git commit -m "fix: require token for isolated query endpoints"
```

## Task 6: Final Verification

**Files:**
- Review only: `Software-web/src/api/users.js`
- Review only: `Software-web/src/utils/request.js`
- Review only: `scripts/simulate_health_data.py`

- [ ] **Step 1: Confirm front-end requests already attach token**

Run:

```bash
sed -n '1,90p' Software-web/src/utils/request.js
```

Expected: `request.interceptors.request.use` reads `loginUserObject` from local storage and assigns `config.headers.token = loginUser.token`; no frontend code change is needed for token-protected query endpoints.

- [ ] **Step 2: Confirm health simulator still targets public ingest endpoints**

Run:

```bash
rg -n "addRate|addHumidity|addBreathe|addTemperature|addFall|getRate|getHumidity|getBreathe|getTemperature|getFall" scripts/simulate_health_data.py
```

Expected: simulator only calls `add*` endpoints and does not call token-protected `get*` endpoints.

- [ ] **Step 3: Run full backend tests**

Run:

```bash
mvn -f Parent/pom.xml -pl ../cpnRobotManagement test
```

Expected: BUILD SUCCESS, no failures.

- [ ] **Step 4: Run frontend build**

Run:

```bash
npm run build
```

Working directory: `Software-web`.

Expected: Vite build succeeds. Existing warnings about legacy scripts and chunk size may remain.

- [ ] **Step 5: Check git status**

Run:

```bash
git status --short --branch
```

Expected: only known unrelated deployment docs remain modified, plus no uncommitted files from this plan.
