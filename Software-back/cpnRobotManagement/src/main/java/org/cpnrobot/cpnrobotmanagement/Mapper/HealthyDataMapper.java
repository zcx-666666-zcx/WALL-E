package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.*;
import pojos.*;

import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface HealthyDataMapper {

    @Select("SELECT * FROM sensor_fall " +
            "ORDER BY created_at DESC " +
            "LIMIT 1")
    SensorFall getFall(String deviceId);

    @Select("SELECT * FROM sensor_rate " +
            "WHERE device_id = #{deviceId}" +
            "AND DATE(created_at) = DATE(#{time}) " +
            "ORDER BY timestamp ASC")

    List<SensorRate> getRate(@Param("deviceId") String deviceId, @Param("time") LocalDateTime time);

    @Select("SELECT * FROM sensor_humidity " +
            "WHERE device_id = #{deviceId} " +
            "AND DATE(created_at) = DATE(#{time}) " +
            "ORDER BY timestamp ASC")
    List<SensorHumidity> getHumidity(String deviceId, LocalDateTime time);

    @Select("SELECT * FROM sensor_breathe " +
            "WHERE device_id = #{deviceId} " +
            "AND DATE(created_at) = DATE(#{time}) " +
            "ORDER BY timestamp ASC")
    List<SensorBreathe> getBreathe(String deviceId, LocalDateTime time);

    @Select("SELECT * FROM sensor_temperature " +
            "WHERE device_id = #{deviceId} " +
            "AND DATE(created_at) = DATE(#{time}) " +
            "ORDER BY timestamp ASC")
    List<SensorTemperature> getTemperature(String deviceId, LocalDateTime time);
}

//本来是想只查询当天的记录。由于开发测试需求给砍掉了。每个select语句后面加上
//+
//            "AND DATE(created_at) = DATE(#{time}) " +
//            "ORDER BY timestamp ASC")
//即可