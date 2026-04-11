package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.SensorHumidity;

import java.util.List;

/**
 * 湿度传感器数据Mapper
 */
@Mapper
public interface SensorHumidityMapper {
    
    @Insert("INSERT INTO sensor_humidity(device_id, humidity, timestamp, message_id) " +
            "VALUES(#{deviceId}, #{humidity}, #{timestamp}, #{messageId})")
    int insert(SensorHumidity sensorHumidity);
    
    @Select("SELECT * FROM sensor_humidity WHERE device_id = #{deviceId} ORDER BY timestamp DESC")
    List<SensorHumidity> findByDeviceId(String deviceId);
    
    @Select("SELECT * FROM sensor_humidity ORDER BY timestamp DESC LIMIT 1")
    SensorHumidity findLatest();
    
    @Select("SELECT * FROM sensor_humidity WHERE timestamp BETWEEN #{startTime} AND #{endTime} ORDER BY timestamp DESC")
    List<SensorHumidity> findByTimeRange(Long startTime, Long endTime);
}