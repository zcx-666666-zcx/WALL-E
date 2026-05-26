package pojos;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SystemConfig {
    private Integer id;
    private String configKey;
    private String configValue;
    private String label;
    private String configGroup;
    private Boolean secret;
    private String remark;
    private LocalDateTime updatedAt;
}
