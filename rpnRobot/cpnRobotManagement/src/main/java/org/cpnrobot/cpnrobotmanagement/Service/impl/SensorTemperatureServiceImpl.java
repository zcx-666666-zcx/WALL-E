package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.SensorTemperatureMapper;
import org.cpnrobot.cpnrobotmanagement.Service.SensorTemperatureService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.SensorTemperature;

import java.util.List;

/**
 * 温度传感器数据服务实现类
 */
@Service
public class SensorTemperatureServiceImpl implements SensorTemperatureService {
    
    @Autowired
    private SensorTemperatureMapper sensorTemperatureMapper;
    
    @Override
    public void save(SensorTemperature sensorTemperature) {
        sensorTemperatureMapper.insert(sensorTemperature);
    }
    
    @Override
    public List<SensorTemperature> findByDeviceId(String deviceId) {
        return sensorTemperatureMapper.findByDeviceId(deviceId);
    }
    
    @Override
    public SensorTemperature findLatest() {
        return sensorTemperatureMapper.findLatest();
    }
    
    @Override
    public List<SensorTemperature> findByTimeRange(Long startTime, Long endTime) {
        return sensorTemperatureMapper.findByTimeRange(startTime, endTime);
    }
}