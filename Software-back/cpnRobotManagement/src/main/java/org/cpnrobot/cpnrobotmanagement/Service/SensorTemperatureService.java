package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.SensorTemperature;

import java.util.List;

/**
 * 温度传感器数据服务接口
 */
public interface SensorTemperatureService {
    
    /**
     * 保存温度传感器数据
     */
    void save(SensorTemperature sensorTemperature);
    
    /**
     * 根据设备ID查询温度数据
     */
    List<SensorTemperature> findByDeviceId(String deviceId);
    
    /**
     * 获取最新温度数据
     */
    SensorTemperature findLatest();
    
    /**
     * 根据时间范围查询温度数据
     */
    List<SensorTemperature> findByTimeRange(Long startTime, Long endTime);
}