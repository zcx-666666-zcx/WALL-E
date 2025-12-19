package com.example.demo.controller;

import com.example.demo.entity.User;
import com.example.demo.service.UserService;
import com.example.demo.common.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    @Autowired
    private UserService userService;
    
    @Autowired
    private PasswordEncoder passwordEncoder;

    @PostMapping("/login")
    public ResponseEntity<Result<Map<String, Object>>> login(@RequestBody Map<String, String> loginData) {
        String username = loginData.get("username");
        String password = loginData.get("password");
        String openid = loginData.get("openid");
        
        User user = null;
        
        // 如果提供了openid，使用微信登录方式
        if (openid != null && !openid.isEmpty()) {
            user = userService.getUserByOpenid(openid);
            
            // 如果用户不存在，则创建新用户
            if (user == null) {
                user = new User();
                user.setOpenid(openid);
                user.setNickname(loginData.getOrDefault("nickname", "默认用户"));
                user.setAvatarUrl(loginData.getOrDefault("avatarUrl", ""));
                user.setGender(loginData.getOrDefault("gender", ""));
                user.setCountry(loginData.getOrDefault("country", ""));
                user.setProvince(loginData.getOrDefault("province", ""));
                user.setCity(loginData.getOrDefault("city", ""));
                user.setLanguage(loginData.getOrDefault("language", ""));
                user.setCreateTime(LocalDateTime.now());
                user.setUpdateTime(LocalDateTime.now());
                user = userService.saveUser(user);
            }
        } 
        // 如果提供了用户名和密码，使用传统登录方式
        else if (username != null && !username.isEmpty() && password != null && !password.isEmpty()) {
            user = userService.getUserByUsername(username);
            
            // 检查用户是否存在以及密码是否正确
            if (user == null || !passwordEncoder.matches(password, user.getPassword())) {
                return ResponseEntity.ok(Result.error("用户名或密码错误"));
            }
        } 
        // 如果既没有openid也没有用户名密码，则返回错误
        else {
            return ResponseEntity.ok(Result.error("缺少必要的登录参数"));
        }
        
        // 生成token（简化处理，实际项目中应使用JWT）
        String token = UUID.randomUUID().toString();
        
        Map<String, Object> responseData = new HashMap<>();
        responseData.put("token", token);
        responseData.put("user", user);
        
        return ResponseEntity.ok(Result.success("登录成功", responseData));
    }

    @PostMapping("/register")
    public ResponseEntity<Result<Map<String, Object>>> register(@RequestBody Map<String, String> registerData) {
        String username = registerData.get("username");
        String password = registerData.get("password");
        String email = registerData.get("email");
        String openid = registerData.get("openid");
        
        // 检查用户名是否已存在
        if (username != null && !username.isEmpty()) {
            User existingUser = userService.getUserByUsername(username);
            if (existingUser != null) {
                return ResponseEntity.ok(Result.error("用户名已存在"));
            }
        }
        
        // 检查openid是否已存在（微信登录用户）
        if (openid != null && !openid.isEmpty()) {
            User existingUser = userService.getUserByOpenid(openid);
            if (existingUser != null) {
                return ResponseEntity.ok(Result.error("用户已存在"));
            }
        }
        
        // 创建新用户
        User newUser = new User();
        if (openid != null && !openid.isEmpty()) {
            // 微信登录注册
            newUser.setOpenid(openid);
            newUser.setNickname(registerData.getOrDefault("nickname", "默认用户"));
            newUser.setAvatarUrl(registerData.getOrDefault("avatarUrl", ""));
            newUser.setGender(registerData.getOrDefault("gender", ""));
            newUser.setCountry(registerData.getOrDefault("country", ""));
            newUser.setProvince(registerData.getOrDefault("province", ""));
            newUser.setCity(registerData.getOrDefault("city", ""));
            newUser.setLanguage(registerData.getOrDefault("language", ""));
        } else {
            // 传统用户名密码注册
            newUser.setUsername(username);
            // 使用BCrypt加密密码
            newUser.setPassword(passwordEncoder.encode(password));
            newUser.setNickname(username); // 默认使用用户名作为昵称
        }
        newUser.setEmail(email);
        newUser.setCreateTime(LocalDateTime.now());
        newUser.setUpdateTime(LocalDateTime.now());
        
        // 保存用户
        User savedUser = userService.saveUser(newUser);
        
        // 生成token
        String token = UUID.randomUUID().toString();
        
        Map<String, Object> responseData = new HashMap<>();
        responseData.put("token", token);
        responseData.put("user", savedUser);
        
        return ResponseEntity.ok(Result.success("注册成功", responseData));
    }

    @PostMapping("/logout")
    public ResponseEntity<Result<String>> logout() {
        return ResponseEntity.ok(Result.success("登出成功", ""));
    }
}