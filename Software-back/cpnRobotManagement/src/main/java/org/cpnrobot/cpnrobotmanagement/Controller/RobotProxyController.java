package org.cpnrobot.cpnrobotmanagement.Controller;

import com.corundumstudio.socketio.SocketIOServer;
import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Service.RobotProxyService;
import org.cpnrobot.cpnrobotmanagement.socket.SignalingHandler;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;
import pojos.ContractMachine;
import pojos.Result;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api/robot")
@CrossOrigin(origins = "*", maxAge = 3600)
public class RobotProxyController {

    @Autowired
    private RobotProxyService robotProxyService;

    @Autowired
    private SocketIOServer server;

    @Autowired
    private ContractMachineMapper contractMachineMapper;

    private final Map<Integer, String> roomCache = new ConcurrentHashMap<>();

    private String getRoom(Integer machineId) {
        return roomCache.computeIfAbsent(machineId, id -> {
            ContractMachine machine = contractMachineMapper.getById(id);
            if (machine == null || machine.getMachines() == null || machine.getMachines().isEmpty()) {
                throw new RuntimeException("机器人未找到或设备名未配置，machineId: " + id);
            }
            return "robot_" + machine.getMachines();
        });
    }

    @PostMapping("/motor")
    public Result motor(@RequestBody Map<String, Object> body) {
        try {
            Integer machineId = (Integer) body.get("machineId");
            double stickX = ((Number) body.get("stickX")).doubleValue();
            double stickY = ((Number) body.get("stickY")).doubleValue();

            String room = getRoom(machineId);
            System.out.println("[RobotProxy] 电机指令 -> 房间: " + room + " | X=" + stickX + " Y=" + stickY);
            server.getRoomOperations(room).sendEvent("cmd_motor",
                    Map.of("stickX", String.valueOf(stickX), "stickY", String.valueOf(stickY)));

            return Result.success();
        } catch (Exception e) {
            System.err.println("[RobotProxy] 电机指令失败: " + e.getMessage());
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/servo")
    public Result servo(@RequestBody Map<String, Object> body) {
        try {
            Integer machineId = (Integer) body.get("machineId");
            String servo = (String) body.get("servo");
            Object valObj = body.get("value");
            String value = valObj != null ? String.valueOf(valObj) : "50";

            String room = getRoom(machineId);
            server.getRoomOperations(room).sendEvent("cmd_servo",
                    Map.of("servo", servo, "value", value));

            return Result.success();
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/animate")
    public Result animate(@RequestBody Map<String, Object> body) {
        try {
            Integer machineId = (Integer) body.get("machineId");
            Object clipObj = body.get("clip");
            String clip = clipObj != null ? String.valueOf(clipObj) : "0";

            String room = getRoom(machineId);
            server.getRoomOperations(room).sendEvent("cmd_animate", Map.of("clip", clip));

            return Result.success();
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/settings")
    public Result settings(@RequestBody Map<String, Object> body) {
        try {
            Integer machineId = (Integer) body.get("machineId");
            String type = (String) body.get("type");
            Object valObj = body.get("value");
            String value = valObj != null ? String.valueOf(valObj) : "";

            String room = getRoom(machineId);
            server.getRoomOperations(room).sendEvent("cmd_settings",
                    Map.of("type", type, "value", value));

            return Result.success();
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @GetMapping("/robotIp/{machineId}")
    public Result getRobotIp(@PathVariable Integer machineId) {
        try {
            String ip = robotProxyService.getRobotIp(machineId);
            return Result.success(ip);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @GetMapping("/video-feed/{machineId}")
    public ResponseEntity<StreamingResponseBody> videoFeed(@PathVariable Integer machineId) {
        StreamingResponseBody stream = outputStream -> {
            try {
                robotProxyService.streamVideo(machineId, outputStream);
            } catch (Exception e) {
                // 客户端断开连接等异常，静默处理
            }
        };
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("multipart/x-mixed-replace; boundary=frame"))
                .header("Cache-Control", "no-cache, no-store")
                .header("Connection", "keep-alive")
                .body(stream);
    }

    @GetMapping("/video-feed-low/{machineId}")
    public ResponseEntity<StreamingResponseBody> videoFeedLow(@PathVariable Integer machineId) {
        StreamingResponseBody stream = outputStream -> {
            try {
                robotProxyService.streamVideoLow(machineId, outputStream);
            } catch (Exception e) {
                // 客户端断开连接等异常，静默处理
            }
        };
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("multipart/x-mixed-replace; boundary=frame"))
                .header("Cache-Control", "no-cache, no-store")
                .header("Connection", "keep-alive")
                .body(stream);
    }

    @GetMapping("/camera-frame/{machineId}")
    public ResponseEntity<byte[]> cameraFrame(@PathVariable Integer machineId) {
        try {
            ContractMachine machine = contractMachineMapper.getById(machineId);
            if (machine == null || machine.getMachines() == null) {
                return ResponseEntity.notFound().build();
            }
            String deviceName = machine.getMachines();
            byte[] jpeg = SignalingHandler.CAMERA_FRAMES.get(deviceName);
            if (jpeg == null) {
                return ResponseEntity.noContent().build();
            }
            return ResponseEntity.ok()
                    .contentType(MediaType.IMAGE_JPEG)
                    .header("Cache-Control", "no-cache, no-store, must-revalidate")
                    .header("Pragma", "no-cache")
                    .header("Expires", "0")
                    .body(jpeg);
        } catch (Exception e) {
            return ResponseEntity.noContent().build();
        }
    }
}
