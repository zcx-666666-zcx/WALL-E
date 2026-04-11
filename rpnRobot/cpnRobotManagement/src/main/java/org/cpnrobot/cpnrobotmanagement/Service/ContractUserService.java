package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.ContractUser;
import pojos.ListResult;

public interface ContractUserService {
    int add(ContractUser contractUser);

    ListResult<ContractUser> search(String userId);

    int delete(ContractUser contractUser);
}
