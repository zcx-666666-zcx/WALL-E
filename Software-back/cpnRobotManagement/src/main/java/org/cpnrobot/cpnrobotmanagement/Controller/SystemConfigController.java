package org.cpnrobot.cpnrobotmanagement.Controller;

import io.jsonwebtoken.Claims;
import jakarta.servlet.http.HttpServletRequest;
import org.cpnrobot.cpnrobotmanagement.Service.SystemConfigService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.Result;
import pojos.SystemConfig;
import util.JwtUtils;

import java.util.List;

@RestController
@RequestMapping("/api/system-config")
@CrossOrigin(origins = "*", maxAge = 3600)
public class SystemConfigController {

    @Autowired
    private SystemConfigService systemConfigService;

    @GetMapping("/public")
    public Result publicConfig() {
        return Result.success(systemConfigService.getRuntimeConfig(false));
    }

    @GetMapping
    public Result list(HttpServletRequest request) {
        if (!isAdmin(request)) {
            return Result.error("无权限");
        }
        return Result.success(systemConfigService.listAll());
    }

    @PutMapping
    public Result update(@RequestBody List<SystemConfig> configs, HttpServletRequest request) {
        if (!isAdmin(request)) {
            return Result.error("无权限");
        }
        systemConfigService.saveAll(configs);
        return Result.success(systemConfigService.listAll());
    }

    private boolean isAdmin(HttpServletRequest request) {
        String token = request.getHeader("token");
        if (token == null || token.isBlank()) {
            return false;
        }
        try {
            Claims claims = JwtUtils.parseJwt(token);
            return "admin".equals(String.valueOf(claims.get("role")));
        } catch (Exception e) {
            return false;
        }
    }
}
