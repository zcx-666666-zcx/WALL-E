package org.cpnrobot.cpnrobotmanagement.Filter;

import io.jsonwebtoken.Claims;

import util.CurrentHolder;
import util.JwtUtils;
import jakarta.servlet.*;
import jakarta.servlet.annotation.WebFilter;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;

@WebFilter(urlPatterns = "/*", dispatcherTypes = {DispatcherType.REQUEST}, asyncSupported = true)
public class TokenFilter implements Filter {

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws ServletException, IOException {
        HttpServletRequest request = (HttpServletRequest) servletRequest;
        HttpServletResponse response = (HttpServletResponse) servletResponse;

        String requestURI = request.getRequestURI();
        String method = request.getMethod();

        System.out.println("[TokenFilter] " + method + " " + requestURI);

        // 只拦截 /api/ 开头的请求
        if (!requestURI.startsWith("/api/") ||
                requestURI.startsWith("/api/healthy") ||
                requestURI.startsWith("/api/events/search") ||
                requestURI.startsWith("/api/robot/video-feed/") ||
                requestURI.startsWith("/api/robot/video-feed-low/") ||
                requestURI.startsWith("/api/robot/camera-frame/") ||
                requestURI.startsWith("/api/users/getId")
        ) {
            System.out.println("[TokenFilter] 非 API 或 healthy 路径，直接放行");
            filterChain.doFilter(request, response);
            return;
        }

        // 登录接口和 OneNET 回调不需要 token
        if (requestURI.contains("/login") || requestURI.contains("/onenet/callback")) {
            System.out.println("[TokenFilter] 白名单路径（登录/回调），直接放行");
            filterChain.doFilter(request, response);
            return;
        }

        // 校验 token
        String token = request.getHeader("token");
        System.out.println("[TokenFilter] token = " + (token != null ? token.substring(0, Math.min(20, token.length())) + "..." : "null"));

        if (token == null || token.isEmpty()) {
            System.out.println("[TokenFilter] *** 无 token，返回 401 ***");
            response.setStatus(401);
            return;
        }

        try {
            Claims claims = JwtUtils.parseJwt(token);
            Object idClaim = claims.get("id");
            if (idClaim == null) {
                System.out.println("[TokenFilter] *** token 中缺少 id claim，返回 401 ***");
                response.setStatus(401);
                return;
            }
            Integer empId = Integer.valueOf(idClaim.toString());
            CurrentHolder.setCurrentId(empId);
            System.out.println("[TokenFilter] token 有效，用户 id=" + empId + "，放行");
        } catch (Exception e) {
            System.out.println("[TokenFilter] *** token 校验失败，返回 401: " + e.getMessage() + " ***");
            response.setStatus(401);
            return;
        }

        filterChain.doFilter(request, response);
        CurrentHolder.remove();
    }

}
