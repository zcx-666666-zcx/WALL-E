package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.userService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.Result;
import pojos.User;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class LoginControllerTest {

    @Mock
    private userService userService;

    @InjectMocks
    private LoginController controller;

    @Test
    void loginRejectsMissingPasswordBeforeCallingService() {
        User request = new User();
        request.setUsername("admin");

        Result result = controller.login(request);

        assertThat(result.getCode()).isEqualTo(0);
        assertThat(result.getMsg()).isEqualTo("请输入用户名和密码");
        verify(userService, never()).login(any());
    }
}
