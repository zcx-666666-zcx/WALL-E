package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.SensorTemperature;

import java.util.List;

/**
 * 温度传感器数据Mapper
 */
@Mapper
public interface SensorTemperatureMapper {
    
    @Insert("INSERT INTO sensor_temperature(device_id, temperature, timestamp, message_id) " +
            "VALUES(#{deviceId}, #{temperature}, #{timestamp}, #{messageId})")
    int insert(SensorTemperature sensorTemperature);
    
    @Select("SELECT * FROM sensor_temperature WHERE device_id = #{deviceId} ORDER BY timestamp DESC")
    List<SensorTemperature> findByDeviceId(String deviceId);
    
    @Select("SELECT * FROM sensor_temperature ORDER BY timestamp DESC LIMIT 1")
    SensorTemperature findLatest();
    
    @Select("SELECT * FROM sensor_temperature WHERE timestamp BETWEEN #{startTime} AND #{endTime} ORDER BY timestamp DESC")
    List<SensorTemperature> findByTimeRange(Long startTime, Long endTime);
}