package pojos;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * 温度传感器数据实体类
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SensorTemperature {
    private Long id;           // 主键ID
    private String deviceId;   // 设备ID
    private Double temperature; // 温度值
    private Long timestamp;    // 数据时间戳
    private String messageId;  // OneNET消息ID
}