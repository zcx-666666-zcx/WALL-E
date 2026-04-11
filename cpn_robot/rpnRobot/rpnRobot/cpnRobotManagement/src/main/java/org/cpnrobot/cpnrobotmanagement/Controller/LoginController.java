package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.userService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.LoginInfo;
import pojos.Result;
import pojos.User;

@RestController()
@RequestMapping("/login")
@CrossOrigin(origins = "http://localhost:5173")
public class LoginController {

    @Autowired
    private userService userservice;

    @PostMapping()
    public Result login(@RequestBody User user){
        LoginInfo l = userservice.login(user);
        if(l!= null){
            return Result.success(l);
        }
        return Result.error("用户名或密码错误");
    }

}
