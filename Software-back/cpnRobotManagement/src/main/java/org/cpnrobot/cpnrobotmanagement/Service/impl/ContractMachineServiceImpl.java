package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Service.ContractMachineService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.ContractMachine;
import pojos.ListResult;

import java.util.List;

@Service
public class ContractMachineServiceImpl implements ContractMachineService {

    @Autowired
    private ContractMachineMapper contractMachineMapper;

    @Override
    public ListResult<ContractMachine> search(String userId) {
        List<ContractMachine> listResult = contractMachineMapper.search(userId);
        return new ListResult<>(listResult);
    }

    @Override
    public int add(ContractMachine contractMachine) {
        if(contractMachineMapper.add(contractMachine)>0){
            return 1;
        }
        return 0;
    }

    @Override
    public int delete(ContractMachine contractMachine) {
        if(contractMachineMapper.delete(contractMachine)>0){
            return 1;
        }
        return 0;
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
}
