package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.SensorData;

import java.util.List;

/**
 * 传感器数据持久化Mapper
 */
@Mapper
public interface SensorDataMapper {

    /**
     * 插入传感器数据
     */
    @Insert("INSERT INTO sensor_data(id, fall, temperature, humidity, rate, breathe, device_id, timestamp) " +
            "VALUES(#{id}, #{fall}, #{temperature}, #{humidity}, #{rate}, #{breathe}, #{deviceId}, #{timestamp})")
    int insert(SensorData sensorData);

    /**
     * 根据设备ID查询传感器数据
     */
    @Select("SELECT * FROM sensor_data WHERE device_id = #{deviceId} ORDER BY timestamp DESC")
    List<SensorData> findByDeviceId(String deviceId);

    /**
     * 查询最新的传感器数据
     */
    @Select("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
    SensorData findLatest();

    /**
     * 根据时间范围查询传感器数据
     */
    @Select("SELECT * FROM sensor_data WHERE timestamp BETWEEN #{startTime} AND #{endTime} ORDER BY timestamp DESC")
    List<SensorData> findByTimeRange(Long startTime, Long endTime);
}