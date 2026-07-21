package org.cpnrobot.cpnrobotmanagement.config;

import jakarta.annotation.PostConstruct;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
public class DeviceNetworkSchemaInitializer {

    private final JdbcTemplate jdbcTemplate;

    public DeviceNetworkSchemaInitializer(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @PostConstruct
    public void initialize() {
        jdbcTemplate.execute("""
                create table if not exists device_network_status (
                  id bigint primary key auto_increment,
                  device_id varchar(128) not null unique,
                  user_id varchar(64) not null,
                  lan_ip varchar(45),
                  observed_ip varchar(45),
                  network_name varchar(128),
                  last_seen_at datetime not null,
                  created_at datetime not null default current_timestamp,
                  updated_at datetime not null default current_timestamp on update current_timestamp,
                  index idx_device_network_last_seen (last_seen_at)
                ) engine=InnoDB default charset=utf8mb4 collate=utf8mb4_unicode_ci
                """);
        Integer userColumnCount = jdbcTemplate.queryForObject("""
                select count(*) from information_schema.columns
                where table_schema = database()
                  and table_name = 'device_network_status'
                  and column_name = 'user_id'
                """, Integer.class);
        if (userColumnCount != null && userColumnCount == 0) {
            jdbcTemplate.execute("""
                    alter table device_network_status
                    add column user_id varchar(64) null after device_id
                    """);
        }
    }
}
