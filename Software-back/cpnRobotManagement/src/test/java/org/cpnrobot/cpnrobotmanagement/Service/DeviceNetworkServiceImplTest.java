package org.cpnrobot.cpnrobotmanagement.Service;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Mapper.DeviceNetworkStatusMapper;
import org.cpnrobot.cpnrobotmanagement.Service.impl.DeviceNetworkServiceImpl;
import org.cpnrobot.cpnrobotmanagement.dto.DeviceHeartbeatRequest;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;
import pojos.ContractMachine;
import pojos.DeviceNetworkStatus;
import pojos.User;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DeviceNetworkServiceImplTest {

    @Test
    void heartbeatUpsertsStatusAndRefreshesCompatibleRobotIp() {
        DeviceNetworkStatusMapper statusMapper = mock(DeviceNetworkStatusMapper.class);
        ContractMachineMapper machineMapper = mock(ContractMachineMapper.class);
        DeviceNetworkServiceImpl service = new DeviceNetworkServiceImpl();
        ReflectionTestUtils.setField(service, "statusMapper", statusMapper);
        ReflectionTestUtils.setField(service, "contractMachineMapper", machineMapper);
        userService users = mock(userService.class);
        User user = new User();
        user.setId(7);
        when(users.getId("test")).thenReturn(user);
        ReflectionTestUtils.setField(service, "userservice", users);
        ReflectionTestUtils.setField(service, "deviceApiUser", "test");
        DeviceHeartbeatRequest request = new DeviceHeartbeatRequest();
        request.setLanIp("192.168.1.25");
        request.setNetworkName("office-wifi");
        DeviceNetworkStatus stored = new DeviceNetworkStatus();
        stored.setDeviceId("WALLE_1");
        stored.setLanIp("192.168.1.25");
        stored.setLastSeenAt(LocalDateTime.now());
        when(statusMapper.findByDeviceIdAndUserId("WALLE_1", "7")).thenReturn(stored);

        DeviceNetworkStatus result = service.recordHeartbeat(
                "WALLE_1", request, "203.0.113.8");

        verify(statusMapper).upsert(any(DeviceNetworkStatus.class));
        verify(machineMapper).updateRobotIpByUserAndConnectionId("7", "WALLE_1", "192.168.1.25");
        assertThat(result.isOnline()).isTrue();
    }

    @Test
    void statusQueryRejectsDeviceNotOwnedByUser() {
        DeviceNetworkStatusMapper statusMapper = mock(DeviceNetworkStatusMapper.class);
        ContractMachineMapper machineMapper = mock(ContractMachineMapper.class);
        DeviceNetworkServiceImpl service = new DeviceNetworkServiceImpl();
        ReflectionTestUtils.setField(service, "statusMapper", statusMapper);
        ReflectionTestUtils.setField(service, "contractMachineMapper", machineMapper);
        when(statusMapper.findByDeviceIdAndUserId("WALLE_1", "7")).thenReturn(null);

        DeviceNetworkStatus result = service.getStatusForUser("WALLE_1", 7);

        assertThat(result).isNull();
    }

    @Test
    void staleHeartbeatIsReportedOffline() {
        DeviceNetworkStatusMapper statusMapper = mock(DeviceNetworkStatusMapper.class);
        ContractMachineMapper machineMapper = mock(ContractMachineMapper.class);
        DeviceNetworkServiceImpl service = new DeviceNetworkServiceImpl();
        ReflectionTestUtils.setField(service, "statusMapper", statusMapper);
        ReflectionTestUtils.setField(service, "contractMachineMapper", machineMapper);
        ReflectionTestUtils.setField(service, "onlineTimeoutSeconds", 120L);
        DeviceNetworkStatus stored = new DeviceNetworkStatus();
        stored.setDeviceId("WALLE_1");
        stored.setUserId("7");
        stored.setLastSeenAt(LocalDateTime.now().minusMinutes(3));
        when(statusMapper.findByDeviceIdAndUserId("WALLE_1", "7")).thenReturn(stored);

        DeviceNetworkStatus result = service.getStatusForUser("WALLE_1", 7);

        assertThat(result.isOnline()).isFalse();
    }

    @Test
    void anotherUsersDefaultMachineCannotReadDeviceStatus() {
        DeviceNetworkStatusMapper statusMapper = mock(DeviceNetworkStatusMapper.class);
        ContractMachineMapper machineMapper = mock(ContractMachineMapper.class);
        DeviceNetworkServiceImpl service = new DeviceNetworkServiceImpl();
        ReflectionTestUtils.setField(service, "statusMapper", statusMapper);
        ReflectionTestUtils.setField(service, "contractMachineMapper", machineMapper);
        when(statusMapper.findByDeviceIdAndUserId("WALLE_1", "99")).thenReturn(null);

        assertThat(service.getStatusForUser("WALLE_1", 99)).isNull();
    }
}
