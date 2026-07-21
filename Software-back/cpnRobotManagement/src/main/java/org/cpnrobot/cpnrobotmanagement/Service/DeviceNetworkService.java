package org.cpnrobot.cpnrobotmanagement.Service;

import org.cpnrobot.cpnrobotmanagement.dto.DeviceHeartbeatRequest;
import pojos.DeviceNetworkStatus;

public interface DeviceNetworkService {
    DeviceNetworkStatus recordHeartbeat(
            String deviceId, DeviceHeartbeatRequest request, String observedIp);

    DeviceNetworkStatus getStatusForUser(String deviceId, Integer userId);
}
