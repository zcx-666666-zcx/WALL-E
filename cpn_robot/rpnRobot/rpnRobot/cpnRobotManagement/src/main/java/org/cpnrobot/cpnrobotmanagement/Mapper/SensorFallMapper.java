package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.SensorFall;

import java.util.List;

/**
 * 跌倒传感器数据Mapper
 */
@Mapper
public interface SensorFallMapper {
    
    @Insert("INSERT INTO sensor_fall(device_id, fall, timestamp, message_id) " +
            "VALUES(#{deviceId}, #{fall}, #{timestamp}, #{messageId})")
    int insert(SensorFall sensorFall);
    
    @Select("SELECT * FROM sensor_fall WHERE device_id = #{deviceId} ORDER BY timestamp DESC")
    List<SensorFall> findByDeviceId(String deviceId);
    
    @Select("SELECT * FROM sensor_fall ORDER BY timestamp DESC LIMIT 1")
    SensorFall findLatest();
    
    @Select("SELECT * FROM sensor_fall WHERE timestamp BETWEEN #{startTime} AND #{endTime} ORDER BY timestamp DESC")
    List<SensorFall> findByTimeRange(Long startTime, Long endTime);
}