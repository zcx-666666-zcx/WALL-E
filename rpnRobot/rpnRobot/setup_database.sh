#!/bin/bash

# 数据库设置脚本
# 用于创建cpnrobot数据库和必要的表结构

echo "开始设置数据库..."

# MySQL连接信息
MYSQL_USER="root"
MYSQL_PASS="20250709"
DATABASE_NAME="cpnrobot"

# 创建数据库和表的SQL命令
SQL_COMMANDS="
CREATE DATABASE IF NOT EXISTS $DATABASE_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE $DATABASE_NAME;

CREATE TABLE IF NOT EXISTS device_message (
    id INT PRIMARY KEY AUTO_INCREMENT,
    msg TEXT,
    nonce VARCHAR(32),
    signature VARCHAR(128),
    push_time BIGINT,
    message_id VARCHAR(64)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    password VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS event (
    id INT PRIMARY KEY AUTO_INCREMENT,
    event_name VARCHAR(100) NOT NULL,
    event_date DATE,
    event_time TIME,
    repeat_days INT DEFAULT 0,
    priority VARCHAR(20),
    machines VARCHAR(200),
    description TEXT,
    user_id VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS contract_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    contract_name VARCHAR(100),
    contract_phone_number VARCHAR(20),
    user_id INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS contract_machine (
    id INT PRIMARY KEY AUTO_INCREMENT,
    machine_name VARCHAR(100),
    machine_type VARCHAR(50),
    user_id INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS command (
    id INT PRIMARY KEY AUTO_INCREMENT,
    command_name VARCHAR(100) NOT NULL,
    command_content TEXT,
    user_id INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 验证表创建
SHOW TABLES;
"

# 执行SQL命令
echo "正在创建数据库和表..."
if mysql -u"$MYSQL_USER" -p"$MYSQL_PASS" -e "$SQL_COMMANDS"; then
    echo "✅ 数据库和表创建成功！"
    echo "✅ device_message 表已创建"
    echo "✅ 其他相关表已创建"
else
    echo "❌ 数据库设置失败，请检查MySQL服务是否运行以及连接信息是否正确"
    exit 1
fi

echo "数据库设置完成！"