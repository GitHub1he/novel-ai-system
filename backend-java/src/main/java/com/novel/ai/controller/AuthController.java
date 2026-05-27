package com.novel.ai.controller;

import com.novel.ai.annotation.SkipAuthentication;
import com.novel.ai.model.dto.request.LoginRequest;
import com.novel.ai.model.dto.request.RegisterRequest;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.model.dto.response.AuthResponse;
import com.novel.ai.service.SimpleAuthServiceImpl;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final SimpleAuthServiceImpl authService;

    public AuthController(SimpleAuthServiceImpl authService) {
        this.authService = authService;
    }

    @PostMapping("/register")
    @SkipAuthentication
    public ApiResponse<AuthResponse> register(@RequestBody RegisterRequest request) {
        AuthResponse response = authService.register(request);
        return ApiResponse.success("注册成功", response);
    }

    @PostMapping("/login")
    @SkipAuthentication
    public ApiResponse<AuthResponse> login(@RequestBody LoginRequest request) {
        AuthResponse response = authService.login(request);
        return ApiResponse.success("登录成功", response);
    }

    @GetMapping("/me")
    public ApiResponse<AuthResponse.User> getCurrentUser(HttpServletRequest request) {
        Integer userId = (Integer) request.getAttribute("userId");
        String username = (String) request.getAttribute("username");

        AuthResponse.User user = AuthResponse.User.builder()
                .id(userId)
                .username(username)
                .email(null) // 暂不返回邮箱
                .build();

        return ApiResponse.success(user);
    }
}