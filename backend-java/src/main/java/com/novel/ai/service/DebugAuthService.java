package com.novel.ai.service;

import com.novel.ai.model.dto.request.LoginRequest;
import com.novel.ai.model.dto.request.RegisterRequest;
import com.novel.ai.model.dto.response.AuthResponse;
import org.springframework.stereotype.Service;

@Service
public class DebugAuthService {

    public AuthResponse register(RegisterRequest request) {
        System.out.println("Register request received: " + request.getUsername());
        AuthResponse response = AuthResponse.builder()
                .token("debug-token-123")
                .user(AuthResponse.User.builder()
                        .id(1)
                        .username(request.getUsername())
                        .email(request.getEmail())
                        .build())
                .build();
        System.out.println("Register response created: " + response.getUser().getUsername());
        return response;
    }

    public AuthResponse login(LoginRequest request) {
        System.out.println("Login request received: " + request.getEmail());
        AuthResponse response = AuthResponse.builder()
                .token("debug-token-123")
                .user(AuthResponse.User.builder()
                        .id(1)
                        .username("debuguser")
                        .email(request.getEmail())
                        .build())
                .build();
        System.out.println("Login response created: " + response.getUser().getUsername());
        return response;
    }
}