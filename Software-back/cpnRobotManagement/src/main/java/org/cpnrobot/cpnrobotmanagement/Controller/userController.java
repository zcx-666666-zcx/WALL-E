package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.userService;
import org.cpnrobot.cpnrobotmanagement.dto.ChangePasswordRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.Result;
import pojos.User;
import util.CurrentHolder;


@RequestMapping("/api/users")
@RestController
@CrossOrigin(origins = "*",maxAge = 3600)
public class userController {

    @Autowired
    private userService userservice;

    @PostMapping("/register")
    public Result register(@RequestBody User user){
        int num = userservice.register(user);
        if(num==1){
            return Result.success();
        }
        if (num == 2) {
            return Result.error("用户名已存在");
        }
        return Result.error("请输入完整注册信息");
    }

    @PutMapping("/password")
    public Result changePassword(@RequestBody ChangePasswordRequest request){
        Integer userId = CurrentHolder.getCurrentId();
        int num = userservice.changePassword(userId, request.getOldPassword(), request.getNewPassword());
        if(num!=0){
            return Result.success();
        }
        return Result.error("原密码错误或新密码不符合要求");
    }

    @GetMapping("/getId/{username}")
    public Result getId(@PathVariable String username){
        User user = userservice.getId(username);
        return Result.success(user);
    }

    @GetMapping("getName/{id}")
    public Result getName(@PathVariable Integer id){
        User user = userservice.getName(id);
        return Result.success(user);
    }

}
