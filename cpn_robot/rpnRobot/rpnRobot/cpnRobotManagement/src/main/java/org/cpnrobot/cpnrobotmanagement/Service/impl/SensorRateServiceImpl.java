package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.SensorRateMapper;
import org.cpnrobot.cpnrobotmanagement.Service.SensorRateService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.SensorRate;

import java.util.List;

/**
 * 心率传感器数据服务实现类
 */
@Service
public class SensorRateServiceImpl implements SensorRateService {
    
    @Autowired
    private SensorRateMapper sensorRateMapper;
    
    @Override
    public void save(SensorRate sensorRate) {
        sensorRateMapper.insert(sensorRate);
    }
    
    @Override
    public List<SensorRate> findByDeviceId(String deviceId) {
        return sensorRateMapper.findByDeviceId(deviceId);
    }
    
    @Override
    public SensorRate findLatest() {
        return sensorRateMapper.findLatest();
    }
    
    @Override
    public List<SensorRate> findByTimeRange(Long startTime, Long endTime) {
        return sensorRateMapper.findByTimeRange(startTime, endTime);
    }
}