package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Service.EventService;
import org.cpnrobot.cpnrobotmanagement.Service.userService;
import org.junit.jupiter.api.Test;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;
import pojos.ContractMachine;
import pojos.Event;
import pojos.ListResult;
import pojos.Result;
import pojos.User;

import java.lang.reflect.Method;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DeviceEventControllerTest {

    @Test
    void deviceIdResolvesOwningUsersEvents() throws Exception {
        Class<?> controllerType = Class.forName(
                "org.cpnrobot.cpnrobotmanagement.Controller.DeviceEventController");
        Object controller = controllerType.getDeclaredConstructor().newInstance();

        ContractMachine machine = new ContractMachine();
        machine.setConnectionId("WALLE_1");
        machine.setUserId("3");
        ContractMachineMapper mapper = mock(ContractMachineMapper.class);
        when(mapper.findByUserIdAndConnectionId("3", "WALLE_1")).thenReturn(machine);
        userService users = mock(userService.class);
        User user = new User();
        user.setId(3);
        user.setUsername("test");
        when(users.getId("test")).thenReturn(user);
        EventService eventService = mock(EventService.class);
        when(eventService.searchEvent("3")).thenReturn(new ListResult<Event>(List.of()));
        ReflectionTestUtils.setField(controller, "contractMachineMapper", mapper);
        ReflectionTestUtils.setField(controller, "eventservice", eventService);
        ReflectionTestUtils.setField(controller, "userservice", users);
        ReflectionTestUtils.setField(controller, "deviceApiUser", "test");
        ReflectionTestUtils.setField(controller, "deviceApiId", "WALLE_1");

        Method search = controllerType.getDeclaredMethod("search", String.class);
        ResponseEntity<?> response = (ResponseEntity<?>) search.invoke(controller, "WALEE_1");

        assertThat(response.getStatusCode().value()).isEqualTo(200);
        assertThat(((Result) response.getBody()).getCode()).isEqualTo(1);
        verify(eventService).searchEvent("3");
    }

    @Test
    void configuredTokenIdentityCannotReadAnotherDevice() throws Exception {
        DeviceEventController controller = new DeviceEventController();
        ReflectionTestUtils.setField(controller, "deviceApiUser", "test");
        ReflectionTestUtils.setField(controller, "deviceApiId", "WALLE_1");

        ResponseEntity<Result> response = controller.search("OTHER_DEVICE");

        assertThat(response.getStatusCode().value()).isEqualTo(404);
    }
}
