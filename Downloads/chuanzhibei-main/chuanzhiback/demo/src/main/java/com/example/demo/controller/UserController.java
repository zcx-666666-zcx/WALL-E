package com.example.demo.controller;

import com.example.demo.entity.User;
import com.example.demo.service.UserService;
import com.example.demo.common.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*")
public class UserController {

    @Autowired
    private UserService userService;

    @GetMapping
    public ResponseEntity<Result<List<User>>> getAllUsers() {
        List<User> users = userService.getAllUsers();
        return ResponseEntity.ok(Result.success(users));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Result<User>> getUserById(@PathVariable Long id) {
        User user = userService.getUserById(id);
        if (user != null) {
            return ResponseEntity.ok(Result.success(user));
        } else {
            return ResponseEntity.ok(Result.error("用户不存在"));
        }
    }

    @PostMapping
    public ResponseEntity<Result<User>> createUser(@RequestBody User user) {
        User savedUser = userService.saveUser(user);
        return ResponseEntity.ok(Result.success("用户创建成功", savedUser));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Result<User>> updateUser(@PathVariable Long id, @RequestBody User userDetails) {
        User user = userService.getUserById(id);
        if (user != null) {
            user.setOpenid(userDetails.getOpenid());
            user.setNickname(userDetails.getNickname());
            user.setAvatarUrl(userDetails.getAvatarUrl());
            user.setGender(userDetails.getGender());
            user.setCountry(userDetails.getCountry());
            user.setProvince(userDetails.getProvince());
            user.setCity(userDetails.getCity());
            user.setLanguage(userDetails.getLanguage());
            user.setUpdateTime(java.time.LocalDateTime.now());
            
            User updatedUser = userService.saveUser(user);
            return ResponseEntity.ok(Result.success("用户更新成功", updatedUser));
        } else {
            return ResponseEntity.ok(Result.error("用户不存在"));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Result<String>> deleteUser(@PathVariable Long id) {
        User user = userService.getUserById(id);
        if (user != null) {
            userService.deleteUser(id);
            return ResponseEntity.ok(Result.success("删除成功", ""));
        } else {
            return ResponseEntity.ok(Result.error("用户不存在"));
        }
    }

    @GetMapping("/openid/{openid}")
    public ResponseEntity<Result<User>> getUserByOpenid(@PathVariable String openid) {
        User user = userService.getUserByOpenid(openid);
        if (user != null) {
            return ResponseEntity.ok(Result.success(user));
        } else {
            return ResponseEntity.ok(Result.error("用户不存在"));
        }
    }
    
    // 个人中心模块 - 获取用户收藏
    @GetMapping("/{id}/collections")
    public ResponseEntity<Result<List<User>>> getUserCollections(@PathVariable Long id) {
        // 这里应该返回用户的收藏列表，目前暂未实现完整的收藏功能
        // 只是提供接口框架
        return ResponseEntity.ok(Result.success("功能待实现", List.of()));
    }
    
    // 个人中心模块 - 删除用户收藏
    @DeleteMapping("/{id}/collections/{collectionId}")
    public ResponseEntity<Result<String>> deleteUserCollection(@PathVariable Long id, @PathVariable Long collectionId) {
        // 这里应该删除用户的指定收藏，目前暂未实现完整的收藏功能
        // 只是提供接口框架
        return ResponseEntity.ok(Result.success("功能待实现", ""));
    }
}