package org.cpnrobot.cpnrobotmanagement.Controller;


import org.apache.ibatis.annotations.Delete;
import org.cpnrobot.cpnrobotmanagement.Service.ContractUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.ContractUser;
import pojos.ListResult;
import pojos.Result;

import java.util.List;

@RestController
@RequestMapping("/contractUser")
@CrossOrigin(origins = "http://localhost:5173")
public class ContractUserController {

    @Autowired
    private ContractUserService contractUserService;

    @GetMapping("/search/{userId}")
    public Result search(@PathVariable("userId") String userId){
        ListResult<ContractUser> listResult = contractUserService.search(userId);
        return Result.success(listResult);
    }

    @PostMapping("/add")
    public Result add(@RequestBody ContractUser contractUser){
        int num = contractUserService.add(contractUser);
        if(num!=0){
            return Result.success();
        }
        return Result.error("添加失败");
    }

    @DeleteMapping("/delete")
    public Result delete(@RequestBody ContractUser contractUser){
    	int num = contractUserService.delete(contractUser);
    	if(num!=0){
    		return Result.success();
    	}
    	return Result.error("删除失败");
    }
}
