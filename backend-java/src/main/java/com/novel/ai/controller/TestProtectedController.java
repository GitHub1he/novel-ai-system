package com.novel.ai.controller;

import com.novel.ai.annotation.SkipAuthentication;
import com.novel.ai.model.dto.response.ApiResponse;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/protected")
public class TestProtectedController {

    @GetMapping("/user-info")
    public ApiResponse<String> getUserInfo(HttpServletRequest request) {
        Integer userId = (Integer) request.getAttribute("userId");
        String username = (String) request.getAttribute("username");

        System.out.println("Debug - UserId: " + userId + ", Username: " + username);
        System.out.println("Debug - Request attrs: " + request.getAttributeNames().toString());

        return ApiResponse.success("UserId: " + userId + ", Username: " + username);
    }

    @GetMapping("/public")
    @SkipAuthentication
    public ApiResponse<String> publicEndpoint() {
        return ApiResponse.success("Public endpoint working!");
    }
}