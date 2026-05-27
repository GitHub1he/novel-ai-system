package com.novel.ai.controller;

import com.novel.ai.annotation.SkipAuthentication;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.security.password.PasswordEncoder;
import com.novel.ai.security.jwt.JwtService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/debug")
public class DebugController {

    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public DebugController(PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    @GetMapping("/services")
    @SkipAuthentication
    public ApiResponse<String> checkServices() {
        try {
            String test = passwordEncoder.encode("test");
            String token = jwtService.generateToken("debug", 1);
            return ApiResponse.success("Services working! Token: " + token.substring(0, 20) + "...");
        } catch (Exception e) {
            return ApiResponse.error("Service error: " + e.getMessage());
        }
    }

    @GetMapping("/health")
    @SkipAuthentication
    public ApiResponse<String> health() {
        return ApiResponse.success("Debug endpoint is working!");
    }
}