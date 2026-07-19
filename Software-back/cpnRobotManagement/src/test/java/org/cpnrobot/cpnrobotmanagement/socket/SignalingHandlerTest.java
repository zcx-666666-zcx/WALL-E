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

    private Map<String, Object> frame(String token, String deviceId, String jpeg) {
        return Map.of(
                "deviceToken", token,
                "deviceName", deviceId,
                "image", Base64.getEncoder().encodeToString(jpeg.getBytes()));
    }
}
