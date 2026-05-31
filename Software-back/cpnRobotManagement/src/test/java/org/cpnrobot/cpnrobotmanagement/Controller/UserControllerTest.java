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
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class UserControllerTest {

    @Mock
    private userService userService;

    @InjectMocks
    private userController controller;

    @Test
    void registerReturnsDuplicateUsernameMessage() {
        User request = new User();
        request.setUsername("admin");
        request.setPassword("admin123");

        when(userService.register(request)).thenReturn(2);

        Result result = controller.register(request);

        assertThat(result.getCode()).isEqualTo(0);
        assertThat(result.getMsg()).isEqualTo("用户名已存在");
    }
}
