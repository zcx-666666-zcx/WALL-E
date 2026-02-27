package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.SensorHumidityMapper;
import org.cpnrobot.cpnrobotmanagement.Service.SensorHumidityService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.SensorHumidity;

import java.util.List;

/**
 * 湿度传感器数据服务实现类
 */
@Service
public class SensorHumidityServiceImpl implements SensorHumidityService {
    
    @Autowired
    private SensorHumidityMapper sensorHumidityMapper;
    
    @Override
    public void save(SensorHumidity sensorHumidity) {
        sensorHumidityMapper.insert(sensorHumidity);
    }
    
    @Override
    public List<SensorHumidity> findByDeviceId(String deviceId) {
        return sensorHumidityMapper.findByDeviceId(deviceId);
    }
    
    @Override
    public SensorHumidity findLatest() {
        return sensorHumidityMapper.findLatest();
    }
    
    @Override
    public List<SensorHumidity> findByTimeRange(Long startTime, Long endTime) {
        return sensorHumidityMapper.findByTimeRange(startTime, endTime);
    }
}