package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.Command;

import java.util.List;

@Mapper
public interface CommandMapper {

    @Select("select * from command where machines = #{machines} and user_id = #{userId} order by time desc")
    List<Command> search(Command command);
}
