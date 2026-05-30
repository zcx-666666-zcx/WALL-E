package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Select;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

import static org.assertj.core.api.Assertions.assertThat;

class HealthyDataMapperSqlTest {

    @Test
    void getFallFiltersByDeviceId() throws Exception {
        Method method = HealthyDataMapper.class.getMethod("getFall", String.class);
        Select select = method.getAnnotation(Select.class);
        String sql = String.join(" ", select.value()).toLowerCase();

        assertThat(sql).contains("where device_id = #{deviceid}");
        assertThat(sql).contains("order by created_at desc");
        assertThat(sql).contains("limit 1");
    }
}
