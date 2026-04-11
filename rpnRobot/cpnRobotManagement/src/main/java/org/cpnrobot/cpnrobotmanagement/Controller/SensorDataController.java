package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 传感器数据控制器
 * 提供各类传感器数据的查询接口
 */
@RestController
@RequestMapping("/sensor")
@CrossOrigin(origins = "http://localhost:5173")
public class SensorDataController {
    
    @Autowired
    private SensorFallService sensorFallService;
    
    @Autowired
    private SensorTemperatureService sensorTemperatureService;
    
    @Autowired
    private SensorHumidityService sensorHumidityService;
    
    @Autowired
    private SensorRateService sensorRateService;
    
    @Autowired
    private SensorBreatheService sensorBreatheService;
    
    /**
     * 获取所有传感器的最新数据
     */
    @GetMapping("/latest")
    public Result getLatestSensorData() {
        Map<String, Object> result = new HashMap<>();
        
        try {
            result.put("fall", sensorFallService.findLatest());
            result.put("temperature", sensorTemperatureService.findLatest());
            result.put("humidity", sensorHumidityService.findLatest());
            result.put("rate", sensorRateService.findLatest());
            result.put("breathe", sensorBreatheService.findLatest());
            
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("获取传感器数据失败: " + e.getMessage());
        }
    }
    
    /**
     * 根据设备ID获取传感器历史数据
     */
    @GetMapping("/history/{deviceId}")
    public Result getSensorHistoryByDevice(
            @PathVariable("deviceId") String deviceId,
            @RequestParam(required = false) Long startTime,
            @RequestParam(required = false) Long endTime) {
        
        Map<String, Object> result = new HashMap<>();
        
        try {
            if (startTime != null && endTime != null) {
                result.put("fall", sensorFallService.findByTimeRange(startTime, endTime));
                result.put("temperature", sensorTemperatureService.findByTimeRange(startTime, endTime));
                result.put("humidity", sensorHumidityService.findByTimeRange(startTime, endTime));
                result.put("rate", sensorRateService.findByTimeRange(startTime, endTime));
                result.put("breathe", sensorBreatheService.findByTimeRange(startTime, endTime));
            } else {
                result.put("fall", sensorFallService.findByDeviceId(deviceId));
                result.put("temperature", sensorTemperatureService.findByDeviceId(deviceId));
                result.put("humidity", sensorHumidityService.findByDeviceId(deviceId));
                result.put("rate", sensorRateService.findByDeviceId(deviceId));
                result.put("breathe", sensorBreatheService.findByDeviceId(deviceId));
            }
            
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("获取传感器历史数据失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取特定传感器的最新数据
     */
    @GetMapping("/{sensorType}/latest")
    public Result getLatestBySensorType(@PathVariable("sensorType") String sensorType) {
        try {
            switch (sensorType.toLowerCase()) {
                case "fall":
                    return Result.success(sensorFallService.findLatest());
                case "temperature":
                    return Result.success(sensorTemperatureService.findLatest());
                case "humidity":
                    return Result.success(sensorHumidityService.findLatest());
                case "rate":
                    return Result.success(sensorRateService.findLatest());
                case "breathe":
                    return Result.success(sensorBreatheService.findLatest());
                default:
                    return Result.error("不支持的传感器类型: " + sensorType);
            }
        } catch (Exception e) {
            return Result.error("获取传感器数据失败: " + e.getMessage());
        }
    }
}