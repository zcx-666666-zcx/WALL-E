package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.SensorHumidity;

import java.util.List;

/**
 * 湿度传感器数据服务接口
 */
public interface SensorHumidityService {
    
    /**
     * 保存湿度传感器数据
     */
    void save(SensorHumidity sensorHumidity);
    
    /**
     * 根据设备ID查询湿度数据
     */
    List<SensorHumidity> findByDeviceId(String deviceId);
    
    /**
     * 获取最新湿度数据
     */
    SensorHumidity findLatest();
    
    /**
     * 根据时间范围查询湿度数据
     */
    List<SensorHumidity> findByTimeRange(Long startTime, Long endTime);
}