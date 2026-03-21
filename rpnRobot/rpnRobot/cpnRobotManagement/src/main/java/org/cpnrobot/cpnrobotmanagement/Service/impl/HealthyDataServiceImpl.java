package org.cpnrobot.cpnrobotmanagement.Service.impl;

import net.sf.jsqlparser.expression.DateTimeLiteralExpression;
import org.cpnrobot.cpnrobotmanagement.Mapper.HealthyDataMapper;
import org.cpnrobot.cpnrobotmanagement.Service.HealthyDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.*;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class HealthyDataServiceImpl implements HealthyDataService {

    @Autowired
    private HealthyDataMapper healthyDataMapper;

    @Override
    public ListResult<SensorRate> getRate(String deviceId) {
        LocalDateTime time = LocalDateTime.now();
        List<SensorRate> rateList = healthyDataMapper.getRate(deviceId,time);
        return new ListResult<>(rateList);
    }

    @Override
    public ListResult<SensorHumidity> getHumidity(String deviceId) {
        LocalDateTime time = LocalDateTime.now();
        List<SensorHumidity> humidityList = healthyDataMapper.getHumidity(deviceId,time);
        return new ListResult<>(humidityList);
    }

    @Override
    public ListResult<SensorBreathe> getBreathe(String deviceId) {
        LocalDateTime time = LocalDateTime.now();
        List<SensorBreathe> breatheList = healthyDataMapper.getBreathe(deviceId,time);
        return new ListResult<>(breatheList);
    }

    @Override
    public ListResult<SensorTemperature> getTemperature(String deviceId) {
        LocalDateTime time = LocalDateTime.now();
        List<SensorTemperature> temperatureList = healthyDataMapper.getTemperature(deviceId,time);
        return new ListResult<>(temperatureList);
    }

    @Override
    public SensorFall getFall(String deviceId) {
        SensorFall sensorFall = healthyDataMapper.getFall(deviceId);
        return sensorFall;
    }
}
