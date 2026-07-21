package pojos;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class DeviceNetworkStatus {
    private Long id;
    private String deviceId;
    private String userId;
    private String lanIp;
    private String observedIp;
    private String networkName;
    private LocalDateTime lastSeenAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private boolean online;
}
