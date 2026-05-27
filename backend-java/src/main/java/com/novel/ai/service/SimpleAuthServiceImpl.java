package com.novel.ai.service;

import com.novel.ai.model.dto.request.LoginRequest;
import com.novel.ai.model.dto.request.RegisterRequest;
import com.novel.ai.model.dto.response.AuthResponse;
import com.novel.ai.security.jwt.JwtService;
import com.novel.ai.security.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class SimpleAuthServiceImpl {

    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;

    // Simple in-memory user storage
    private final Map<String, UserInfo> usersByEmail = new HashMap<>();
    private final Map<String, UserInfo> usersByUsername = new HashMap<>();
    private int nextId = 1;

    public SimpleAuthServiceImpl(JwtService jwtService, PasswordEncoder passwordEncoder) {
        this.jwtService = jwtService;
        this.passwordEncoder = passwordEncoder;

        // Create a default test user
        String defaultPassword = passwordEncoder.encode("password123");
        UserInfo defaultUser = new UserInfo(1, "testuser", "test@example.com", defaultPassword);
        usersByEmail.put("test@example.com", defaultUser);
        usersByUsername.put("testuser", defaultUser);
    }

    public AuthResponse login(LoginRequest request) {
        UserInfo user = usersByEmail.get(request.getEmail());
        if (user == null) {
            throw new IllegalArgumentException("用户不存在");
        }

        if (!passwordEncoder.matches(request.getPassword(), user.encodedPassword)) {
            throw new IllegalArgumentException("密码错误");
        }

        String token = jwtService.generateToken(user.username, user.id);

        return AuthResponse.builder()
                .token(token)
                .user(AuthResponse.User.builder()
                        .id(user.id)
                        .username(user.username)
                        .email(user.email)
                        .build())
                .build();
    }

    public AuthResponse register(RegisterRequest request) {
        if (usersByEmail.containsKey(request.getEmail())) {
            throw new IllegalArgumentException("邮箱已被注册");
        }

        if (usersByUsername.containsKey(request.getUsername())) {
            throw new IllegalArgumentException("用户名已存在");
        }

        String encodedPassword = passwordEncoder.encode(request.getPassword());
        int userId = nextId++;

        UserInfo user = new UserInfo(userId, request.getUsername(), request.getEmail(), encodedPassword);
        usersByEmail.put(request.getEmail(), user);
        usersByUsername.put(request.getUsername(), user);

        String token = jwtService.generateToken(request.getUsername(), userId);

        return AuthResponse.builder()
                .token(token)
                .user(AuthResponse.User.builder()
                        .id(userId)
                        .username(request.getUsername())
                        .email(request.getEmail())
                        .build())
                .build();
    }

    private static class UserInfo {
        public Integer id;
        public String username;
        public String email;
        public String encodedPassword;  // Store full encoded password

        public UserInfo(Integer id, String username, String email, String encodedPassword) {
            this.id = id;
            this.username = username;
            this.email = email;
            this.encodedPassword = encodedPassword;
        }
    }
}