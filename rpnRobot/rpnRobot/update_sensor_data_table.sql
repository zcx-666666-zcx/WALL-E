-- 传感器数据表结构更新脚本
-- 用于创建sensor_data表并优化数据存储

USE cpnrobot;

-- 创建传感器数据表
CREATE TABLE IF NOT EXISTS sensor_data (
    id BIGINT PRIMARY KEY COMMENT '时间戳作为唯一ID',
    fall BOOLEAN DEFAULT FALSE COMMENT '跌倒状态',
    temperature DOUBLE DEFAULT 0.0 COMMENT '温度',
    humidity DOUBLE DEFAULT 0.0 COMMENT '湿度',
    rate INTEGER DEFAULT 0 COMMENT '心率',
    breathe INTEGER DEFAULT 0 COMMENT '呼吸频率',
    device_id VARCHAR(64) COMMENT '设备ID',
    timestamp BIGINT COMMENT '数据时间戳',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器数据表';

-- 添加索引以提高查询性能
ALTER TABLE sensor_data ADD INDEX idx_device_id (device_id);
ALTER TABLE sensor_data ADD INDEX idx_timestamp (timestamp);
ALTER TABLE sensor_data ADD INDEX idx_created_at (created_at);

-- 如果需要清理旧的device_message表中的重复数据，可以执行以下语句：
-- DELETE t1 FROM device_message t1 INNER JOIN device_message t2 
-- WHERE t1.id > t2.id AND t1.message_id = t2.message_id;

-- 查看表结构
DESCRIBE sensor_data;

-- 查看索引
SHOW INDEX FROM sensor_data;