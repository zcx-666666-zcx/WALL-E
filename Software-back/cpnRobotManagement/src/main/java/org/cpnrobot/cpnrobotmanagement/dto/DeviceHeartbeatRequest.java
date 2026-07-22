package org.cpnrobot.cpnrobotmanagement.dto;

import lombok.Data;

@Data
public class DeviceHeartbeatRequest {
    private String lanIp;
    private String networkName;
}
