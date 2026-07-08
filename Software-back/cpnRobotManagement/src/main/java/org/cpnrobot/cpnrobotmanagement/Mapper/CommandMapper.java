package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.Command;

import java.util.List;

@Mapper
public interface CommandMapper {

    @Select("""
            select id,
                   device_id as deviceId,
                   type,
                   machines,
                   user_id as userId,
                   timestamp,
                   message_id as messageId,
                   time,
                   created_at as createdAt,
                   type as commandName,
                   '已执行' as commandCode
            from command
            where machines = #{machines} and user_id = #{userId}
            order by time desc
            """)
    List<Command> search(Command command);
}
