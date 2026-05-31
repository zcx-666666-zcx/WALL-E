package org.cpnrobot.cpnrobotmanagement.Service;

import org.cpnrobot.cpnrobotmanagement.Mapper.userMapper;
import org.cpnrobot.cpnrobotmanagement.Service.impl.userServiceImpl;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.LoginInfo;
import pojos.User;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class userServiceImplTest {

    @Mock
    private userMapper userMapper;

    @InjectMocks
    private userServiceImpl service;

    @Test
    void loginUpgradesLegacyPlaintextPasswordAndKeepsRole() {
        User stored = new User();
        stored.setId(1);
        stored.setUsername("admin");
        stored.setPassword("admin123");
        stored.setRole("admin");
        when(userMapper.findByUsername("admin")).thenReturn(stored);

        LoginInfo result = service.login(loginRequest("admin", "admin123"));

        assertThat(result).isNotNull();
        assertThat(result.getUsername()).isEqualTo("admin");
        assertThat(result.getRole()).isEqualTo("admin");
        assertThat(result.getToken()).isNotBlank();

        ArgumentCaptor<String> passwordCaptor = ArgumentCaptor.forClass(String.class);
        verify(userMapper).updatePassword(org.mockito.ArgumentMatchers.eq(1), passwordCaptor.capture());
        assertThat(passwordCaptor.getValue()).startsWith("$2");
    }

    @Test
    void registerReturnsDuplicateCodeWhenUsernameExists() {
        User request = loginRequest("admin", "admin123");
        when(userMapper.register_check(request)).thenReturn(new User());

        int result = service.register(request);

        assertThat(result).isEqualTo(2);
        verify(userMapper, never()).register(request);
    }

    private User loginRequest(String username, String password) {
        User user = new User();
        user.setUsername(username);
        user.setPassword(password);
        return user;
    }
}
