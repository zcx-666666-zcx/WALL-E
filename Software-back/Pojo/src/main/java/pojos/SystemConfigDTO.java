package pojos;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SystemConfigDTO {
    private String apiBaseUrl;
    private String webBaseUrl;
    private String staticBaseUrl;
    private String robotDefaultIp;
    private Integer robotHttpPort;
    private String socketServerUrl;
    private String cozeApiUrl;
    private String cozeWorkflowId;
    private Map<String, Object> publicConfig;
}
