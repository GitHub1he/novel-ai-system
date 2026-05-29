package com.novel.ai.controller;

import com.novel.ai.model.dto.request.ChapterGenerationRequest;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.model.dto.response.ChapterGenerationResponse;
import com.novel.ai.service.AIChapterGenerationService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chapters")
public class AIChapterGenerationController {

    private final AIChapterGenerationService generationService;

    public AIChapterGenerationController(AIChapterGenerationService generationService) {
        this.generationService = generationService;
    }

    /**
     * 生成章节内容（带WebSocket进度反馈）
     * POST /api/chapters/generate-with-progress
     */
    @PostMapping("/generate-with-progress")
    public ApiResponse<ChapterGenerationResponse> generateWithProgress(
            @RequestBody @Valid ChapterGenerationRequest request,
            HttpServletRequest httpRequest) {

        Integer userId = (Integer) httpRequest.getAttribute("userId");

        ChapterGenerationResponse response = generationService.generateChapterWithProgress(request);

        return ApiResponse.success("生成任务已启动", response);
    }

    /**
     * 生成多个版本（带WebSocket进度反馈）
     * POST /api/chapters/generate-versions
     */
    @PostMapping("/generate-versions")
    public ApiResponse<ChapterGenerationResponse> generateMultipleVersions(
            @RequestBody @Valid ChapterGenerationRequest request,
            @RequestParam(defaultValue = "3") int versionCount,
            HttpServletRequest httpRequest) {

        Integer userId = (Integer) httpRequest.getAttribute("userId");

        ChapterGenerationResponse response = generationService.generateMultipleVersions(request, versionCount);

        return ApiResponse.success("多版本生成任务已启动", response);
    }

    /**
     * 智能续写（带WebSocket进度反馈）
     * POST /api/chapters/continue-with-progress
     */
    @PostMapping("/continue-with-progress")
    public ApiResponse<ChapterGenerationResponse> continueWithProgress(
            @RequestBody @Valid ChapterGenerationRequest request,
            @RequestParam(defaultValue = "2000") int targetLength,
            HttpServletRequest httpRequest) {

        Integer userId = (Integer) httpRequest.getAttribute("userId");

        ChapterGenerationResponse response = generationService.continueWritingWithProgress(
                request.getContent() != null ? request.getContent() : "",
                buildContextFromRequest(request),
                targetLength
        );

        return ApiResponse.success("续写任务已启动", response);
    }

    /**
     * 从请求构建上下文
     */
    private String buildContextFromRequest(ChapterGenerationRequest request) {
        StringBuilder context = new StringBuilder();

        if (request.getProjectInfo() != null) {
            context.append("项目信息: ").append(request.getProjectInfo()).append("\n");
        }

        if (request.getGenre() != null) {
            context.append("类型: ").append(request.getGenre()).append("\n");
        }

        if (request.getStyle() != null) {
            context.append("风格: ").append(request.getStyle()).append("\n");
        }

        return context.toString();
    }
}