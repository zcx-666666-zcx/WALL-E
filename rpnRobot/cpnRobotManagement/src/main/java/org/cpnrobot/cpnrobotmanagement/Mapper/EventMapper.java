package org.cpnrobot.cpnrobotmanagement.Mapper;


import org.apache.ibatis.annotations.*;
import pojos.Event;

import java.util.List;

@Mapper
public interface EventMapper {

    @Insert("insert into event(event_name,event_date,event_time,repeat_days,priority,machines,description,user_id) values(#{eventName},#{eventDate},#{eventTime},#{repeatDays},#{priority},#{machines},#{description},#{userId})")
    int addEvent(Event event);

    @Select("select * from event where user_id = #{userId}")
    List<Event> searchEvent(String userId);

    @Delete("delete from event where event_name = #{eventName} and user_id = #{userId}")
    int deleteEvent(Event event);

    @Select("select * from event where event_name = #{eventName} and user_id = #{userId}")
    Event searchOne(Event event);

    @Update("update event set event_name = #{eventName},event_date = #{eventDate},event_time = #{eventTime},repeat_days = #{repeatDays},priority = #{priority},machines = #{machines},description = #{description} where event_name = #{eventName} and user_id = #{userId}")
    int updateEvent(Event event);
}
