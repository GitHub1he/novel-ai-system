package com.novel.ai.security.jwt;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.*;

class JwtServiceTest {

    private JwtService jwtService;

    @BeforeEach
    void setUp() {
        jwtService = new JwtService();
        // 设置测试用的密钥 (Base64编码的256位密钥)
        String testSecret = "dGVzdC1zZWNyZXQta2V5LWZvci1qd3QtdGVzdGluZy1wdXJwb3Nlcy1vbHk=";
        ReflectionTestUtils.setField(jwtService, "secret", testSecret);
        ReflectionTestUtils.setField(jwtService, "jwtExpiration", 3600000L); // 1小时
    }

    @Test
    void testGenerateToken() {
        String token = jwtService.generateToken("testuser", 100);

        assertNotNull(token, "Token should not be null");
        assertTrue(token.length() > 0, "Token should not be empty");
    }

    @Test
    void testExtractUsername() {
        String username = "testuser";
        Integer userId = 100;
        String token = jwtService.generateToken(username, userId);

        String extractedUsername = jwtService.extractUsername(token);

        assertEquals(username, extractedUsername, "Extracted username should match");
    }

    @Test
    void testExtractUserId() {
        String username = "testuser";
        Integer userId = 100;
        String token = jwtService.generateToken(username, userId);

        Integer extractedUserId = jwtService.extractUserId(token);

        assertEquals(userId, extractedUserId, "Extracted user ID should match");
    }

    @Test
    void testValidToken() {
        String token = jwtService.generateToken("testuser", 100);

        assertTrue(jwtService.isTokenValid(token), "Token should be valid");
    }

    @Test
    void testInvalidToken() {
        String invalidToken = "invalid.token.string";

        assertFalse(jwtService.isTokenValid(invalidToken), "Invalid token should not be valid");
    }
}