package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.ContractMachineService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.ContractMachine;
import pojos.ListResult;
import pojos.Result;
import util.CurrentHolder;

@RestController
@RequestMapping("/api/contractMachine")
@CrossOrigin(origins = "*",maxAge = 3600)
public class ContractMachineController {

    @Autowired
    private ContractMachineService contractMachineService;

    @GetMapping("/search/{userId}")
    public Result search(@PathVariable String userId){
        Integer currentUserId = CurrentHolder.getCurrentId();
        if (currentUserId == null) {
            return Result.error("未登录或 token 无效");
        }
        ListResult<ContractMachine> listResult = contractMachineService.searchForCurrentUser(currentUserId);
        return Result.success(listResult);
    }

    @PostMapping("/add")
    public Result add(@RequestBody ContractMachine contractMachine){
        Integer currentUserId = CurrentHolder.getCurrentId();
        if (currentUserId == null) {
            return Result.error("未登录或 token 无效");
        }
        int num = contractMachineService.addForCurrentUser(contractMachine, currentUserId);
        if(num!=0){
            return Result.success();
        }
        return Result.error("添加失败");
    }

    @DeleteMapping("/delete")
    public Result delete(@RequestBody ContractMachine contractMachine){
        Integer currentUserId = CurrentHolder.getCurrentId();
        if (currentUserId == null) {
            return Result.error("未登录或 token 无效");
        }
        int num = contractMachineService.deleteForCurrentUser(contractMachine, currentUserId);
        if(num!=0){
            return Result.success();
        }
        return Result.error("删除失败");
    }

    @PutMapping("/robot-ip")
    public Result updateRobotIp(@RequestBody ContractMachine contractMachine){
        Integer currentUserId = CurrentHolder.getCurrentId();
        if (currentUserId == null) {
            return Result.error("未登录或 token 无效");
        }
        int num = contractMachineService.updateRobotIpForCurrentUser(contractMachine, currentUserId);
        if(num!=0){
            return Result.success();
        }
        return Result.error("修改 IP 失败");
    }
}
