package org.cpnrobot.cpnrobotmanagement.config;

import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;

import static org.assertj.core.api.Assertions.assertThat;

class DeviceNetworkSchemaInitializerTest {

    @Test
    void createsNetworkStatusTableForExistingDatabases() {
        RecordingJdbcTemplate jdbcTemplate = new RecordingJdbcTemplate();
        DeviceNetworkSchemaInitializer initializer = new DeviceNetworkSchemaInitializer(jdbcTemplate);

        initializer.initialize();

        assertThat(jdbcTemplate.sql).contains("device_network_status");
    }

    private static class RecordingJdbcTemplate extends JdbcTemplate {
        private String sql;

        @Override
        public void execute(String sql) {
            this.sql = sql;
        }

        @Override
        public <T> T queryForObject(String sql, Class<T> requiredType) {
            return requiredType.cast(1);
        }
    }
}
