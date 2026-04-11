package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.SensorRate;

import java.util.List;

/**
 * 心率传感器数据Mapper
 */
@Mapper
public interface SensorRateMapper {
    
    @Insert("INSERT INTO sensor_rate(device_id, rate, timestamp, message_id) " +
            "VALUES(#{deviceId}, #{rate}, #{timestamp}, #{messageId})")
    int insert(SensorRate sensorRate);
    
    @Select("SELECT * FROM sensor_rate WHERE device_id = #{deviceId} ORDER BY timestamp DESC")
    List<SensorRate> findByDeviceId(String deviceId);
    
    @Select("SELECT * FROM sensor_rate ORDER BY timestamp DESC LIMIT 1")
    SensorRate findLatest();
    
    @Select("SELECT * FROM sensor_rate WHERE timestamp BETWEEN #{startTime} AND #{endTime} ORDER BY timestamp DESC")
    List<SensorRate> findByTimeRange(Long startTime, Long endTime);
}