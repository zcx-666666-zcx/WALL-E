package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.ContractMachine;
import pojos.ListResult;

public interface ContractMachineService {
    ListResult<ContractMachine> search(String userId);

    int add(ContractMachine contractMachine);

    int delete(ContractMachine contractMachine);

    int updateRobotIp(ContractMachine contractMachine);

    ListResult<ContractMachine> searchForCurrentUser(Integer currentUserId);

    int addForCurrentUser(ContractMachine contractMachine, Integer currentUserId);

    int deleteForCurrentUser(ContractMachine contractMachine, Integer currentUserId);

    int updateRobotIpForCurrentUser(ContractMachine contractMachine, Integer currentUserId);
}
