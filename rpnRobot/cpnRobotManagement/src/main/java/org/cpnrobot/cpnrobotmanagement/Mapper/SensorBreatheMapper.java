package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.SensorBreathe;

import java.util.List;

/**
 * 呼吸频率传感器数据Mapper
 */
@Mapper
public interface SensorBreatheMapper {
    
    @Insert("INSERT INTO sensor_breathe(device_id, breathe, timestamp, message_id) " +
            "VALUES(#{deviceId}, #{breathe}, #{timestamp}, #{messageId})")
    int insert(SensorBreathe sensorBreathe);
    
    @Select("SELECT * FROM sensor_breathe WHERE device_id = #{deviceId} ORDER BY timestamp DESC")
    List<SensorBreathe> findByDeviceId(String deviceId);
    
    @Select("SELECT * FROM sensor_breathe ORDER BY timestamp DESC LIMIT 1")
    SensorBreathe findLatest();
    
    @Select("SELECT * FROM sensor_breathe WHERE timestamp BETWEEN #{startTime} AND #{endTime} ORDER BY timestamp DESC")
    List<SensorBreathe> findByTimeRange(Long startTime, Long endTime);
}