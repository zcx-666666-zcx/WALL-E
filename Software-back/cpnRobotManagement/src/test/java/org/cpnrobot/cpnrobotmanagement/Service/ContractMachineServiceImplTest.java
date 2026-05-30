package org.cpnrobot.cpnrobotmanagement.Service;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Service.impl.ContractMachineServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.ContractMachine;
import pojos.ListResult;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ContractMachineServiceImplTest {

    @Mock
    private ContractMachineMapper contractMachineMapper;

    @InjectMocks
    private ContractMachineServiceImpl service;

    @BeforeEach
    void setUp() {
        service.setDefaultRobotIpForTests("127.0.0.1");
    }

    @Test
    void searchForCurrentUserCreatesDefaultDeviceWhenMissing() {
        when(contractMachineMapper.findByUserIdAndConnectionId("7", "WALLE_1")).thenReturn(null);
        when(contractMachineMapper.add(any(ContractMachine.class))).thenReturn(1);
        when(contractMachineMapper.search("7")).thenReturn(List.of(defaultMachine(1, "7")));

        ListResult<ContractMachine> result = service.searchForCurrentUser(7);

        ArgumentCaptor<ContractMachine> captor = ArgumentCaptor.forClass(ContractMachine.class);
        verify(contractMachineMapper).add(captor.capture());
        assertThat(captor.getValue().getMachines()).isEqualTo("瓦力");
        assertThat(captor.getValue().getConnectionId()).isEqualTo("WALLE_1");
        assertThat(captor.getValue().getUserId()).isEqualTo("7");
        assertThat(captor.getValue().getRobotIp()).isEqualTo("127.0.0.1");
        assertThat(result.getRows()).hasSize(1);
    }

    @Test
    void searchForCurrentUserDoesNotCreateDuplicateDefaultDevice() {
        when(contractMachineMapper.findByUserIdAndConnectionId("7", "WALLE_1")).thenReturn(defaultMachine(1, "7"));
        when(contractMachineMapper.search("7")).thenReturn(List.of(defaultMachine(1, "7")));

        ListResult<ContractMachine> result = service.searchForCurrentUser(7);

        verify(contractMachineMapper, never()).add(any());
        assertThat(result.getRows()).extracting(ContractMachine::getConnectionId).containsExactly("WALLE_1");
    }

    @Test
    void deleteRejectsDefaultDevice() {
        ContractMachine request = new ContractMachine();
        request.setMachines("瓦力");
        request.setConnectionId("WALLE_1");
        request.setUserId("7");

        int deleted = service.deleteForCurrentUser(request, 7);

        assertThat(deleted).isZero();
        verify(contractMachineMapper, never()).delete(any());
    }

    @Test
    void updateRobotIpRequiresDeviceOwnedByCurrentUser() {
        ContractMachine request = new ContractMachine();
        request.setId(3);
        request.setRobotIp("192.168.1.20");
        when(contractMachineMapper.getByIdAndUserId(3, "7")).thenReturn(defaultMachine(3, "7"));
        when(contractMachineMapper.updateRobotIp(any())).thenReturn(1);

        int updated = service.updateRobotIpForCurrentUser(request, 7);

        assertThat(updated).isEqualTo(1);
        ArgumentCaptor<ContractMachine> captor = ArgumentCaptor.forClass(ContractMachine.class);
        verify(contractMachineMapper).updateRobotIp(captor.capture());
        assertThat(captor.getValue().getUserId()).isEqualTo("7");
    }

    @Test
    void updateRobotIpRejectsDeviceOwnedByOtherUser() {
        ContractMachine request = new ContractMachine();
        request.setId(3);
        request.setRobotIp("192.168.1.20");
        when(contractMachineMapper.getByIdAndUserId(3, "7")).thenReturn(null);

        int updated = service.updateRobotIpForCurrentUser(request, 7);

        assertThat(updated).isZero();
        verify(contractMachineMapper, never()).updateRobotIp(any());
    }

    private ContractMachine defaultMachine(Integer id, String userId) {
        ContractMachine machine = new ContractMachine();
        machine.setId(id);
        machine.setMachines("瓦力");
        machine.setConnectionId("WALLE_1");
        machine.setUserId(userId);
        machine.setRobotIp("127.0.0.1");
        return machine;
    }
}
