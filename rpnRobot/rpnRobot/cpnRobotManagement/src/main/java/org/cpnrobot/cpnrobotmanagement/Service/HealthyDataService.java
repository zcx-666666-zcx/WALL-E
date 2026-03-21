package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.*;

public interface HealthyDataService {
    ListResult<SensorRate> getRate(String deviceId);

    ListResult<SensorHumidity> getHumidity(String deviceId);

    ListResult<SensorBreathe> getBreathe(String deviceId);

    ListResult<SensorTemperature> getTemperature(String deviceId);

    SensorFall getFall(String deviceId);
}
