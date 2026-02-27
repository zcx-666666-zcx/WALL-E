package pojos;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * 跌倒传感器数据实体类
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SensorFall {
    private Long id;           // 主键ID
    private String deviceId;   // 设备ID
    private Boolean fall;      // 跌倒状态
    private Long timestamp;    // 数据时间戳
    private String messageId;  // OneNET消息ID
}