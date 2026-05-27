package com.novel.ai.service;

import com.novel.ai.model.dto.request.LoginRequest;
import com.novel.ai.model.dto.request.RegisterRequest;
import com.novel.ai.model.dto.response.AuthResponse;
import com.novel.ai.security.jwt.JwtService;
import com.novel.ai.security.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

@Service
public class AuthService {

    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;

    // 简单的内存存储，生产环境应该使用数据库
    private final ConcurrentHashMap<String, User> users = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, User> usersByEmail = new ConcurrentHashMap<>();
    private final AtomicInteger idGenerator = new AtomicInteger(1);

    public AuthService(JwtService jwtService, PasswordEncoder passwordEncoder) {
        this.jwtService = jwtService;
        this.passwordEncoder = passwordEncoder;
    }

    public AuthResponse login(LoginRequest request) {
        User user = usersByEmail.get(request.getEmail());
        if (user == null) {
            throw new IllegalArgumentException("用户不存在");
        }

        if (!passwordEncoder.matches(request.getPassword(), user.passwordHash)) {
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

        if (users.containsKey(request.getUsername())) {
            throw new IllegalArgumentException("用户名已存在");
        }

        String passwordHash = passwordEncoder.encode(request.getPassword());
        int userId = idGenerator.getAndIncrement();

        User user = new User(userId, request.getUsername(), request.getEmail(), passwordHash);
        users.put(request.getUsername(), user);
        usersByEmail.put(request.getEmail(), user);

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

    private record User(Integer id, String username, String email, String passwordHash) {}
}