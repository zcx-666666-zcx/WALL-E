package org.cpnrobot.cpnrobotmanagement.Mapper;


import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.Event;

import java.util.List;

@Mapper
public interface EventMapper {

    @Insert("insert into event(event_name,event_date,event_time,repeat_days,priority,machines,description,user_id) values(#{eventName},#{eventDate},#{eventTime},#{repeatDays},#{priority},#{machines},#{description},#{userId})")
    int addEvent(Event event);

    @Select("select * from event where user_id = #{userId}")
    List<Event> searchEvent(String userId);
}
