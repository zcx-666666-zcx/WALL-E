package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.ContractMachineService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.ContractMachine;
import pojos.ListResult;
import pojos.Result;
import util.CurrentHolder;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ContractMachineControllerTest {

    @Mock
    private ContractMachineService contractMachineService;

    @InjectMocks
    private ContractMachineController controller;

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
    }

    @Test
    void searchUsesCurrentTokenUserInsteadOfPathUser() {
        CurrentHolder.setCurrentId(7);
        when(contractMachineService.searchForCurrentUser(7)).thenReturn(new ListResult<>(List.of()));

        Result result = controller.search("999");

        assertThat(result.getCode()).isEqualTo(1);
        verify(contractMachineService).searchForCurrentUser(7);
    }

    @Test
    void addForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        ContractMachine request = new ContractMachine();
        request.setUserId("999");
        when(contractMachineService.addForCurrentUser(request, 7)).thenReturn(1);

        Result result = controller.add(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(contractMachineService).addForCurrentUser(request, 7);
    }

    @Test
    void deleteForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        ContractMachine request = new ContractMachine();
        request.setUserId("999");
        when(contractMachineService.deleteForCurrentUser(request, 7)).thenReturn(1);

        Result result = controller.delete(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(contractMachineService).deleteForCurrentUser(request, 7);
    }

    @Test
    void updateIpForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        ContractMachine request = new ContractMachine();
        request.setUserId("999");
        request.setId(3);
        request.setRobotIp("192.168.1.20");
        when(contractMachineService.updateRobotIpForCurrentUser(request, 7)).thenReturn(1);

        Result result = controller.updateRobotIp(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(contractMachineService).updateRobotIpForCurrentUser(request, 7);
    }
}
