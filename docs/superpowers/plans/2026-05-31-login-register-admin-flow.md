# Login / Register / Admin Auth Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make login and registration behave cleanly end to end, keep `admin/admin123` as the initial super-admin entry, and route admins into the admin console after sign-in.

**Architecture:** Keep authentication rules on the backend, keep redirect decisions in the frontend router, and keep the login/register views thin. The backend should return specific auth failures so the UI can show them directly, while the admin seed stays in the SQL bootstrap file for fresh databases.

**Tech Stack:** Vue 3, Vue Router 4, Element Plus, Spring Boot, MyBatis, BCrypt, JUnit 5, Mockito.

---

### Task 1: Backend auth result codes and messages

**Files:**
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/LoginController.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/userController.java`
- Modify: `Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/userServiceImpl.java`
- Test: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/LoginControllerTest.java`
- Test: `Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/UserControllerTest.java`

- [ ] **Step 1: Write the failing tests**

```java
@Test
void loginRejectsMissingPassword() {
    User request = new User();
    request.setUsername("admin");

    Result result = controller.login(request);

    assertThat(result.getCode()).isEqualTo(0);
    assertThat(result.getMsg()).isEqualTo("请输入用户名和密码");
    verify(userService, never()).login(any());
}

@Test
void registerRejectsDuplicateUsername() {
    User request = new User();
    request.setUsername("admin");
    request.setPassword("admin123");
    when(userService.register(request)).thenReturn(2);

    Result result = controller.register(request);

    assertThat(result.getCode()).isEqualTo(0);
    assertThat(result.getMsg()).isEqualTo("用户名已存在");
}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `mvn -pl cpnRobotManagement -am test -Dtest=LoginControllerTest,UserControllerTest -DfailIfNoTests=false`
Expected: fail because the current controllers do not return the specific validation messages yet.

- [ ] **Step 3: Write the minimal implementation**

```java
if (user == null || user.getUsername() == null || user.getUsername().isBlank()
        || user.getPassword() == null || user.getPassword().isBlank()) {
    return Result.error("请输入用户名和密码");
}

int num = userservice.register(user);
if (num == 2) {
    return Result.error("用户名已存在");
}
```

- [ ] **Step 4: Run the tests again**

Run: `mvn -pl cpnRobotManagement -am test -Dtest=LoginControllerTest,UserControllerTest -DfailIfNoTests=false`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/LoginController.java \
  Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/userController.java \
  Software-back/cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/userServiceImpl.java \
  Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/LoginControllerTest.java \
  Software-back/cpnRobotManagement/src/test/java/org/cpnrobot/cpnrobotmanagement/Controller/UserControllerTest.java
git commit -m "修复登录注册提示"
```

### Task 2: Frontend login, register, and admin redirect

**Files:**
- Modify: `Software-web/src/views/login/login.vue`
- Modify: `Software-web/src/views/regis/regis.vue`
- Modify: `Software-web/src/router/index.js`

- [ ] **Step 1: Write the failing behavior checks**

```js
// login.vue should route admins to /admin and always clear loading in finally
// regis.vue should surface duplicate-username errors instead of showing a generic失败
```

- [ ] **Step 2: Run the app build or a browser smoke check**

Run: `npm run build`
Expected: the current code still lacks the requested admin redirect and defensive finally blocks.

- [ ] **Step 3: Write the minimal implementation**

```js
const targetPath = loginUser.role === 'admin' ? '/admin' : '/index'
router.replace(targetPath)

try {
  const result = await LoginApi(payload)
  ...
} catch (error) {
  ElMessage.error(error?.response?.data?.msg || error?.message || '登录失败')
} finally {
  loading.value = false
  log.value = '登 录'
}
```

- [ ] **Step 4: Run the build again**

Run: `npm run build`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add Software-web/src/views/login/login.vue \
  Software-web/src/views/regis/regis.vue \
  Software-web/src/router/index.js
git commit -m "完善登录注册与管理员跳转"
```

### Task 3: Keep the admin seed stable for fresh databases

**Files:**
- Modify: `Software-back/deploy/mysql/init/01-schema.sql`

- [ ] **Step 1: Confirm the seed row exists**

```sql
INSERT INTO user(username, phone_number, password, role)
VALUES ('admin', '', 'admin123', 'admin')
ON DUPLICATE KEY UPDATE password = VALUES(password), role = VALUES(role);
```

- [ ] **Step 2: Run a quick schema review**

Run: inspect the init SQL and confirm the admin row is still present.

- [ ] **Step 3: Commit if the file changed**

```bash
git add Software-back/deploy/mysql/init/01-schema.sql
git commit -m "保留管理员初始化账号"
```
