package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Service.EventService;
import org.cpnrobot.cpnrobotmanagement.Service.userService;
import org.cpnrobot.cpnrobotmanagement.socket.DeviceIdentity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import pojos.ContractMachine;
import pojos.Event;
import pojos.ListResult;
import pojos.Result;
import pojos.User;

import java.util.List;

@RestController
@RequestMapping("/api/device/events")
public class DeviceEventController {

    @Autowired
    private EventService eventservice;

    @Autowired
    private userService userservice;

    @Autowired
    private ContractMachineMapper contractMachineMapper;

    @Value("${walle.device-api-user:test}")
    private String deviceApiUser;

    @Value("${walle.device-api-id:WALLE_1}")
    private String deviceApiId;

    @GetMapping("/{deviceId}")
    public ResponseEntity<Result> search(@PathVariable String deviceId) {
        String canonicalDeviceId = DeviceIdentity.canonicalize(deviceId);
        if (!canonicalDeviceId.equals(DeviceIdentity.canonicalize(deviceApiId))) {
            return ResponseEntity.notFound().build();
        }

        User user = userservice.getId(deviceApiUser);
        if (user == null || user.getId() == null) {
            return ResponseEntity.notFound().build();
        }

        String userId = String.valueOf(user.getId());
        ContractMachine machine = contractMachineMapper.findByUserIdAndConnectionId(userId, canonicalDeviceId);
        if (machine == null && DeviceIdentity.STANDARD_DEVICE_ID.equals(canonicalDeviceId)) {
            machine = contractMachineMapper.findByUserIdAndConnectionId(userId, DeviceIdentity.LEGACY_DEVICE_ID);
        }
        if (machine == null) {
            return ResponseEntity.notFound().build();
        }

        ListResult<Event> allEvents = eventservice.searchEvent(userId);
        String displayName = machine.getMachines();
        List<Event> deviceEvents = allEvents.getRows().stream()
                .filter(event -> isForDevice(event, canonicalDeviceId, displayName))
                .toList();
        return ResponseEntity.ok(Result.success(new ListResult<>(deviceEvents)));
    }

    private boolean isForDevice(Event event, String deviceId, String displayName) {
        String binding = event.getMachines();
        return binding == null
                || binding.isBlank()
                || binding.equals(displayName)
                || DeviceIdentity.canonicalize(binding).equals(deviceId);
    }
}
