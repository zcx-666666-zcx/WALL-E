package org.cpnrobot.cpnrobotmanagement.Controller;

import jakarta.servlet.http.HttpServletRequest;
import org.cpnrobot.cpnrobotmanagement.Service.DeviceNetworkService;
import org.cpnrobot.cpnrobotmanagement.dto.DeviceHeartbeatRequest;
import org.cpnrobot.cpnrobotmanagement.socket.DeviceIdentity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import pojos.DeviceNetworkStatus;
import pojos.Result;
import util.CurrentHolder;

@RestController
@RequestMapping("/api/device/network")
public class DeviceNetworkController {

    @Autowired
    private DeviceNetworkService deviceNetworkService;

    @Value("${walle.device-api-id:WALLE_1}")
    private String deviceApiId = DeviceIdentity.STANDARD_DEVICE_ID;

    @PostMapping("/heartbeat/{deviceId}")
    public ResponseEntity<Result> heartbeat(
            @PathVariable String deviceId,
            @RequestBody DeviceHeartbeatRequest body,
            HttpServletRequest request) {
        String canonicalDeviceId = DeviceIdentity.canonicalize(deviceId);
        if (!canonicalDeviceId.equals(DeviceIdentity.canonicalize(deviceApiId))) {
            return ResponseEntity.notFound().build();
        }
        DeviceNetworkStatus status = deviceNetworkService.recordHeartbeat(
                canonicalDeviceId, body, request.getRemoteAddr());
        return ResponseEntity.ok(Result.success(status));
    }

    @GetMapping("/status/{deviceId}")
    public Result status(@PathVariable String deviceId) {
        Integer currentUserId = CurrentHolder.getCurrentId();
        if (currentUserId == null) {
            return Result.error("未登录或 token 无效");
        }
        DeviceNetworkStatus status = deviceNetworkService.getStatusForUser(
                DeviceIdentity.canonicalize(deviceId), currentUserId);
        return status == null ? Result.error("设备不存在或暂无网络状态") : Result.success(status);
    }
}
