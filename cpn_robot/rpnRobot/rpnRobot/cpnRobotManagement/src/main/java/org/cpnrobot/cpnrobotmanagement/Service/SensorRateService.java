package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.SensorRate;

import java.util.List;

/**
 * 心率传感器数据服务接口
 */
public interface SensorRateService {
    
    /**
     * 保存心率传感器数据
     */
    void save(SensorRate sensorRate);
    
    /**
     * 根据设备ID查询心率数据
     */
    List<SensorRate> findByDeviceId(String deviceId);
    
    /**
     * 获取最新心率数据
     */
    SensorRate findLatest();
    
    /**
     * 根据时间范围查询心率数据
     */
    List<SensorRate> findByTimeRange(Long startTime, Long endTime);
}