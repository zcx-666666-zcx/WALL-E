# 非遗传承小程序API连接问题修复文档

## 一、问题描述

在开发非遗传承微信小程序的过程中，遇到了前后端连接失败的问题。具体表现为：

### 1. 错误现象
- 微信小程序在调用后端API时出现网络错误
- 浏览器控制台报错信息：
  ```
  http://localhost:8001/api/auth/register:1 Failed to load resource: net::ERR_CONNECTION_REFUSED
  ```

### 2. 影响范围
- 用户注册功能无法正常使用
- 用户登录功能无法正常使用
- 所有需要与后端交互的功能均受到影响

## 二、问题分析

通过对项目代码和运行环境的分析，确定了两个主要原因：

### 1. 端口配置不一致
- 微信小程序前端代码中配置的后端API地址为：`http://localhost:8001`
- 实际后端服务运行在端口：`8001`
- 端口不匹配导致连接被拒绝

### 2. 数据库配置问题
- 后端服务配置中指定了数据库名称为：`intangible_heritage`
- MySQL中缺少该数据库导致服务启动失败
- 即使端口配置正确，也会因服务未正常启动而连接失败

## 三、解决方案

### 1. 修复端口配置问题

#### 修改位置：
`/Users/zhangchenxi/Desktop/CodeProjects/微信小程序/chuanzhifron/utils/util.js`

#### 修改内容：
将文件中的API基础URL从：
```
url: `http://localhost:8001/api${options.url}`
```

修改为：
```
url: `http://localhost:8001/api${options.url}`
```

#### 实现方式：
使用sed命令批量替换：
```
sed -i '' 's/http:\/\/localhost:8001/http:\/\/localhost:8001/g' /Users/zhangchenxi/Desktop/CodeProjects/微信小程序/chuanzhifron/utils/util.js
```

### 2. 创建缺失的数据库

#### 操作步骤：
1. 连接到MySQL数据库：
   ```bash
   mysql -u root -p
   ```

2. 创建数据库：
   ```sql
   CREATE DATABASE IF NOT EXISTS intangible_heritage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. 验证数据库创建成功：
   ```sql
   SHOW DATABASES LIKE 'intangible_heritage';
   ```

### 3. 验证修复结果

#### 后端服务验证：
1. 启动后端服务：
   ```bash
   cd /Users/zhangchenxi/Desktop/CodeProjects/微信小程序/chuanzhiback/demo
   ./mvnw spring-boot:run
   ```

2. 确认服务正常启动，无数据库连接错误

#### API接口验证：
1. 测试GET请求：
   ```bash
   curl -X GET http://localhost:8081/api/news
   ```

2. 测试POST请求：
   ```bash
   curl -X POST http://localhost:8081/api/news -H "Content-Type: application/json" -d '{"title":"测试新闻","description":"这是一个测试新闻","imageUrl":"https://example.com/test.jpg"}'
   ```

## 四、预防措施

### 1. 配置文件统一管理
- 将API地址等配置信息集中管理，避免硬编码
- 使用环境变量区分开发、测试和生产环境

### 2. 数据库初始化脚本
- 编写数据库初始化脚本，确保开发环境的一致性
- 在项目文档中明确列出依赖的服务和初始化步骤

### 3. 启动检查机制
- 在项目启动时增加配置检查和依赖服务检查
- 提供一键启动脚本，自动完成环境准备和服务启动

## 五、后续改进建议

### 1. 环境配置优化
- 使用配置文件管理不同环境的设置
- 实现配置的热加载，无需重启服务即可生效

### 2. 错误处理增强
- 增加网络连接失败的友好提示
- 实现自动重连机制，提高用户体验

### 3. 文档完善
- 更新项目文档，明确环境搭建步骤
- 提供常见问题解答，便于快速定位和解决问题

## 六、总结

本次问题的根本原因是配置不一致导致的服务连接失败。通过统一端口配置和修复数据库问题，成功解决了API连接问题。后续应加强配置管理和环境一致性，避免类似问题再次发生。