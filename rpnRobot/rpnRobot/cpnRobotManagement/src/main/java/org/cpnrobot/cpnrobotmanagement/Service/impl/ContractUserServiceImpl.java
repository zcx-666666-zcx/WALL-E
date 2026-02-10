package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractUserMapper;
import org.cpnrobot.cpnrobotmanagement.Service.ContractUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.ContractUser;
import pojos.ListResult;

import java.util.List;

@Service
public class ContractUserServiceImpl implements ContractUserService {

    @Autowired
    private ContractUserMapper contractUserMapper;

    @Override
    public int add(ContractUser contractUser) {
       if(contractUserMapper.add(contractUser)>0){
           return 1;
       }
       return 0;
    }

    @Override
    public ListResult<ContractUser> search(String userId) {
        List<ContractUser> listResult = contractUserMapper.search(userId);
        return new ListResult<>(listResult);
    }

    @Override
    public int delete(ContractUser contractUser) {
        if(contractUserMapper.delete(contractUser)>0){
            return 1;
        }
        return 0;
    }
}
