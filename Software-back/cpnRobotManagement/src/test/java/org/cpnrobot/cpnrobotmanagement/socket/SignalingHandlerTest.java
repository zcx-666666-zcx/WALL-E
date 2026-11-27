package org.cpnrobot.cpnrobotmanagement.socket;

import com.corundumstudio.socketio.SocketIOClient;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.Base64;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import java.util.UUID;
import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import pojos.ContractMachine;
import util.JwtUtils;

class SignalingHandlerTest {

    private SignalingHandler handler;
    private SocketIOClient client;

    @BeforeEach
    void setUp() {
        handler = new SignalingHandler();
        client = mock(SocketIOClient.class);
        ReflectionTestUtils.setField(handler, "deviceApiToken", "device-secret");
        ReflectionTestUtils.setField(handler, "cameraDeviceId", "WALLE_1");
        ReflectionTestUtils.setField(handler, "cameraFrameMaxBase64Bytes", 1024);
    }

    @AfterEach
    void tearDown() {
        SignalingHandler.CAMERA_FRAMES.clear();
        SignalingHandler.CAMERA_FRAME_TIMES.clear();
    }

    @Test
    void cameraFrameRejectsInvalidDeviceToken() {
        handler.onCameraFrame(client, frame("wrong-secret", "WALEE_1", "jpeg"));

        assertThat(SignalingHandler.CAMERA_FRAMES).isEmpty();
    }

    @Test
    void cameraFrameAcceptsConfiguredDeviceAndCanonicalizesItsId() {
        handler.onCameraFrame(client, frame("device-secret", "WALEE_1", "jpeg"));

        assertThat(SignalingHandler.CAMERA_FRAMES.get("WALLE_1")).isEqualTo("jpeg".getBytes());
        assertThat(SignalingHandler.CAMERA_FRAME_TIMES.get("WALLE_1")).isNotNull();
    }

    @Test
    void cameraFrameRejectsOversizedPayload() {
        ReflectionTestUtils.setField(handler, "cameraFrameMaxBase64Bytes", 4);

        handler.onCameraFrame(client, frame("device-secret", "WALLE_1", "jpeg"));

        assertThat(SignalingHandler.CAMERA_FRAMES).isEmpty();
    }

    @Test
    void secureJoinRejectsMissingCredential() {
        assertThat(org.springframework.util.ReflectionUtils.findField(SignalingHandler.class, "requireSignalingAuth")).isNotNull();
        ReflectionTestUtils.setField(handler, "requireSignalingAuth", true);
        handler.onJoin(client, Map.of("room", "robot_WALLE_1"));
        verify(client, never()).joinRoom("robot_WALLE_1");
    }

    @Test
    void secureJoinAcceptsDeviceCredentialForConfiguredDeviceOnly() {
        assertThat(org.springframework.util.ReflectionUtils.findField(SignalingHandler.class, "requireSignalingAuth")).isNotNull();
        ReflectionTestUtils.setField(handler, "requireSignalingAuth", true);
        when(client.getSessionId()).thenReturn(UUID.randomUUID());
        handler.onJoin(client, Map.of("room", "robot_OTHER", "deviceToken", "device-secret"));
        verify(client, never()).joinRoom("robot_OTHER");
        handler.onJoin(client, Map.of("room", "robot_WALLE_1", "deviceToken", "device-secret"));
        verify(client).joinRoom("robot_WALLE_1");
        assertThat(SignalingHandler.isRobotOnline("robot_WALLE_1")).isTrue();
        handler.onDisconnect(client);
        assertThat(SignalingHandler.isRobotOnline("robot_WALLE_1")).isFalse();
    }

    @Test
    void secureJoinRequiresUserToOwnTheDevice() {
        ReflectionTestUtils.setField(handler, "requireSignalingAuth", true);
        ContractMachineMapper mapper = mock(ContractMachineMapper.class);
        ReflectionTestUtils.setField(handler, "contractMachineMapper", mapper);
        when(client.getSessionId()).thenReturn(UUID.randomUUID());
        String token = JwtUtils.createJwt(Map.of("id", 7));
        handler.onJoin(client, Map.of("room", "0001", "token", token));
        verify(client, never()).joinRoom("0001");
        when(mapper.findByUserIdAndConnectionId("7", "WALLE_1")).thenReturn(new ContractMachine());
        handler.onJoin(client, Map.of("room", "0001", "token", token));
        verify(client).joinRoom("0001");
        handler.onDisconnect(client);
    }

    @Test
    void nonMemberCannotSendMessagesIntoRoom() {
        ReflectionTestUtils.setField(handler, "requireSignalingAuth", true);
        SocketIOClient intruder = mock(SocketIOClient.class);
        when(client.getSessionId()).thenReturn(UUID.randomUUID());
        handler.onJoin(client, Map.of("room", "0001", "deviceToken", "device-secret"));
        handler.onMessage(intruder, Map.of("room", "0001", "payload", "injected"));
        verify(client, never()).sendEvent("message", "injected");
        handler.onDisconnect(client);
    }

    private Map<String, Object> frame(String token, String deviceId, String jpeg) {
        return Map.of(
                "deviceToken", token,
                "deviceName", deviceId,
                "image", Base64.getEncoder().encodeToString(jpeg.getBytes()));
    }
}
