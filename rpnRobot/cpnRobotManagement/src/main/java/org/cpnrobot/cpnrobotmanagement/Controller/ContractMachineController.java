package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.ContractMachineService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.ContractMachine;
import pojos.ListResult;
import pojos.Result;

@RestController
@RequestMapping("/contractMachine")
@CrossOrigin(origins = "http://localhost:5173")
public class ContractMachineController {

    @Autowired
    private ContractMachineService contractMachineService;

    @GetMapping("/search/{userId}")
    public Result search(@PathVariable String userId){
        ListResult<ContractMachine> listResult = contractMachineService.search(userId);
        return Result.success(listResult);
    }

    @PostMapping("/add")
    public Result add(@RequestBody ContractMachine contractMachine){
    	int num = contractMachineService.add(contractMachine);
    	if(num!=0){
    		return Result.success();
    	}
    	return Result.error("添加失败");
    }

    @DeleteMapping("/delete")
    public Result delete(@RequestBody ContractMachine contractMachine){
    	int num = contractMachineService.delete(contractMachine);
    	if(num!=0){
    		return Result.success();
    	}
    	return Result.error("删除失败");
    }
}
