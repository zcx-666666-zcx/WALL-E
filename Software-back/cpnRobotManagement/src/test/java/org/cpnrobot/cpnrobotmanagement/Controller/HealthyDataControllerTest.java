package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Service.HealthyDataService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorBreatheService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorFallService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorHumidityService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorRateService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorTemperatureService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import pojos.ContractMachine;
import pojos.ListResult;
import pojos.Result;
import pojos.SensorRate;
import util.CurrentHolder;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class HealthyDataControllerTest {

    @Mock private HealthyDataService healthyDataService;
    @Mock private SensorTemperatureService sensorTemperatureService;
    @Mock private SensorHumidityService sensorHumidityService;
    @Mock private SensorRateService sensorRateService;
    @Mock private SensorBreatheService sensorBreatheService;
    @Mock private SensorFallService sensorFallService;
    @Mock private ContractMachineMapper contractMachineMapper;

    private HealthyDataController controller;

    @BeforeEach
    void setUp() {
        controller = new HealthyDataController();
        ReflectionTestUtils.setField(controller, "healthyDataService", healthyDataService);
        ReflectionTestUtils.setField(controller, "sensorTemperatureService", sensorTemperatureService);
        ReflectionTestUtils.setField(controller, "sensorHumidityService", sensorHumidityService);
        ReflectionTestUtils.setField(controller, "sensorRateService", sensorRateService);
        ReflectionTestUtils.setField(controller, "sensorBreatheService", sensorBreatheService);
        ReflectionTestUtils.setField(controller, "sensorFallService", sensorFallService);
        ReflectionTestUtils.setField(controller, "contractMachineMapper", contractMachineMapper);
    }

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
    }

    @Test
    void rateQueryAllowsOwnedDevice() {
        CurrentHolder.setCurrentId(7);
        when(contractMachineMapper.findByUserIdAndConnectionId("7", "WALLE_1")).thenReturn(new ContractMachine());
        when(healthyDataService.getRate("WALLE_1")).thenReturn(new ListResult<>(List.of(new SensorRate())));

        Result result = controller.getRate("WALLE_1");

        assertThat(result.getCode()).isEqualTo(1);
        verify(healthyDataService).getRate("WALLE_1");
    }

    @Test
    void rateQueryRejectsDeviceNotOwnedByCurrentUser() {
        CurrentHolder.setCurrentId(7);
        when(contractMachineMapper.findByUserIdAndConnectionId("7", "OTHER")).thenReturn(null);

        Result result = controller.getRate("OTHER");

        assertThat(result.getCode()).isEqualTo(0);
        assertThat(result.getMsg()).contains("设备不存在或不属于当前用户");
        verify(healthyDataService, never()).getRate("OTHER");
    }
}
