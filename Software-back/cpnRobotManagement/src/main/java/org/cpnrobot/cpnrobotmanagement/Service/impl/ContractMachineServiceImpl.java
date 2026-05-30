package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Service.ContractMachineService;
import org.cpnrobot.cpnrobotmanagement.Service.SystemConfigService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.ContractMachine;
import pojos.ListResult;

import java.util.List;

@Service
public class ContractMachineServiceImpl implements ContractMachineService {

    private static final String DEFAULT_DEVICE_NAME = "瓦力";
    private static final String DEFAULT_DEVICE_ID = "WALLE_1";
    private String defaultRobotIp = "127.0.0.1";

    @Autowired
    private ContractMachineMapper contractMachineMapper;

    @Autowired(required = false)
    private SystemConfigService systemConfigService;

    public void setDefaultRobotIpForTests(String defaultRobotIp) {
        this.defaultRobotIp = defaultRobotIp;
    }

    @Override
    public ListResult<ContractMachine> search(String userId) {
        List<ContractMachine> listResult = contractMachineMapper.search(userId);
        return new ListResult<>(listResult);
    }

    @Override
    public ListResult<ContractMachine> searchForCurrentUser(Integer currentUserId) {
        if (currentUserId == null) {
            return new ListResult<>(List.of());
        }
        String userId = String.valueOf(currentUserId);
        ensureDefaultMachine(userId);
        return search(userId);
    }

    @Override
    public int add(ContractMachine contractMachine) {
        if(contractMachineMapper.add(contractMachine)>0){
            return 1;
        }
        return 0;
    }

    @Override
    public int addForCurrentUser(ContractMachine contractMachine, Integer currentUserId) {
        if (contractMachine == null || currentUserId == null) {
            return 0;
        }
        contractMachine.setUserId(String.valueOf(currentUserId));
        if (contractMachine.getRobotIp() == null || contractMachine.getRobotIp().isBlank()) {
            contractMachine.setRobotIp(resolveDefaultRobotIp());
        }
        return add(contractMachine);
    }

    @Override
    public int delete(ContractMachine contractMachine) {
        if(contractMachineMapper.delete(contractMachine)>0){
            return 1;
        }
        return 0;
    }

    @Override
    public int deleteForCurrentUser(ContractMachine contractMachine, Integer currentUserId) {
        if (contractMachine == null || currentUserId == null || isDefaultDevice(contractMachine)) {
            return 0;
        }
        contractMachine.setUserId(String.valueOf(currentUserId));
        return delete(contractMachine);
    }

    @Override
    public int updateRobotIp(ContractMachine contractMachine) {
        if (contractMachine == null || contractMachine.getId() == null || contractMachine.getUserId() == null) {
            return 0;
        }
        if (contractMachine.getRobotIp() == null || contractMachine.getRobotIp().isBlank()) {
            return 0;
        }
        if(contractMachineMapper.updateRobotIp(contractMachine)>0){
            return 1;
        }
        return 0;
    }

    @Override
    public int updateRobotIpForCurrentUser(ContractMachine contractMachine, Integer currentUserId) {
        if (contractMachine == null || currentUserId == null || contractMachine.getId() == null) {
            return 0;
        }
        if (contractMachine.getRobotIp() == null || contractMachine.getRobotIp().isBlank()) {
            return 0;
        }
        String userId = String.valueOf(currentUserId);
        ContractMachine owned = contractMachineMapper.getByIdAndUserId(contractMachine.getId(), userId);
        if (owned == null) {
            return 0;
        }
        contractMachine.setUserId(userId);
        return updateRobotIp(contractMachine);
    }

    private void ensureDefaultMachine(String userId) {
        ContractMachine existing = contractMachineMapper.findByUserIdAndConnectionId(userId, DEFAULT_DEVICE_ID);
        if (existing != null) {
            return;
        }
        ContractMachine machine = new ContractMachine();
        machine.setMachines(DEFAULT_DEVICE_NAME);
        machine.setConnectionId(DEFAULT_DEVICE_ID);
        machine.setUserId(userId);
        machine.setRobotIp(resolveDefaultRobotIp());
        contractMachineMapper.add(machine);
    }

    private String resolveDefaultRobotIp() {
        if (systemConfigService == null) {
            return defaultRobotIp;
        }
        return systemConfigService.getValue("robot.default-ip", defaultRobotIp);
    }

    private boolean isDefaultDevice(ContractMachine contractMachine) {
        return DEFAULT_DEVICE_ID.equals(contractMachine.getConnectionId())
                || DEFAULT_DEVICE_NAME.equals(contractMachine.getMachines());
    }
}
