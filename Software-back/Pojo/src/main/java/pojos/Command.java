package pojos;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Command {
    private Long id;           // 主键ID
    private String deviceId;   // 设备ID
    private String type;       // 命令类型"go","back","left"...
    private Long timestamp;    // 数据时间戳
    private String messageId;  // OneNET消息ID
    private LocalDateTime createdAt;
}
