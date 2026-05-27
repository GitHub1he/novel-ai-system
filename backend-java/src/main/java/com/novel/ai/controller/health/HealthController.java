package com.novel.ai.controller.health;

import com.novel.ai.annotation.SkipAuthentication;
import com.novel.ai.model.dto.response.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping
@SkipAuthentication
public class HealthController {

    @GetMapping("/health")
    public ApiResponse<Map<String, Object>> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("timestamp", LocalDateTime.now().toString());
        health.put("service", "Novel AI System - Java Backend");
        health.put("version", "1.0.0");
        health.put("java_version", System.getProperty("java.version"));
        return ApiResponse.success(health);
    }
}