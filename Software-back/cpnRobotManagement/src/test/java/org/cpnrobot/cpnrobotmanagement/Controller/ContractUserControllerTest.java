package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.ContractUserService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.ContractUser;
import pojos.ListResult;
import pojos.Result;
import util.CurrentHolder;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ContractUserControllerTest {

    @Mock
    private ContractUserService contractUserService;

    @InjectMocks
    private ContractUserController controller;

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
    }

    @Test
    void searchUsesCurrentTokenUserInsteadOfPathUser() {
        CurrentHolder.setCurrentId(7);
        when(contractUserService.search("7")).thenReturn(new ListResult<>(List.of()));

        Result result = controller.search("999");

        assertThat(result.getCode()).isEqualTo(1);
        verify(contractUserService).search("7");
    }

    @Test
    void addForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        ContractUser request = new ContractUser();
        request.setContractName("家属");
        request.setContractPhoneNumber("13800000000");
        request.setUserId(999);
        when(contractUserService.add(argThat(user -> user.getUserId() == 7))).thenReturn(1);

        Result result = controller.add(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(contractUserService).add(argThat(user -> user.getUserId() == 7));
    }

    @Test
    void deleteForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        ContractUser request = new ContractUser();
        request.setContractName("家属");
        request.setUserId(999);
        when(contractUserService.delete(argThat(user -> user.getUserId() == 7))).thenReturn(1);

        Result result = controller.delete(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(contractUserService).delete(argThat(user -> user.getUserId() == 7));
    }
}
