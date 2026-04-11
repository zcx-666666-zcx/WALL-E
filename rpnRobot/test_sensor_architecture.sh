#!/bin/bash

# 传感器数据架构测试脚本

echo "=== 传感器数据架构升级测试 ==="

echo "1. 检查新创建的文件..."
echo "数据库脚本:"
ls -la database/sensor_data_tables.sql

echo -e "\n实体类:"
ls -la Pojo/src/main/java/pojos/Sensor*.java

echo -e "\nMapper接口:"
ls -la cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/Sensor*Mapper.java

echo -e "\nService接口:"
ls -la cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/Sensor*Service.java

echo -e "\nService实现类:"
ls -la cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Service/impl/Sensor*ServiceImpl.java

echo -e "\n控制器:"
ls -la cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Controller/SensorDataController.java

echo -e "\n2. 显示关键文件内容预览..."

echo -e "\nsensor_fall表结构:"
head -10 database/sensor_data_tables.sql

echo -e "\nSensorFall实体类:"
head -10 Pojo/src/main/java/pojos/SensorFall.java

echo -e "\nSensorFallMapper接口:"
head -10 cpnRobotManagement/src/main/java/org/cpnrobot/cpnrobotmanagement/Mapper/SensorFallMapper.java

echo -e "\n3. 编译检查..."
cd cpnRobotManagement
mvn compile -q
if [ $? -eq 0 ]; then
    echo "✅ 编译成功"
else
    echo "❌ 编译失败"
fi
cd ..

echo -e "\n=== 测试完成 ==="
echo "请按以下步骤部署:"
echo "1. 执行 database/sensor_data_tables.sql 创建新表"
echo "2. 重启应用服务"
echo "3. 测试API接口: GET /sensor/latest"