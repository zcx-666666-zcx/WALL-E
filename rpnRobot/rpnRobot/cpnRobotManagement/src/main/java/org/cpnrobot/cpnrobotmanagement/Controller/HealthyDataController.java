package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.HealthyDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import pojos.*;

@RequestMapping("/healthy")
@RestController
@CrossOrigin(origins = "http://localhost:5173")
public class HealthyDataController {

    @Autowired
    private HealthyDataService healthyDataService;

    @GetMapping("/getRate/{deviceId}")
    public Result getRate(@PathVariable("deviceId") String deviceId){
        ListResult<SensorRate> rateList = healthyDataService.getRate(deviceId);
        return Result.success(rateList);
    }

    @GetMapping("/getHumidity/{deviceId}")
    public Result getHumidity(@PathVariable("deviceId") String deviceId){
        ListResult<SensorHumidity> humidityList = healthyDataService.getHumidity(deviceId);
        return Result.success(humidityList);
    }

    @GetMapping("/getBreathe/{deviceId}")
    public Result getBreathe(@PathVariable("deviceId") String deviceId){
        ListResult<SensorBreathe> breatheList = healthyDataService.getBreathe(deviceId);
        return Result.success(breatheList);
    }

    @GetMapping("/getTemperature/{deviceId}")
    public Result getTemperature(@PathVariable("deviceId") String deviceId){
        ListResult<SensorTemperature> temperatureList = healthyDataService.getTemperature(deviceId);
        return Result.success(temperatureList);
    }

    @GetMapping("/getFall/{deviceId}")
    public Result getFall(@PathVariable("deviceId")String deviceId){
        SensorFall sensorFall = healthyDataService.getFall(deviceId);
        return Result.success(sensorFall);
    }

}
