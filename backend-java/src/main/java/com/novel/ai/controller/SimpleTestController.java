package com.novel.ai.controller;

import com.novel.ai.annotation.SkipAuthentication;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.service.SimpleAuthService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/simple")
public class SimpleTestController {

    private final SimpleAuthService simpleAuthService;

    public SimpleTestController(SimpleAuthService simpleAuthService) {
        this.simpleAuthService = simpleAuthService;
    }

    @GetMapping("/test")
    @SkipAuthentication
    public ApiResponse<String> test() {
        return ApiResponse.success(simpleAuthService.test());
    }
}