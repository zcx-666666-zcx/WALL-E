package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Select;
import org.junit.jupiter.api.Test;
import pojos.Command;

import java.lang.reflect.Method;

import static org.assertj.core.api.Assertions.assertThat;

class CommandMapperSqlTest {

    @Test
    void searchUsesCommandFieldsAndReturnsUiAliases() throws Exception {
        Command command = new Command();
        command.setMachines("瓦力");
        command.setUserId("7");

        assertThat(command.getMachines()).isEqualTo("瓦力");
        assertThat(command.getUserId()).isEqualTo("7");

        Method method = CommandMapper.class.getMethod("search", Command.class);
        Select select = method.getAnnotation(Select.class);
        String sql = String.join(" ", select.value()).toLowerCase();

        assertThat(sql).contains("#{machines}");
        assertThat(sql).contains("#{userid}");
        assertThat(sql).contains("type as commandname");
        assertThat(sql).contains("as commandcode");
    }
}
