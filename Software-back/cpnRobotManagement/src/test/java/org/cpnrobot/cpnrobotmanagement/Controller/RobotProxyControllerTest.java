package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import pojos.Result;
import util.CurrentHolder;

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
    }

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
    }

    @Test
    void motorRejectsMachineNotOwnedByCurrentUser() {
        CurrentHolder.setCurrentId(7);
        when(contractMachineMapper.getByIdAndUserId(99, "7")).thenReturn(null);

        Result result = controller.motor(Map.of("machineId", 99, "stickX", 0.1, "stickY", 0.2));

        assertThat(result.getCode()).isEqualTo(0);
        assertThat(result.getMsg()).contains("不属于当前用户");
    }
}
