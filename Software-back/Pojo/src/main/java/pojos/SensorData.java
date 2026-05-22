package pojos;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * 传感器数据实体类
 * 用于存储从OneNET设备上传的传感器数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SensorData {
    private Long id;           // 时间戳作为唯一ID
    private Boolean fall;      // 跌倒状态（布尔类型）
    private Double temperature; // 温度（double类型）
    private Double humidity;   // 湿度（double类型）
    private Integer rate;      // 心率（整型）
    private Integer breathe;   // 呼吸频率（整型）
    private String deviceId;   // 设备ID
    private Long timestamp;    // 数据时间戳
}