package com.novel.ai.security.interceptor;

import com.novel.ai.annotation.SkipAuthentication;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.security.jwt.JwtService;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

import java.io.IOException;

@Component
public class AuthInterceptor implements HandlerInterceptor {

    private final JwtService jwtService;
    private final ObjectMapper objectMapper;

    public AuthInterceptor(JwtService jwtService, ObjectMapper objectMapper) {
        this.jwtService = jwtService;
        this.objectMapper = objectMapper;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 检查是否跳过认证
        if (handler instanceof HandlerMethod handlerMethod) {
            SkipAuthentication skipAuth = handlerMethod.getMethodAnnotation(SkipAuthentication.class);
            if (skipAuth == null) {
                skipAuth = handlerMethod.getBeanType().getAnnotation(SkipAuthentication.class);
            }
            if (skipAuth != null) {
                System.out.println("Skipping authentication for: " + handlerMethod.getMethod().getName());
                return true;
            }
        }

        System.out.println("Authentication required for handler: " + handler);

        // 提取JWT token
        String token = extractToken(request);
        if (token == null) {
            sendErrorResponse(response, 401, "未提供认证令牌");
            return false;
        }

        // 验证token
        if (!jwtService.isTokenValid(token)) {
            sendErrorResponse(response, 401, "令牌无效或已过期");
            return false;
        }

        // 将用户信息存储到request attribute中
        String username = jwtService.extractUsername(token);
        Integer userId = jwtService.extractUserId(token);
        request.setAttribute("username", username);
        request.setAttribute("userId", userId);

        return true;
    }

    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }

    private void sendErrorResponse(HttpServletResponse response, int status, String message) throws IOException {
        response.setStatus(status);
        response.setContentType("application/json;charset=UTF-8");
        ApiResponse<Object> errorResponse = ApiResponse.error(status, message);
        response.getWriter().write(objectMapper.writeValueAsString(errorResponse));
    }
}