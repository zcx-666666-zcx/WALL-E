package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.SensorBreatheMapper;
import org.cpnrobot.cpnrobotmanagement.Service.SensorBreatheService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.SensorBreathe;

import java.util.List;

/**
 * 呼吸频率传感器数据服务实现类
 */
@Service
public class SensorBreatheServiceImpl implements SensorBreatheService {
    
    @Autowired
    private SensorBreatheMapper sensorBreatheMapper;
    
    @Override
    public void save(SensorBreathe sensorBreathe) {
        sensorBreatheMapper.insert(sensorBreathe);
    }
    
    @Override
    public List<SensorBreathe> findByDeviceId(String deviceId) {
        return sensorBreatheMapper.findByDeviceId(deviceId);
    }
    
    @Override
    public SensorBreathe findLatest() {
        return sensorBreatheMapper.findLatest();
    }
    
    @Override
    public List<SensorBreathe> findByTimeRange(Long startTime, Long endTime) {
        return sensorBreatheMapper.findByTimeRange(startTime, endTime);
    }
}