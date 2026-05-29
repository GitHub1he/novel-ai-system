package com.novel.ai.controller;

import com.novel.ai.model.dto.request.AIGenerateRequest;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.service.AIService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ai")
public class AIController {

    private final AIService aiService;

    public AIController(AIService aiService) {
        this.aiService = aiService;
    }

    /**
     * 生成章节内容
     * POST /api/ai/generate-content
     */
    @PostMapping("/generate-content")
    public ApiResponse<String> generateContent(@RequestBody @Valid AIGenerateRequest request,
                                              HttpServletRequest httpRequest) {
        // 验证用户身份
        Integer userId = (Integer) httpRequest.getAttribute("userId");

        String response = aiService.generateContent(request.getPrompt(), request.getContext());
        return ApiResponse.success("生成成功", response);
    }

    /**
     * 生成章节大纲
     * POST /api/ai/generate-outline
     */
    @PostMapping("/generate-outline")
    public ApiResponse<String> generateOutline(@RequestBody @Valid AIGenerateRequest request,
                                              HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");

        String response = aiService.generateOutline(request.getPrompt(), request.getContext());
        return ApiResponse.success("大纲生成成功", response);
    }

    /**
     * 扩展内容
     * POST /api/ai/expand-content
     */
    @PostMapping("/expand-content")
    public ApiResponse<String> expandContent(@RequestBody @Valid AIGenerateRequest request,
                                           HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");

        int targetWords = request.getTargetWords() != null ? request.getTargetWords() : 3000;
        String response = aiService.expandContent(request.getContent(), targetWords, request.getContext());
        return ApiResponse.success("内容扩展成功", response);
    }

    /**
     * 生成章节摘要
     * POST /api/ai/generate-summary
     */
    @PostMapping("/generate-summary")
    public ApiResponse<String> generateSummary(@RequestBody @Valid AIGenerateRequest request,
                                             HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");

        String title = request.getTitle() != null ? request.getTitle() : "";
        String response = aiService.generateSummary(request.getContent(), title);
        return ApiResponse.success("摘要生成成功", response);
    }

    /**
     * 生成展示摘要
     * POST /api/ai/generate-display-summary
     */
    @PostMapping("/generate-display-summary")
    public ApiResponse<String> generateDisplaySummary(@RequestBody @Valid AIGenerateRequest request,
                                                     HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");

        String title = request.getTitle() != null ? request.getTitle() : "";
        String response = aiService.generateDisplaySummary(request.getContent(), title);
        return ApiResponse.success("展示摘要生成成功", response);
    }

    /**
     * 智能续写
     * POST /api/ai/continue-writing
     */
    @PostMapping("/continue-writing")
    public ApiResponse<String> continueWriting(@RequestBody @Valid AIGenerateRequest request,
                                              HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");

        int targetLength = request.getTargetLength() != null ? request.getTargetLength() : 2000;
        String response = aiService.continueWriting(request.getContent(), request.getContext(), targetLength);
        return ApiResponse.success("续写成功", response);
    }

    /**
     * 检查AI服务状态
     * GET /api/ai/status
     */
    @GetMapping("/status")
    public ApiResponse<Boolean> checkStatus(HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");

        boolean isAvailable = ((com.novel.ai.service.AISpringServiceImpl) aiService).isAvailable();
        return ApiResponse.success(isAvailable);
    }
}