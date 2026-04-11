package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.SensorData;

import java.util.List;

/**
 * 传感器数据服务接口
 */
public interface SensorDataService {

    /**
     * 保存传感器数据
     */
    void save(SensorData sensorData);

    /**
     * 根据设备ID查询传感器数据
     */
    List<SensorData> findByDeviceId(String deviceId);

    /**
     * 获取最新传感器数据
     */
    SensorData findLatest();

    /**
     * 根据时间范围查询传感器数据
     */
    List<SensorData> findByTimeRange(Long startTime, Long endTime);

    /**
     * 从OneNET消息中解析并保存传感器数据
     */
    void parseAndSaveFromOneNetMessage(String msg, Long timestamp, String messageId);
}