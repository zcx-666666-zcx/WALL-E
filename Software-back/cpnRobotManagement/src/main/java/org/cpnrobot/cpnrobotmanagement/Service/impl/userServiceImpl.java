package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.userMapper;
import org.cpnrobot.cpnrobotmanagement.Service.userService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import pojos.LoginInfo;
import pojos.User;
import util.JwtUtils;

import java.util.HashMap;
import java.util.Map;



@Service
public class userServiceImpl implements userService {

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Autowired
    private userMapper usermapper;

    @Override
    public LoginInfo login(User user) {
        if (user == null || user.getUsername() == null || user.getPassword() == null) {
            return null;
        }
        User u = usermapper.findByUsername(user.getUsername());
        if (u == null || !passwordMatches(user.getPassword(), u.getPassword())) {
            return null;
        }
        if (!isBcryptHash(u.getPassword())) {
            usermapper.updatePassword(u.getId(), passwordEncoder.encode(user.getPassword()));
        }
        String role = (u.getRole() == null || u.getRole().isBlank()) ? "user" : u.getRole();
        Map<String,Object> claims = new HashMap<>();
        claims.put("id",u.getId());
        claims.put("name",u.getUsername());
        claims.put("role", role);
        String token = JwtUtils.createJwt(claims);
        return new LoginInfo(u.getId(),u.getUsername(),null,token,role);
    }

    @Override
    public int register(User user) {
        if (user == null || user.getUsername() == null || user.getPassword() == null) {
            return 0;
        }
        User u = usermapper.register_check(user);
        if(u==null){
            user.setPassword(passwordEncoder.encode(user.getPassword()));
            int num = usermapper.register(user);
            if(num!=0){
                return 1;
            }
            return 0;
        }
        return 0;
    }

    @Override
    public int changePassword(Integer userId, String oldPassword, String newPassword) {
        if (userId == null || oldPassword == null || newPassword == null || newPassword.length() < 6) {
            return 0;
        }
        User u = usermapper.getName(userId);
        if (u == null || !passwordMatches(oldPassword, u.getPassword())) {
            return 0;
        }
        return usermapper.updatePassword(userId, passwordEncoder.encode(newPassword));
    }

    @Override
    public User getId(String username) {
        User u = usermapper.getId(username);
        clearPassword(u);
        return u;
    }

    @Override
    public User getName(Integer id) {
        User u = usermapper.getName(id);
        clearPassword(u);
        return u;
    }

    private boolean passwordMatches(String rawPassword, String storedPassword) {
        if (storedPassword == null) {
            return false;
        }
        if (isBcryptHash(storedPassword)) {
            return passwordEncoder.matches(rawPassword, storedPassword);
        }
        return storedPassword.equals(rawPassword);
    }

    private boolean isBcryptHash(String password) {
        return password != null && (
                password.startsWith("$2a$")
                        || password.startsWith("$2b$")
                        || password.startsWith("$2y$")
        );
    }

    private void clearPassword(User user) {
        if (user != null) {
            user.setPassword(null);
        }
    }
}
