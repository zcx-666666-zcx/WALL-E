package org.cpnrobot.cpnrobotmanagement.Service.impl;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.cpnrobot.cpnrobotmanagement.Mapper.SensorDataMapper;
import org.cpnrobot.cpnrobotmanagement.Service.SensorDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.SensorData;

import java.io.IOException;
import java.util.List;

/**
 * 传感器数据服务实现类
 */
@Service
public class SensorDataServiceImpl implements SensorDataService {

    @Autowired
    private SensorDataMapper sensorDataMapper;

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

        sensorDataMapper.insert(sensorData);

        System.out.println("[传感器数据][保存] 传感器数据保存完成");
    }

    @Override
    public List<SensorData> findByDeviceId(String deviceId) {
        return sensorDataMapper.findByDeviceId(deviceId);
    }

    @Override
    public SensorData findLatest() {
        return sensorDataMapper.findLatest();
    }

    @Override
    public List<SensorData> findByTimeRange(Long startTime, Long endTime) {
        return sensorDataMapper.findByTimeRange(startTime, endTime);
    }

    @Override
    public void parseAndSaveFromOneNetMessage(String msg, Long timestamp, String messageId) {
        try {
            System.out.println("[传感器数据][解析] 开始解析OneNET消息: " + msg);

            JsonNode rootNode = objectMapper.readTree(msg);
            
            // 提取设备相关信息
            String devName = rootNode.path("dev_name").asText();
            String pid = rootNode.path("pid").asText();
            String dsId = rootNode.path("ds_id").asText();
            
            // 提取传感器数据
            JsonNode dpNode = rootNode.path("dp");
            JsonNode ceshiArray = dpNode.path(dsId);
            
            if (ceshiArray.isArray() && ceshiArray.size() > 0) {
                JsonNode firstDataPoint = ceshiArray.get(0);
                int value = firstDataPoint.path("v").asInt();
                
                // 创建传感器数据对象
                SensorData sensorData = new SensorData();
                sensorData.setId(timestamp); // 使用时间戳作为ID
                sensorData.setDeviceId(pid); // 使用设备PID作为设备ID
                sensorData.setTimestamp(timestamp);
                
                // 根据您的测试数据，value=666，这里需要确定具体映射关系
                // 暂时将value映射到rate字段作为示例
                sensorData.setRate(value);
                // 其他字段暂时设置默认值
                sensorData.setFall(false);
                sensorData.setTemperature(0.0);
                sensorData.setHumidity(0.0);
                sensorData.setBreathe(0);
                
                System.out.println("[传感器数据][解析] 解析完成，准备保存数据");
                save(sensorData);
            } else {
                System.out.println("[传感器数据][解析] 未找到有效的传感器数据");
            }
            
        } catch (IOException e) {
            System.out.println("[传感器数据][解析] 解析OneNET消息失败: " + e.getMessage());
        }
    }
}