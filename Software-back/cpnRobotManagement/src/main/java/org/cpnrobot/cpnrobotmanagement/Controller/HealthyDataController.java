package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import pojos.*;

@RequestMapping("/api/healthy")
@RestController
@CrossOrigin(origins = "*",maxAge = 3600)
public class HealthyDataController {

    @Autowired
    private HealthyDataService healthyDataService;
    @Autowired
    private SensorTemperatureService sensorTemperatureService;
    @Autowired
    private SensorHumidityService sensorHumidityService;
    @Autowired
    private SensorRateService sensorRateService;
    @Autowired
    private SensorBreatheService sensorBreatheService;
    @Autowired
    private SensorFallService sensorFallService;

    @PostMapping("/addRate")
    public Result addRate(@RequestBody SensorRate sensorRate){
        sensorRateService.save(sensorRate);
        return Result.success();
    }

    @PostMapping("/addHumidity")
    public Result addHumidity(@RequestBody SensorHumidity sensorHumidity){
        sensorHumidityService.save(sensorHumidity);
        return Result.success();
    }

    @PostMapping("/addBreathe")
    public Result addBreathe(@RequestBody SensorBreathe sensorBreathe){
        sensorBreatheService.save(sensorBreathe);
        return Result.success();
    }

    @PostMapping("/addTemperature")
    public Result addTemperatrue(@RequestBody SensorTemperature sensorTemperature){
        sensorTemperatureService.save(sensorTemperature);
        return Result.success();
    }

    @PostMapping("/addFall")
    public Result addFall(@RequestBody SensorFall sensorFall){
        sensorFallService.save(sensorFall);
        return Result.success();
    }

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
