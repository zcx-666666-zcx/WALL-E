package org.cpnrobot.cpnrobotmanagement.Service.impl;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.cpnrobot.cpnrobotmanagement.Mapper.*;
import org.cpnrobot.cpnrobotmanagement.Service.SensorDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pojos.*;

import java.io.IOException;
import java.util.List;

/**
 * 传感器数据服务实现类
 */
@Service
public class SensorDataServiceImpl implements SensorDataService {

    @Autowired
    private SensorFallMapper sensorFallMapper;
    
    @Autowired
    private SensorTemperatureMapper sensorTemperatureMapper;
    
    @Autowired
    private SensorHumidityMapper sensorHumidityMapper;
    
    @Autowired
    private SensorRateMapper sensorRateMapper;
    
    @Autowired
    private SensorBreatheMapper sensorBreatheMapper;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public void save(SensorData sensorData) {
        System.out.println("[传感器数据][保存] 开始保存传感器数据");
        System.out.println("[传感器数据][保存] 数据详情: " +
                "id=" + sensorData.getId() +
                ", fall=" + sensorData.getFall() +
                ", temperature=" + sensorData.getTemperature() +
                ", humidity=" + sensorData.getHumidity() +
                ", rate=" + sensorData.getRate() +
                ", breathe=" + sensorData.getBreathe() +
                ", deviceId=" + sensorData.getDeviceId() +
                ", timestamp=" + sensorData.getTimestamp());

        // 这里可以根据需要决定是否还需要保存到旧表
        // sensorDataMapper.insert(sensorData);

        System.out.println("[传感器数据][保存] 传感器数据保存完成");
    }

    @Override
    public List<SensorData> findByDeviceId(String deviceId) {
        // 可以根据需要实现合并查询逻辑
        return null;
    }

    @Override
    public SensorData findLatest() {
        // 可以根据需要实现合并查询逻辑
        return null;
    }

    @Override
    public List<SensorData> findByTimeRange(Long startTime, Long endTime) {
        // 可以根据需要实现合并查询逻辑
        return null;
    }

    @Override
    @Transactional
    public void parseAndSaveFromOneNetMessage(String msg, Long timestamp, String messageId) {
        try {
            System.out.println("[传感器数据][解析] 开始解析OneNET消息: " + msg);

            JsonNode rootNode = objectMapper.readTree(msg);
            
            // 提取设备相关信息
            String devName = rootNode.path("dev_name").asText();
            String pid = rootNode.path("pid").asText();
            String dsId = rootNode.path("ds_id").asText();
            String valueStr = rootNode.path("value").asText();
            
            System.out.println("[传感器数据][解析] 解析到的数据: dev_name=" + devName + ", pid=" + pid + ", ds_id=" + dsId + ", value=" + valueStr);
            
            // 根据ds_id判断数据类型并保存到对应表
            switch (dsId.toLowerCase()) {
                case "fall": // 跌倒传感器
                    try {
                        boolean fallValue = Boolean.parseBoolean(valueStr);
                        SensorFall fallData = new SensorFall();
                        fallData.setDeviceId(pid);
                        fallData.setFall(fallValue);
                        fallData.setTimestamp(timestamp);
                        fallData.setMessageId(messageId);
                        sensorFallMapper.insert(fallData);
                        System.out.println("[传感器数据][解析] 跌倒数据保存完成: " + fallValue);
                    } catch (Exception e) {
                        System.err.println("[传感器数据][解析] 插入sensor_fall表失败: " + e.getMessage());
                    }
                    break;
                    
                case "temperature": // 温度传感器
                    try {
                        double tempValue = Double.parseDouble(valueStr);
                        SensorTemperature tempData = new SensorTemperature();
                        tempData.setDeviceId(pid);
                        tempData.setTemperature(tempValue);
                        tempData.setTimestamp(timestamp);
                        tempData.setMessageId(messageId);
                        sensorTemperatureMapper.insert(tempData);
                        System.out.println("[传感器数据][解析] 温度数据保存完成: " + tempValue);
                    } catch (Exception e) {
                        System.err.println("[传感器数据][解析] 插入sensor_temperature表失败: " + e.getMessage());
                    }
                    break;
                    
                case "humidity": // 湿度传感器
                    try {
                        double humidityValue = Double.parseDouble(valueStr);
                        SensorHumidity humidityData = new SensorHumidity();
                        humidityData.setDeviceId(pid);
                        humidityData.setHumidity(humidityValue);
                        humidityData.setTimestamp(timestamp);
                        humidityData.setMessageId(messageId);
                        sensorHumidityMapper.insert(humidityData);
                        System.out.println("[传感器数据][解析] 湿度数据保存完成: " + humidityValue);
                    } catch (Exception e) {
                        System.err.println("[传感器数据][解析] 插入sensor_humidity表失败: " + e.getMessage());
                    }
                    break;
                    
                case "rate": // 心率传感器
                    try {
                        int rateValue = Integer.parseInt(valueStr);
                        SensorRate rateData = new SensorRate();
                        rateData.setDeviceId(pid);
                        rateData.setRate(rateValue);
                        rateData.setTimestamp(timestamp);
                        rateData.setMessageId(messageId);
                        sensorRateMapper.insert(rateData);
                        System.out.println("[传感器数据][解析] 心率数据保存完成: " + rateValue);
                    } catch (Exception e) {
                        System.err.println("[传感器数据][解析] 插入sensor_rate表失败: " + e.getMessage());
                    }
                    break;
                    
                case "breathe": // 呼吸频率传感器
                    try {
                        int breatheValue = Integer.parseInt(valueStr);
                        SensorBreathe breatheData = new SensorBreathe();
                        breatheData.setDeviceId(pid);
                        breatheData.setBreathe(breatheValue);
                        breatheData.setTimestamp(timestamp);
                        breatheData.setMessageId(messageId);
                        sensorBreatheMapper.insert(breatheData);
                        System.out.println("[传感器数据][解析] 呼吸频率数据保存完成: " + breatheValue);
                    } catch (Exception e) {
                        System.err.println("[传感器数据][解析] 插入sensor_breathe表失败: " + e.getMessage());
                    }
                    break;
                    
                case "online_status": // 设备在线状态
                    // 静默丢弃，不做处理
                    System.out.println("[传感器数据][解析] 收到设备在线状态信息，已静默丢弃: " + valueStr);
                    break;
                    
                default:
                    System.out.println("[传感器数据][解析] 未知的传感器类型: " + dsId + "，已静默丢弃");
                    break;
            }
            
        } catch (Exception e) {
            System.out.println("[传感器数据][解析] 解析OneNET消息失败: " + e.getMessage());
            e.printStackTrace();
        }
    }
}