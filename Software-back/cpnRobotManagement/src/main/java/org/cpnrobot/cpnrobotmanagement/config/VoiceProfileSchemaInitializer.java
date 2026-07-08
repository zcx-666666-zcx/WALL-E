package org.cpnrobot.cpnrobotmanagement.config;

import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
public class VoiceProfileSchemaInitializer {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @PostConstruct
    public void init() {
        jdbcTemplate.execute("""
                create table if not exists voice_profile (
                  id bigint primary key auto_increment,
                  user_id int not null,
                  name varchar(128) not null,
                  engine varchar(32) not null default 'zero_shot',
                  status varchar(32) not null default 'uploaded',
                  reference_audio_path varchar(1024) not null,
                  reference_text text,
                  model_path varchar(1024),
                  is_default boolean not null default false,
                  last_error text,
                  created_at datetime not null default current_timestamp,
                  updated_at datetime not null default current_timestamp on update current_timestamp,
                  index idx_voice_profile_user (user_id),
                  index idx_voice_profile_default (user_id, is_default)
                ) engine=InnoDB default charset=utf8mb4 collate=utf8mb4_unicode_ci
                """);
        upsertConfig("robot.tts-stream-port", "6007", "TTS 流式播放端口", "robot", "树莓派 tts_stream_player.py 监听端口");
        upsertConfig("voice.service-url", "http://127.0.0.1:7862", "本地音色服务地址", "voice", "台式机本地 Python voice-service 地址");
        upsertConfig("voice.storage-root", "D:/WALL-E/data", "音色文件存储根目录", "voice", "音频样本、训练输出和合成缓存默认放到 D 盘");
    }

    private void upsertConfig(String key, String value, String label, String group, String remark) {
        jdbcTemplate.update("""
                insert into system_config(config_key, config_value, label, config_group, secret, remark)
                values (?, ?, ?, ?, false, ?)
                on duplicate key update
                  label = values(label),
                  config_group = values(config_group),
                  secret = values(secret),
                  remark = values(remark)
                """, key, value, label, group, remark);
    }
}
