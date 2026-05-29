package com.novel.ai.service;

import com.novel.ai.model.dto.request.ChapterGenerationRequest;
import com.novel.ai.model.dto.response.ChapterGenerationResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
public class AIChapterGenerationService {

    private static final Logger logger = LoggerFactory.getLogger(AIChapterGenerationService.class);

    private final AIService aiService;
    private final WebSocketService webSocketService;

    public AIChapterGenerationService(AIService aiService, WebSocketService webSocketService) {
        this.aiService = aiService;
        this.webSocketService = webSocketService;
    }

    /**
     * 生成章节内容（带进度反馈）
     */
    public ChapterGenerationResponse generateChapterWithProgress(ChapterGenerationRequest request) {
        String taskId = UUID.randomUUID().toString();

        try {
            // 发送开始消息
            webSocketService.sendGenerationStarted(taskId, 1);

            // 构建上下文
            String context = buildGenerationContext(request);

            // 发送版本开始消息
            webSocketService.sendVersionStarted(taskId, 1);

            // 生成内容
            String content = aiService.generateContent(request.getPrompt(), context);

            // 发送进度更新（模拟分阶段生成）
            simulateProgressUpdates(taskId, content);

            // 发送完成消息
            ChapterGenerationResponse response = new ChapterGenerationResponse();
            response.setContent(content);
            response.setTaskId(taskId);
            response.setWordCount(content.length());

            webSocketService.sendGenerationCompleted(taskId, content);

            return response;

        } catch (Exception e) {
            logger.error("章节生成失败: {}", e.getMessage(), e);
            webSocketService.sendGenerationError(taskId, "生成失败: " + e.getMessage());

            ChapterGenerationResponse errorResponse = new ChapterGenerationResponse();
            errorResponse.setTaskId(taskId);
            errorResponse.setError(e.getMessage());
            return errorResponse;
        }
    }

    /**
     * 生成多个版本（带进度反馈）
     */
    public ChapterGenerationResponse generateMultipleVersions(ChapterGenerationRequest request, int versionCount) {
        String taskId = UUID.randomUUID().toString();

        try {
            // 发送开始消息
            webSocketService.sendGenerationStarted(taskId, versionCount);

            Map<Integer, String> versions = new HashMap<>();
            String context = buildGenerationContext(request);

            // 生成多个版本
            for (int i = 1; i <= versionCount; i++) {
                webSocketService.sendVersionStarted(taskId, i);

                String versionContent = aiService.generateContent(request.getPrompt(), context);
                versions.put(i, versionContent);

                // 发送进度更新
                webSocketService.sendProgressUpdate(taskId, i, versionCount, versionContent);

                // 模拟延迟
                Thread.sleep(500);
            }

            // 发送完成消息
            ChapterGenerationResponse response = new ChapterGenerationResponse();
            response.setVersions(versions);
            response.setTaskId(taskId);
            response.setVersionCount(versionCount);

            webSocketService.sendGenerationCompleted(taskId, "所有版本生成完成");

            return response;

        } catch (Exception e) {
            logger.error("多版本生成失败: {}", e.getMessage(), e);
            webSocketService.sendGenerationError(taskId, "生成失败: " + e.getMessage());

            ChapterGenerationResponse errorResponse = new ChapterGenerationResponse();
            errorResponse.setTaskId(taskId);
            errorResponse.setError(e.getMessage());
            return errorResponse;
        }
    }

    /**
     * 智能续写（带进度反馈）
     */
    public ChapterGenerationResponse continueWritingWithProgress(String existingContent, String context, int targetLength) {
        String taskId = UUID.randomUUID().toString();

        try {
            webSocketService.sendGenerationStarted(taskId, 1);
            webSocketService.sendVersionStarted(taskId, 1);

            String continuedContent = aiService.continueWriting(existingContent, context, targetLength);

            // 模拟进度更新
            simulateProgressUpdates(taskId, continuedContent);

            ChapterGenerationResponse response = new ChapterGenerationResponse();
            response.setContent(continuedContent);
            response.setTaskId(taskId);
            response.setWordCount(continuedContent.length());

            webSocketService.sendGenerationCompleted(taskId, continuedContent);

            return response;

        } catch (Exception e) {
            logger.error("续写失败: {}", e.getMessage(), e);
            webSocketService.sendGenerationError(taskId, "续写失败: " + e.getMessage());

            ChapterGenerationResponse errorResponse = new ChapterGenerationResponse();
            errorResponse.setTaskId(taskId);
            errorResponse.setError(e.getMessage());
            return errorResponse;
        }
    }

    /**
     * 构建生成上下文
     */
    private String buildGenerationContext(ChapterGenerationRequest request) {
        StringBuilder context = new StringBuilder();

        if (request.getProjectInfo() != null) {
            context.append("## 项目信息\n");
            context.append(request.getProjectInfo()).append("\n\n");
        }

        if (request.getCharacters() != null && !request.getCharacters().isEmpty()) {
            context.append("## 人物设定\n");
            context.append(request.getCharacters()).append("\n\n");
        }

        if (request.getWorldSettings() != null && !request.getWorldSettings().isEmpty()) {
            context.append("## 世界观设定\n");
            context.append(request.getWorldSettings()).append("\n\n");
        }

        if (request.getPreviousChapter() != null) {
            context.append("## 前情提要\n");
            context.append(request.getPreviousChapter()).append("\n\n");
        }

        if (request.getGenre() != null) {
            context.append("## 类型风格\n");
            context.append("类型: ").append(request.getGenre()).append("\n");
            if (request.getStyle() != null) {
                context.append("风格: ").append(request.getStyle()).append("\n");
            }
        }

        return context.toString();
    }

    /**
     * 模拟进度更新（实际应该从AI流式响应中获取）
     */
    private void simulateProgressUpdates(String taskId, String content) {
        try {
            int totalSteps = 5;
            for (int i = 1; i <= totalSteps; i++) {
                int progress = (i * 100) / totalSteps;
                String partialContent = content.substring(0, Math.min(content.length(), (i * content.length()) / totalSteps));

                webSocketService.sendProgressUpdate(taskId, i, totalSteps, partialContent);
                Thread.sleep(100); // 模拟生成延迟
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}