package com.novel.ai.controller;

import com.novel.ai.annotation.SkipAuthentication;
import com.novel.ai.model.dto.response.ApiResponse;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/test")
public class TestController {

    @GetMapping("/hello")
    @SkipAuthentication
    public ApiResponse<String> hello() {
        return ApiResponse.success("Hello from test endpoint!");
    }

    @PostMapping("/echo")
    @SkipAuthentication
    public ApiResponse<String> echo(@RequestBody String data) {
        return ApiResponse.success("Echo: " + data);
    }
}