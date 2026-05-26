package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.userMapper;
import org.cpnrobot.cpnrobotmanagement.Service.userService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.LoginInfo;
import pojos.Result;
import pojos.User;
import util.JwtUtils;

import java.util.HashMap;
import java.util.Map;



@Service
public class userServiceImpl implements userService {

    @Autowired
    private userMapper usermapper;

    @Override
    public LoginInfo login(User user) {
        User u = usermapper.login(user);
        if(u!=null){
            String role = (u.getRole() == null || u.getRole().isBlank()) ? "user" : u.getRole();
            Map<String,Object> claims = new HashMap<>();
            claims.put("id",u.getId());
            claims.put("name",u.getUsername());
            claims.put("role", role);
            String token = JwtUtils.createJwt(claims);
            return new LoginInfo(u.getId(),u.getUsername(),u.getPassword(),token,role);
        }
        return null;
    }

    @Override
    public int register(User user) {
        User u = usermapper.register_check(user);
        if(u==null){
            int num = usermapper.register(user);
            if(num!=0){
                return 1;
            }
            return 0;
        }
        return 0;
    }

    @Override
    public User getId(String username) {
        User u = usermapper.getId(username);
        return u;
    }

    @Override
    public User getName(Integer id) {
        User u = usermapper.getName(id);
        return u;
    }
}
