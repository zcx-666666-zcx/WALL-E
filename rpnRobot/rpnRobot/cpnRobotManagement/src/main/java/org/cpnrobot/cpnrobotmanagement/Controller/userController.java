package org.cpnrobot.cpnrobotmanagement.Controller;

import jakarta.websocket.server.PathParam;
import org.cpnrobot.cpnrobotmanagement.Service.userService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.Result;
import pojos.User;


@RequestMapping("/users")
@RestController
@CrossOrigin(origins = "http://localhost:5173")
public class userController {

    @Autowired
    private userService userservice;

    @PostMapping("/register")
    public Result register(@RequestBody User user){
        int num = userservice.register(user);
        if(num!=0){
            return Result.success();
        }
        return Result.error("注册失败");
    }

    @GetMapping("/getId/{username}")
    public Result getId(@PathVariable String username){
        System.out.println(username);
    	User user = userservice.getId(username);
    	return Result.success(user);
    }

    @GetMapping("getName/{id}")
    public Result getName(@PathVariable Integer id){
        User user = userservice.getName(id);
        return Result.success(user);
    }

}
