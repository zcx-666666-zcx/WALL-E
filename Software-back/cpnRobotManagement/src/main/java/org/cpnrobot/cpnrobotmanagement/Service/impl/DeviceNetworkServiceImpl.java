package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Mapper.DeviceNetworkStatusMapper;
import org.cpnrobot.cpnrobotmanagement.Service.DeviceNetworkService;
import org.cpnrobot.cpnrobotmanagement.Service.userService;
import org.cpnrobot.cpnrobotmanagement.dto.DeviceHeartbeatRequest;
import org.cpnrobot.cpnrobotmanagement.socket.DeviceIdentity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import pojos.ContractMachine;
import pojos.DeviceNetworkStatus;
import pojos.User;

import java.time.LocalDateTime;

@Service
public class DeviceNetworkServiceImpl implements DeviceNetworkService {

    @Autowired
    private DeviceNetworkStatusMapper statusMapper;

    @Autowired
    private ContractMachineMapper contractMachineMapper;

    @Autowired
    private userService userservice;

    @Value("${walle.device-api-user:test}")
    private String deviceApiUser = "test";

    @Value("${walle.device-online-timeout-seconds:120}")
    private long onlineTimeoutSeconds = 120L;

    @Override
    public DeviceNetworkStatus recordHeartbeat(
            String deviceId, DeviceHeartbeatRequest request, String observedIp) {
        String canonicalDeviceId = DeviceIdentity.canonicalize(deviceId);
        User owner = userservice.getId(deviceApiUser);
        if (owner == null || owner.getId() == null) {
            throw new IllegalStateException("设备所属用户不存在");
        }
        String userId = String.valueOf(owner.getId());
        DeviceNetworkStatus heartbeat = new DeviceNetworkStatus();
        heartbeat.setDeviceId(canonicalDeviceId);
        heartbeat.setUserId(userId);
        heartbeat.setLanIp(normalize(request == null ? null : request.getLanIp(), 45));
        heartbeat.setObservedIp(normalize(observedIp, 45));
        heartbeat.setNetworkName(normalize(request == null ? null : request.getNetworkName(), 128));
        heartbeat.setLastSeenAt(LocalDateTime.now());
        statusMapper.upsert(heartbeat);

        if (heartbeat.getLanIp() != null) {
            int updated = contractMachineMapper.updateRobotIpByUserAndConnectionId(
                    userId, canonicalDeviceId, heartbeat.getLanIp());
            if (updated == 0 && DeviceIdentity.STANDARD_DEVICE_ID.equals(canonicalDeviceId)) {
                contractMachineMapper.updateRobotIpByUserAndConnectionId(
                        userId, DeviceIdentity.LEGACY_DEVICE_ID, heartbeat.getLanIp());
            }
        }

        DeviceNetworkStatus stored = statusMapper.findByDeviceIdAndUserId(canonicalDeviceId, userId);
        return applyOnlineState(stored == null ? heartbeat : stored);
    }

    @Override
    public DeviceNetworkStatus getStatusForUser(String deviceId, Integer userId) {
        if (userId == null) {
            return null;
        }
        String canonicalDeviceId = DeviceIdentity.canonicalize(deviceId);
        return applyOnlineState(statusMapper.findByDeviceIdAndUserId(
                canonicalDeviceId, String.valueOf(userId)));
    }

    private DeviceNetworkStatus applyOnlineState(DeviceNetworkStatus status) {
        if (status == null) {
            return null;
        }
        LocalDateTime cutoff = LocalDateTime.now().minusSeconds(onlineTimeoutSeconds);
        status.setOnline(status.getLastSeenAt() != null && !status.getLastSeenAt().isBefore(cutoff));
        return status;
    }

    private String normalize(String value, int maxLength) {
        if (value == null || value.isBlank()) {
            return null;
        }
        String normalized = value.trim();
        return normalized.length() <= maxLength ? normalized : normalized.substring(0, maxLength);
    }
}
