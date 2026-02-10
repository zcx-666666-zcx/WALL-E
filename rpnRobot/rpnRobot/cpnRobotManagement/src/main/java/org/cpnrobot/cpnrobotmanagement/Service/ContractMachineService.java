package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.ContractMachine;
import pojos.ListResult;

public interface ContractMachineService {
    ListResult<ContractMachine> search(String userId);

    int add(ContractMachine contractMachine);

    int delete(ContractMachine contractMachine);
}
