package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.SensorFall;

import java.util.List;

/**
 * 跌倒传感器数据服务接口
 */
public interface SensorFallService {
    
    /**
     * 保存跌倒传感器数据
     */
    void save(SensorFall sensorFall);
    
    /**
     * 根据设备ID查询跌倒数据
     */
    List<SensorFall> findByDeviceId(String deviceId);
    
    /**
     * 获取最新跌倒数据
     */
    SensorFall findLatest();
    
    /**
     * 根据时间范围查询跌倒数据
     */
    List<SensorFall> findByTimeRange(Long startTime, Long endTime);
}