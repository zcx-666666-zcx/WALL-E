-- 数据库初始化脚本
-- 创建cpnrobot数据库所需的表结构

-- 使用cpnrobot数据库
USE cpnrobot;

-- 创建device_message表（用于存储OneNET推送的原始数据）
CREATE TABLE IF NOT EXISTS device_message (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    msg TEXT COMMENT '消息内容（JSON字符串或密文）',
    nonce VARCHAR(32) COMMENT '随机字符串',
    signature VARCHAR(128) COMMENT '消息签名',
    push_time BIGINT COMMENT '推送时间戳（毫秒）',
    message_id VARCHAR(64) COMMENT '消息ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OneNET设备消息表';

-- 创建user表（用户表）
CREATE TABLE IF NOT EXISTS user (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    phone_number VARCHAR(20) COMMENT '手机号',
    password VARCHAR(100) NOT NULL COMMENT '密码'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 创建event表（事件表）
CREATE TABLE IF NOT EXISTS event (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '事件ID',
    event_name VARCHAR(100) NOT NULL COMMENT '事件名称',
    event_date DATE COMMENT '事件日期',
    event_time TIME COMMENT '事件时间',
    repeat_days INT DEFAULT 0 COMMENT '重复天数',
    priority VARCHAR(20) COMMENT '优先级',
    machines VARCHAR(200) COMMENT '涉及设备',
    description TEXT COMMENT '描述',
    user_id VARCHAR(50) COMMENT '用户ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='事件表';

-- 创建contract_user表（合同用户表）
CREATE TABLE IF NOT EXISTS contract_user (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    contract_name VARCHAR(100) COMMENT '合同名称',
    contract_phone_number VARCHAR(20) COMMENT '联系电话',
    user_id INT COMMENT '用户ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='合同用户表';

-- 创建contract_machine表（合同设备表）
CREATE TABLE IF NOT EXISTS contract_machine (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    machine_name VARCHAR(100) COMMENT '设备名称',
    machine_type VARCHAR(50) COMMENT '设备类型',
    user_id INT COMMENT '用户ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='合同设备表';

-- 创建command表（指令表）
CREATE TABLE IF NOT EXISTS command (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '指令ID',
    command_name VARCHAR(100) NOT NULL COMMENT '指令名称',
    command_content TEXT COMMENT '指令内容',
    user_id INT COMMENT '用户ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='指令表';

-- 如果需要创建zzulicloud数据库和表，请取消下面的注释
/*
-- 创建zzulicloud数据库
CREATE DATABASE IF NOT EXISTS zzulicloud CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用zzulicloud数据库
USE zzulicloud;

-- 创建onenet_device_message表（用于同步OneNET数据）
CREATE TABLE IF NOT EXISTS onenet_device_message (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    msg TEXT COMMENT '消息内容（JSON字符串或密文）',
    nonce VARCHAR(32) COMMENT '随机字符串',
    signature VARCHAR(128) COMMENT '消息签名',
    push_time BIGINT COMMENT '推送时间戳（毫秒）',
    message_id VARCHAR(64) COMMENT '消息ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OneNET设备消息同步表';
*/