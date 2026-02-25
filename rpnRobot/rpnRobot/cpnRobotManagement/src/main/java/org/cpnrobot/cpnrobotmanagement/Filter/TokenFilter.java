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
        HttpServletRequest request = (HttpServletRequest) servletRequest;
        HttpServletResponse response = (HttpServletResponse) servletResponse;

        //获取请求路径
        String requestURI = request.getRequestURI();

        System.out.println("[TokenFilter] 收到请求，URI=" + requestURI);

        //判断是否是登录请求或 OneNET 回调请求：
        //- 登录请求（路径中包含 /login）需要放行，才能获取 token
        //- OneNET 回调（路径中包含 /onenet/callback）来自云平台，不携带前端登录 token，也需要放行
        if(requestURI.contains("/login") || requestURI.contains("/onenet/callback")){
            System.out.println("[TokenFilter] 放行请求（登录或 OneNET 回调），URI=" + requestURI);
            filterChain.doFilter(request,response);
            return;
        }

        //获取请求头中的token
        String token = request.getHeader("token");
        System.out.println("[TokenFilter] 从请求头获取到 token=" + token);

        //判断token是否存在，如果不存在，说明用户没有登录，返回错误信息（401状态码）
        if(token == null || token.isEmpty()){
            System.out.println("[TokenFilter] 未获取到 token，返回 401 未登录");
            response.setStatus(401);
            return;
        }

        //判断token存在，校验令牌，如果校验事拜，返回错误信息（401状态码）
        try{
            Claims claims = JwtUtils.parseJwt(token);
            Integer empId = Integer.valueOf(claims.get("id").toString());
            CurrentHolder.setCurrentId(empId);
            System.out.println("[TokenFilter] token 校验通过，当前用户 id=" + empId);

        } catch (Exception e){
            System.out.println("[TokenFilter] token 校验失败，返回 401，异常信息：" + e.getMessage());
            response.setStatus(401);
            return;
        }

        //校验通过，放行
        System.out.println("[TokenFilter] 已通过校验，放行后续过滤器与业务逻辑");
        filterChain.doFilter(request,response);

        CurrentHolder.remove();

    }

}
