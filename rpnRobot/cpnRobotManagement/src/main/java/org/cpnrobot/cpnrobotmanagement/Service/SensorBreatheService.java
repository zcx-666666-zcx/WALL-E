package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.SensorBreathe;

import java.util.List;

/**
 * 呼吸频率传感器数据服务接口
 */
public interface SensorBreatheService {
    
    /**
     * 保存呼吸频率传感器数据
     */
    void save(SensorBreathe sensorBreathe);
    
    /**
     * 根据设备ID查询呼吸频率数据
     */
    List<SensorBreathe> findByDeviceId(String deviceId);
    
    /**
     * 获取最新呼吸频率数据
     */
    SensorBreathe findLatest();
    
    /**
     * 根据时间范围查询呼吸频率数据
     */
    List<SensorBreathe> findByTimeRange(Long startTime, Long endTime);
}