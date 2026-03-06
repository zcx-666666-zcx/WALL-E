# 1. 使用 Java 21 的轻量级运行环境（关键修改点）
FROM eclipse-temurin:21-jre-alpine

# 2. 指定工作目录
WORKDIR /app

# 3. 将刚刚打包好的 jar 包复制进去
COPY cpnRobotManagement/target/cpnRobotManagement-0.0.1-SNAPSHOT.jar app.jar

# 4. 暴露端口
EXPOSE 8080

# 5. 启动项目
ENTRYPOINT ["java", "-jar", "app.jar"]