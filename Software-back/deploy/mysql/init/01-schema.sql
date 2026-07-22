SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS cpnrobot DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE cpnrobot;

CREATE TABLE IF NOT EXISTS user (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL UNIQUE,
  phone_number VARCHAR(32),
  password VARCHAR(128) NOT NULL,
  role VARCHAR(32) NOT NULL DEFAULT 'user',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contract_machine (
  id INT PRIMARY KEY AUTO_INCREMENT,
  machines VARCHAR(128) NOT NULL,
  connectionId VARCHAR(128),
  user_id VARCHAR(64),
  robot_ip VARCHAR(128),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_contract_machine_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contract_user (
  id INT PRIMARY KEY AUTO_INCREMENT,
  contract_name VARCHAR(128) NOT NULL,
  contract_phone_number VARCHAR(32),
  user_id INT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_contract_user_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS event (
  id INT PRIMARY KEY AUTO_INCREMENT,
  event_name VARCHAR(128) NOT NULL,
  event_date DATE,
  event_time TIME,
  repeat_days INT,
  priority VARCHAR(32),
  machines VARCHAR(128),
  description TEXT,
  user_id VARCHAR(64),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_event_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS command (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  device_id VARCHAR(128),
  type VARCHAR(64),
  machines VARCHAR(128),
  user_id VARCHAR(64),
  timestamp BIGINT,
  message_id VARCHAR(128),
  time DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_command_machine_user (machines, user_id),
  INDEX idx_command_device (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS device_message (
  id INT PRIMARY KEY AUTO_INCREMENT,
  msg TEXT,
  nonce VARCHAR(64),
  signature VARCHAR(128),
  push_time BIGINT,
  message_id VARCHAR(128),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS device_network_status (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  device_id VARCHAR(128) NOT NULL UNIQUE,
  user_id VARCHAR(64) NOT NULL,
  lan_ip VARCHAR(45),
  observed_ip VARCHAR(45),
  network_name VARCHAR(128),
  last_seen_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_device_network_last_seen (last_seen_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sensor_data (
  id BIGINT PRIMARY KEY,
  fall BOOLEAN,
  temperature DOUBLE,
  humidity DOUBLE,
  rate INT,
  breathe INT,
  device_id VARCHAR(128),
  timestamp BIGINT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_sensor_data_device (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sensor_rate (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  device_id VARCHAR(128),
  rate INT,
  timestamp BIGINT,
  message_id VARCHAR(128),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_sensor_rate_device (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sensor_temperature (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  device_id VARCHAR(128),
  temperature DOUBLE,
  timestamp BIGINT,
  message_id VARCHAR(128),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_sensor_temperature_device (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sensor_humidity (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  device_id VARCHAR(128),
  humidity DOUBLE,
  timestamp BIGINT,
  message_id VARCHAR(128),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_sensor_humidity_device (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sensor_breathe (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  device_id VARCHAR(128),
  breathe INT,
  timestamp BIGINT,
  message_id VARCHAR(128),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_sensor_breathe_device (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sensor_fall (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  device_id VARCHAR(128),
  fall BOOLEAN,
  timestamp BIGINT,
  message_id VARCHAR(128),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_sensor_fall_device (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS system_config (
  id INT PRIMARY KEY AUTO_INCREMENT,
  config_key VARCHAR(128) NOT NULL UNIQUE,
  config_value TEXT,
  label VARCHAR(128) NOT NULL,
  config_group VARCHAR(64) NOT NULL DEFAULT 'basic',
  secret BOOLEAN NOT NULL DEFAULT FALSE,
  remark VARCHAR(255),
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS voice_profile (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  name VARCHAR(128) NOT NULL,
  engine VARCHAR(32) NOT NULL DEFAULT 'zero_shot',
  status VARCHAR(32) NOT NULL DEFAULT 'uploaded',
  reference_audio_path VARCHAR(1024) NOT NULL,
  reference_text TEXT,
  model_path VARCHAR(1024),
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  last_error TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_voice_profile_user (user_id),
  INDEX idx_voice_profile_default (user_id, is_default)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO user(username, phone_number, password, role)
VALUES ('admin', '', 'admin123', 'admin')
ON DUPLICATE KEY UPDATE password = VALUES(password), role = VALUES(role);

INSERT INTO system_config(config_key, config_value, label, config_group, secret, remark) VALUES
('api.base-url', 'http://localhost:8080/api', '后端 API 地址', 'network', false, 'Web、小程序和硬件端访问 Java 后端的 API 根地址'),
('web.base-url', 'http://localhost:5173', 'Web 前端地址', 'network', false, 'Vue 管理端访问地址'),
('static.base-url', 'http://localhost:8080', '静态资源地址', 'network', false, '图片、视频等静态资源根地址'),
('robot.default-ip', '127.0.0.1', '机器人默认 IP', 'robot', false, '新增机器人时的默认 IP，可按设备单独覆盖'),
('robot.http-port', '5000', '机器人 HTTP 端口', 'robot', false, '树莓派 Web 控制服务端口'),
('socket.server-url', 'http://localhost:8081', 'Socket 服务地址', 'robot', false, '机器人遥控和视频信令地址'),
('robot.tts-stream-port', '6007', 'TTS 流式播放端口', 'robot', false, '树莓派 tts_stream_player.py 监听端口'),
('voice.service-url', 'http://127.0.0.1:7862', '本地音色服务地址', 'voice', false, '台式机本地 Python voice-service 地址'),
('voice.storage-root', 'D:/WALL-E/data', '音色文件存储根目录', 'voice', false, '音频样本、训练输出和合成缓存默认放到 D 盘'),
('ai.agent-api-url', '', 'AI Agent 服务地址', 'third_party', false, '瓦利人设和对话服务地址，例如 http://localhost:6006'),
('liveness.api-url', '', '活体检测服务地址', 'third_party', false, '视频通话前的人脸活体检测服务地址'),
('coze.api-url', 'https://api.coze.cn', 'Coze API 地址', 'third_party', false, 'AI 对话/工作流 API 根地址'),
('coze.workflow-id', '', 'Coze 工作流 ID', 'third_party', false, 'AI 工作流标识'),
('coze.token', '', 'Coze Token', 'secret', true, '第三方 AI Token'),
('onenet.token', '123456789', 'OneNET Token', 'secret', true, 'OneNET 回调校验 Token'),
('onenet.aes-key', 'your-onenet-aes-base64-key', 'OneNET AES Key', 'secret', true, 'OneNET 消息加密密钥')
ON DUPLICATE KEY UPDATE
  config_value = VALUES(config_value),
  label = VALUES(label),
  config_group = VALUES(config_group),
  secret = VALUES(secret),
  remark = VALUES(remark);
