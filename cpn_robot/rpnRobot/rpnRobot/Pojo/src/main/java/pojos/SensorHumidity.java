package pojos;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * 湿度传感器数据实体类
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SensorHumidity {
    private Long id;           // 主键ID
    private String deviceId;   // 设备ID
    private Double humidity;   // 湿度值
    private Long timestamp;    // 数据时间戳
    private String messageId;  // OneNET消息ID
}