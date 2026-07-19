package org.cpnrobot.cpnrobotmanagement.socket;

import com.corundumstudio.socketio.AckRequest;
import com.corundumstudio.socketio.SocketIOClient;
import com.corundumstudio.socketio.SocketIOServer;
import com.corundumstudio.socketio.annotation.OnConnect;
import com.corundumstudio.socketio.annotation.OnDisconnect;
import com.corundumstudio.socketio.annotation.OnEvent;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.util.Map;
import java.util.Set;
import java.util.Base64;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArraySet;

@Component
public class SignalingHandler {

    @Autowired
    private SocketIOServer server;

    // 账本：RoomID -> Set of SessionIDs (等同于 Python 的 MY_ROOMS)
    private static final Map<String, Set<SocketIOClient>> MY_ROOMS = new ConcurrentHashMap<>();

    // 摄像头帧缓存：deviceName -> { jpegBytes, timestamp }
    public static final Map<String, byte[]> CAMERA_FRAMES = new ConcurrentHashMap<>();
    public static final Map<String, Long> CAMERA_FRAME_TIMES = new ConcurrentHashMap<>();

    @org.springframework.beans.factory.annotation.Value("${walle.device-api-token:}")
    private String deviceApiToken = "";

    @org.springframework.beans.factory.annotation.Value("${walle.device-api-id:WALLE_1}")
    private String cameraDeviceId = DeviceIdentity.STANDARD_DEVICE_ID;

    @org.springframework.beans.factory.annotation.Value("${walle.camera-frame-max-base64-bytes:524288}")
    private int cameraFrameMaxBase64Bytes = 524288;

    @PostConstruct
    public void start() {
        server.addListeners(this);
        server.start(); // 随 Spring Boot 启动
        System.out.println("✅ [信令服务器] v4.0 Java集成版已启动，监听端口: 8081");
    }

    @PreDestroy
    public void stop() {
        server.stop();
    }

    @OnConnect
    public void onConnect(SocketIOClient client) {
        System.out.println("✅ [连接] 新用户: " + client.getSessionId());
    }

    @OnDisconnect
    public void onDisconnect(SocketIOClient client) {
        System.out.println("❌ [断开] 用户离开: " + client.getSessionId());
        // 扫一遍账本划掉用户
        MY_ROOMS.forEach((room, clients) -> {
            if (clients.contains(client)) {
                clients.remove(client);
                if (clients.isEmpty()) {
                    MY_ROOMS.remove(room);
                }
            }
        });
    }

    @OnEvent("join")
    public void onJoin(SocketIOClient client, Map<String, Object> data ){
        System.out.println("DEBUG: 收到 join 事件了！数据内容: " + data);

        if (data == null || data.get("room") == null) {
            System.out.println("⚠️ 收到 join 事件，但房间号是空的");
            return;
        }

        String room = DeviceIdentity.canonicalizeRoom(String.valueOf(data.get("room")));

        // 1. 加入 netty-socketio 内部房间（供 server.getRoomOperations() 使用）
        client.joinRoom(room);

        // 2. 手动记账
        MY_ROOMS.computeIfAbsent(room, k -> new CopyOnWriteArraySet<>()).add(client);

        System.out.println("📥 [加入] 用户 " + client.getSessionId() + " -> 房间 " + room);

        // 2. 告诉自己加入成功
        client.sendEvent("joined", Map.of("room", room, "id", client.getSessionId().toString()));

        // 3. 手动广播给其他人
        for (SocketIOClient member : MY_ROOMS.get(room)) {
            if (!member.getSessionId().equals(client.getSessionId())) {
                member.sendEvent("message", Map.of("type", "system", "msg", "用户进来了"));
            }
        }
    }

    @OnEvent("message")
    public void onMessage(SocketIOClient client, Map<String, Object> data) {
        String room = DeviceIdentity.canonicalizeRoom(String.valueOf(data.get("room")));
        Object payload = data.get("payload");

        if (MY_ROOMS.containsKey(room)) {
            for (SocketIOClient member : MY_ROOMS.get(room)) {
                // 转发消息给除自己以外的人
                if (!member.getSessionId().equals(client.getSessionId())) {
                    member.sendEvent("message", payload);
                }
            }
        }
    }

    @OnEvent("camera_frame")
    public void onCameraFrame(SocketIOClient client, Map<String, Object> data) {
        if (data == null || !data.containsKey("deviceName") || !data.containsKey("image")
                || !tokensMatch(deviceApiToken, String.valueOf(data.get("deviceToken")))) {
            return;
        }
        try {
            String deviceName = DeviceIdentity.canonicalize(String.valueOf(data.get("deviceName")));
            if (!deviceName.equals(DeviceIdentity.canonicalize(cameraDeviceId))) {
                return;
            }
            String imageBase64 = String.valueOf(data.get("image"));
            if (imageBase64.length() > cameraFrameMaxBase64Bytes) {
                return;
            }
            byte[] jpeg = Base64.getDecoder().decode(imageBase64);
            CAMERA_FRAMES.put(deviceName, jpeg);
            CAMERA_FRAME_TIMES.put(deviceName, System.currentTimeMillis());
        } catch (Exception ignored) {
            // base64 解码失败，丢弃这一帧
        }
    }

    private boolean tokensMatch(String expected, String provided) {
        if (expected == null || expected.isBlank() || provided == null || provided.isBlank()) {
            return false;
        }
        return MessageDigest.isEqual(
                expected.getBytes(StandardCharsets.UTF_8),
                provided.getBytes(StandardCharsets.UTF_8));
    }
}
