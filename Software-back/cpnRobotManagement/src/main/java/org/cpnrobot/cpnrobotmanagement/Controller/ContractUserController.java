package org.cpnrobot.cpnrobotmanagement.Controller;


import org.apache.ibatis.annotations.Delete;
import org.cpnrobot.cpnrobotmanagement.Service.ContractUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.ContractUser;
import pojos.ListResult;
import pojos.Result;
import util.CurrentHolder;

import java.util.List;

@RestController
@RequestMapping("/api/contractUser")
@CrossOrigin(origins = "*",maxAge = 3600)
public class ContractUserController {

    @Autowired
    private ContractUserService contractUserService;

    @GetMapping("/search/{userId}")
    public Result search(@PathVariable("userId") String userId){
        Integer currentUserId = CurrentHolder.getCurrentId();
        ListResult<ContractUser> listResult = contractUserService.search(String.valueOf(currentUserId));
        return Result.success(listResult);
    }

    @PostMapping("/add")
    public Result add(@RequestBody ContractUser contractUser){
        Integer currentUserId = CurrentHolder.getCurrentId();
        contractUser.setUserId(currentUserId);
        int num = contractUserService.add(contractUser);
        if(num!=0){
            return Result.success();
        }
        return Result.error("添加失败");
    }

    @DeleteMapping("/delete")
    public Result delete(@RequestBody ContractUser contractUser){
        Integer currentUserId = CurrentHolder.getCurrentId();
        contractUser.setUserId(currentUserId);
    	int num = contractUserService.delete(contractUser);
    	if(num!=0){
    		return Result.success();
    	}
    	return Result.error("删除失败");
    }
}
