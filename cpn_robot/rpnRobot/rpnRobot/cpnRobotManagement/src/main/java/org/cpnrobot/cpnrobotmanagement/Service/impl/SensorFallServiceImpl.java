package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.SensorFallMapper;
import org.cpnrobot.cpnrobotmanagement.Service.SensorFallService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.SensorFall;

import java.util.List;

/**
 * 跌倒传感器数据服务实现类
 */
@Service
public class SensorFallServiceImpl implements SensorFallService {
    
    @Autowired
    private SensorFallMapper sensorFallMapper;
    
    @Override
    public void save(SensorFall sensorFall) {
        sensorFallMapper.insert(sensorFall);
    }
    
    @Override
    public List<SensorFall> findByDeviceId(String deviceId) {
        return sensorFallMapper.findByDeviceId(deviceId);
    }
    
    @Override
    public SensorFall findLatest() {
        return sensorFallMapper.findLatest();
    }
    
    @Override
    public List<SensorFall> findByTimeRange(Long startTime, Long endTime) {
        return sensorFallMapper.findByTimeRange(startTime, endTime);
    }
}