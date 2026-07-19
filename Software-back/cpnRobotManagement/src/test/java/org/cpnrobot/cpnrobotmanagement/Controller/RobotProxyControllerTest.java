package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.socket.SignalingHandler;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import pojos.Result;
import pojos.ContractMachine;
import util.CurrentHolder;

import org.springframework.http.ResponseEntity;

import java.nio.charset.StandardCharsets;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class RobotProxyControllerTest {

    @Mock
    private ContractMachineMapper contractMachineMapper;

    private RobotProxyController controller;

    @BeforeEach
    void setUp() {
        controller = new RobotProxyController();
        ReflectionTestUtils.setField(controller, "contractMachineMapper", contractMachineMapper);
        ReflectionTestUtils.setField(controller, "cameraFrameMaxAgeMs", 3000L);
    }

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
        SignalingHandler.CAMERA_FRAMES.clear();
        SignalingHandler.CAMERA_FRAME_TIMES.clear();
    }

    @Test
    void motorRejectsMachineNotOwnedByCurrentUser() {
        CurrentHolder.setCurrentId(7);
        when(contractMachineMapper.getByIdAndUserId(99, "7")).thenReturn(null);

        Result result = controller.motor(Map.of("machineId", 99, "stickX", 0.1, "stickY", 0.2));

        assertThat(result.getCode()).isEqualTo(0);
        assertThat(result.getMsg()).contains("不属于当前用户");
    }

    @Test
    void cameraFrameUsesCanonicalConnectionIdInsteadOfDisplayName() {
        CurrentHolder.setCurrentId(7);
        ContractMachine machine = new ContractMachine();
        machine.setId(2);
        machine.setMachines("瓦力");
        machine.setConnectionId("WALLE_1");
        when(contractMachineMapper.getByIdAndUserId(2, "7")).thenReturn(machine);
        byte[] jpeg = "jpeg-data".getBytes(StandardCharsets.US_ASCII);
        SignalingHandler.CAMERA_FRAMES.put("WALLE_1", jpeg);
        SignalingHandler.CAMERA_FRAME_TIMES.put("WALLE_1", System.currentTimeMillis());

        ResponseEntity<byte[]> response = controller.cameraFrame(2);

        assertThat(response.getStatusCode().value()).isEqualTo(200);
        assertThat(response.getBody()).isEqualTo(jpeg);
    }

    @Test
    void cameraFrameRejectsStaleCache() {
        CurrentHolder.setCurrentId(7);
        ContractMachine machine = new ContractMachine();
        machine.setId(2);
        machine.setConnectionId("WALLE_1");
        when(contractMachineMapper.getByIdAndUserId(2, "7")).thenReturn(machine);
        SignalingHandler.CAMERA_FRAMES.put("WALLE_1", new byte[]{1, 2, 3});
        SignalingHandler.CAMERA_FRAME_TIMES.put("WALLE_1", System.currentTimeMillis() - 5000L);

        ResponseEntity<byte[]> response = controller.cameraFrame(2);

        assertThat(response.getStatusCode().value()).isEqualTo(204);
    }

    @Test
    void commandRoomCanonicalizesLegacyDeviceId() {
        ContractMachine machine = new ContractMachine();
        machine.setConnectionId("WALEE_1");

        String room = ReflectionTestUtils.invokeMethod(controller, "getRoom", machine);

        assertThat(room).isEqualTo("robot_WALLE_1");
    }
}
