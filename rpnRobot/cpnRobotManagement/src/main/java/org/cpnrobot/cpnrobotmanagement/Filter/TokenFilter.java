package org.cpnrobot.cpnrobotmanagement.Filter;

import io.jsonwebtoken.Claims;

import util.CurrentHolder;
import util.JwtUtils;
import jakarta.servlet.*;
import jakarta.servlet.annotation.WebFilter;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;

@WebFilter(urlPatterns = "/*")
public class TokenFilter implements Filter {

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws ServletException, IOException {
        System.out.println("进入过滤器");
        HttpServletRequest request = (HttpServletRequest) servletRequest;
        HttpServletResponse response = (HttpServletResponse) servletResponse;

        //获取请求路径
        String requestURI = request.getRequestURI();

        //判断是否是登录请求，如果路径中包含/login，说明是登录操作，放行
        if(requestURI.contains("/login")){
            filterChain.doFilter(request,response);
            return;
        }

        //获取请求头中的token
        String token = request.getHeader("token");

        //判断token是否存在，如果不存在，说明用户没有登录，返回错误信息（401状态码）
        if(token == null || token.isEmpty()){
            response.setStatus(401);
            return;
        }

        //判断token存在，校验令牌，如果校验事拜，返回错误信息（401状态码）
        try{
            Claims claims = JwtUtils.parseJwt(token);
            Integer empId = Integer.valueOf(claims.get("id").toString());
            CurrentHolder.setCurrentId(empId);

        } catch (Exception e){
            response.setStatus(401);
            return;
        }

        //校验通过，放行
        filterChain.doFilter(request,response);

        CurrentHolder.remove();

    }

}
