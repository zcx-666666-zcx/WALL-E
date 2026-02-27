-- 新的传感器数据表结构设计
-- 每个传感器数据独立存储，支持单个数据变化时的单独插入

-- 跌倒传感器数据表
CREATE TABLE IF NOT EXISTS sensor_fall (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    device_id VARCHAR(100) NOT NULL COMMENT '设备ID',
    fall BOOLEAN NOT NULL COMMENT '跌倒状态(true:跌倒,false:正常)',
    timestamp BIGINT NOT NULL COMMENT '数据时间戳(毫秒)',
    message_id VARCHAR(100) COMMENT 'OneNET消息ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    INDEX idx_device_time (device_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='跌倒传感器数据表';

-- 温度传感器数据表
CREATE TABLE IF NOT EXISTS sensor_temperature (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    device_id VARCHAR(100) NOT NULL COMMENT '设备ID',
    temperature DOUBLE NOT NULL COMMENT '温度值(℃)',
    timestamp BIGINT NOT NULL COMMENT '数据时间戳(毫秒)',
    message_id VARCHAR(100) COMMENT 'OneNET消息ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    INDEX idx_device_time (device_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='温度传感器数据表';

-- 湿度传感器数据表
CREATE TABLE IF NOT EXISTS sensor_humidity (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    device_id VARCHAR(100) NOT NULL COMMENT '设备ID',
    humidity DOUBLE NOT NULL COMMENT '湿度值(%)',
    timestamp BIGINT NOT NULL COMMENT '数据时间戳(毫秒)',
    message_id VARCHAR(100) COMMENT 'OneNET消息ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    INDEX idx_device_time (device_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='湿度传感器数据表';

-- 心率传感器数据表
CREATE TABLE IF NOT EXISTS sensor_rate (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    device_id VARCHAR(100) NOT NULL COMMENT '设备ID',
    rate INTEGER NOT NULL COMMENT '心率值(bpm)',
    timestamp BIGINT NOT NULL COMMENT '数据时间戳(毫秒)',
    message_id VARCHAR(100) COMMENT 'OneNET消息ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    INDEX idx_device_time (device_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='心率传感器数据表';

-- 呼吸频率传感器数据表
CREATE TABLE IF NOT EXISTS sensor_breathe (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    device_id VARCHAR(100) NOT NULL COMMENT '设备ID',
    breathe INTEGER NOT NULL COMMENT '呼吸频率值(breaths/min)',
    timestamp BIGINT NOT NULL COMMENT '数据时间戳(毫秒)',
    message_id VARCHAR(100) COMMENT 'OneNET消息ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    INDEX idx_device_time (device_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='呼吸频率传感器数据表';

-- 如果需要保留原有的汇总表，可以创建视图
CREATE OR REPLACE VIEW sensor_data_view AS
SELECT 
    COALESCE(f.timestamp, t.timestamp, h.timestamp, r.timestamp, b.timestamp) as timestamp,
    COALESCE(f.device_id, t.device_id, h.device_id, r.device_id, b.device_id) as device_id,
    f.fall,
    t.temperature,
    h.humidity,
    r.rate,
    b.breathe
FROM sensor_fall f
FULL OUTER JOIN sensor_temperature t ON f.device_id = t.device_id AND f.timestamp = t.timestamp
FULL OUTER JOIN sensor_humidity h ON f.device_id = h.device_id AND f.timestamp = h.timestamp
FULL OUTER JOIN sensor_rate r ON f.device_id = r.device_id AND f.timestamp = r.timestamp
FULL OUTER JOIN sensor_breathe b ON f.device_id = b.device_id AND f.timestamp = b.timestamp
ORDER BY timestamp DESC;
