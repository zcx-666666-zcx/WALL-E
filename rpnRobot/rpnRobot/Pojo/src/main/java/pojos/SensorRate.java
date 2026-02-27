package pojos;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * 心率传感器数据实体类
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SensorRate {
    private Long id;           // 主键ID
    private String deviceId;   // 设备ID
    private Integer rate;      // 心率值
    private Long timestamp;    // 数据时间戳
    private String messageId;  // OneNET消息ID
}