package pojos;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 呼吸频率传感器数据实体类
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SensorBreathe {
    private Long id;           // 主键ID
    private String deviceId;   // 设备ID
    private Integer breathe;   // 呼吸频率值
    private Long timestamp;    // 数据时间戳
    private String messageId;  // OneNET消息ID
    private LocalDateTime createdAt;
}