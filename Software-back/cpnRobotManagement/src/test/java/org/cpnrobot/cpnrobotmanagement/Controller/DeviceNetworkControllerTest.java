package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.DeviceNetworkService;
import org.cpnrobot.cpnrobotmanagement.dto.DeviceHeartbeatRequest;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.ResponseEntity;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.test.util.ReflectionTestUtils;
import pojos.DeviceNetworkStatus;
import pojos.Result;
import util.CurrentHolder;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

class DeviceNetworkControllerTest {

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
    }

    @Test
    void heartbeatStoresCanonicalDeviceAndObservedAddress() {
        DeviceNetworkService service = mock(DeviceNetworkService.class);
        DeviceNetworkController controller = new DeviceNetworkController();
        ReflectionTestUtils.setField(controller, "deviceNetworkService", service);
        ReflectionTestUtils.setField(controller, "deviceApiId", "WALLE_1");
        DeviceHeartbeatRequest body = new DeviceHeartbeatRequest();
        body.setLanIp("192.168.1.25");
        body.setNetworkName("office-wifi");
        MockHttpServletRequest request = new MockHttpServletRequest();
        request.setRemoteAddr("203.0.113.8");
        DeviceNetworkStatus status = status("WALLE_1", true);
        when(service.recordHeartbeat("WALLE_1", body, "203.0.113.8")).thenReturn(status);

        ResponseEntity<Result> response = controller.heartbeat("WALEE_1", body, request);

        assertThat(response.getStatusCode().value()).isEqualTo(200);
        assertThat(response.getBody().getData()).isSameAs(status);
        verify(service).recordHeartbeat("WALLE_1", body, "203.0.113.8");
    }

    @Test
    void heartbeatRejectsUnconfiguredDevice() {
        DeviceNetworkService service = mock(DeviceNetworkService.class);
        DeviceNetworkController controller = new DeviceNetworkController();
        ReflectionTestUtils.setField(controller, "deviceNetworkService", service);
        ReflectionTestUtils.setField(controller, "deviceApiId", "WALLE_1");

        ResponseEntity<Result> response = controller.heartbeat(
                "OTHER_DEVICE", new DeviceHeartbeatRequest(), new MockHttpServletRequest());

        assertThat(response.getStatusCode().value()).isEqualTo(404);
        verifyNoInteractions(service);
    }

    @Test
    void statusQueryUsesLoggedInUserOwnership() {
        CurrentHolder.setCurrentId(7);
        DeviceNetworkService service = mock(DeviceNetworkService.class);
        DeviceNetworkController controller = new DeviceNetworkController();
        ReflectionTestUtils.setField(controller, "deviceNetworkService", service);
        DeviceNetworkStatus status = status("WALLE_1", true);
        when(service.getStatusForUser("WALLE_1", 7)).thenReturn(status);

        Result result = controller.status("WALEE_1");

        assertThat(result.getCode()).isEqualTo(1);
        assertThat(result.getData()).isSameAs(status);
        verify(service).getStatusForUser("WALLE_1", 7);
    }

    private DeviceNetworkStatus status(String deviceId, boolean online) {
        DeviceNetworkStatus status = new DeviceNetworkStatus();
        status.setDeviceId(deviceId);
        status.setOnline(online);
        status.setLastSeenAt(LocalDateTime.now());
        return status;
    }
}
