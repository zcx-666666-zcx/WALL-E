package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.userService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.LoginInfo;
import pojos.Result;
import pojos.User;

@RestController()
@RequestMapping("/api/login")
@CrossOrigin(origins = "*",maxAge = 3600)
public class LoginController {

    @Autowired
    private userService userservice;

    @PostMapping()
    public Result login(@RequestBody User user){
        if (user == null || user.getUsername() == null || user.getUsername().isBlank()
                || user.getPassword() == null || user.getPassword().isBlank()) {
            return Result.error("请输入用户名和密码");
        }
        LoginInfo l = userservice.login(user);
        if(l!= null){
            return Result.success(l);
        }
        return Result.error("用户名或密码错误");
    }

}
