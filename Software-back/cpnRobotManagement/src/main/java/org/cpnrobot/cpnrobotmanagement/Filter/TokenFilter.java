package org.cpnrobot.cpnrobotmanagement.Filter;

import io.jsonwebtoken.Claims;
import jakarta.servlet.DispatcherType;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.annotation.WebFilter;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import util.CurrentHolder;
import util.JwtUtils;

import java.io.IOException;

@WebFilter(urlPatterns = "/*", dispatcherTypes = {DispatcherType.REQUEST}, asyncSupported = true)
public class TokenFilter implements Filter {

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain)
            throws ServletException, IOException {
        HttpServletRequest request = (HttpServletRequest) servletRequest;
        HttpServletResponse response = (HttpServletResponse) servletResponse;

        String requestURI = request.getRequestURI();
        String method = request.getMethod();

        System.out.println("[TokenFilter] " + method + " " + requestURI);

        if ("OPTIONS".equalsIgnoreCase(method)) {
            response.setHeader("Access-Control-Allow-Origin", "*");
            response.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
            response.setHeader("Access-Control-Allow-Headers", "Content-Type,token");
            response.setStatus(HttpServletResponse.SC_NO_CONTENT);
            return;
        }

        boolean publicHealthyIngest =
                requestURI.equals("/api/healthy/addRate") ||
                requestURI.equals("/api/healthy/addHumidity") ||
                requestURI.equals("/api/healthy/addBreathe") ||
                requestURI.equals("/api/healthy/addTemperature") ||
                requestURI.equals("/api/healthy/addFall");
        boolean publicUserAuth =
                requestURI.equals("/api/users/register") ||
                requestURI.startsWith("/api/users/getId");

        if (!requestURI.startsWith("/api/") ||
                publicHealthyIngest ||
                publicUserAuth ||
                requestURI.startsWith("/api/robot/video-feed/") ||
                requestURI.startsWith("/api/robot/video-feed-low/") ||
                requestURI.startsWith("/api/robot/camera-frame/") ||
                requestURI.startsWith("/api/system-config/public")) {
            System.out.println("[TokenFilter] public route, bypass auth");
            filterChain.doFilter(request, response);
            return;
        }

        if (requestURI.contains("/login") || requestURI.contains("/onenet/callback")) {
            System.out.println("[TokenFilter] login/callback route, bypass auth");
            filterChain.doFilter(request, response);
            return;
        }

        String token = request.getHeader("token");
        System.out.println("[TokenFilter] token = " +
                (token != null ? token.substring(0, Math.min(20, token.length())) + "..." : "null"));

        if (token == null || token.isEmpty()) {
            System.out.println("[TokenFilter] missing token, returning 401");
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }

        try {
            Claims claims = JwtUtils.parseJwt(token);
            Object idClaim = claims.get("id");
            if (idClaim == null) {
                System.out.println("[TokenFilter] missing id claim, returning 401");
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                return;
            }
            Integer empId = Integer.valueOf(idClaim.toString());
            CurrentHolder.setCurrentId(empId);
            System.out.println("[TokenFilter] token valid, user id=" + empId);
        } catch (Exception e) {
            System.out.println("[TokenFilter] token invalid, returning 401: " + e.getMessage());
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }

        filterChain.doFilter(request, response);
        CurrentHolder.remove();
    }
}
