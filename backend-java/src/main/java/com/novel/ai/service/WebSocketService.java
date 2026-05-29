package com.novel.ai.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class WebSocketService {

    private static final Logger logger = LoggerFactory.getLogger(WebSocketService.class);

    private final SimpMessagingTemplate messagingTemplate;
    private final ObjectMapper objectMapper;

    public WebSocketService(SimpMessagingTemplate messagingTemplate, ObjectMapper objectMapper) {
        this.messagingTemplate = messagingTemplate;
        this.objectMapper = objectMapper;
    }

    /**
     * 发送章节生成进度消息
     *
     * @param taskId 任务ID
     * @param event 事件类型 (started, version_started, progress, completed, error)
     * @param data 消息数据
     */
    public void sendGenerationProgress(String taskId, String event, Map<String, Object> data) {
        try {
            Map<String, Object> message = Map.of(
                    "event", event,
                    "data", data,
                    "taskId", taskId,
                    "timestamp", System.currentTimeMillis()
            );

            messagingTemplate.convertAndSend("/topic/chapters/generate/" + taskId, message);

            logger.info("WebSocket消息发送成功: {} - {}", taskId, event);

        } catch (Exception e) {
            logger.error("WebSocket消息发送失败: {} - {}", taskId, event, e);
        }
    }

    /**
     * 发送生成开始消息
     */
    public void sendGenerationStarted(String taskId, int totalVersions) {
        Map<String, Object> data = Map.of(
                "totalVersions", totalVersions,
                "status", "generation_started"
        );

        sendGenerationProgress(taskId, "started", data);
    }

    /**
     * 发送版本生成开始消息
     */
    public void sendVersionStarted(String taskId, int versionNumber) {
        Map<String, Object> data = Map.of(
                "versionNumber", versionNumber,
                "status", "version_started"
        );

        sendGenerationProgress(taskId, "version_started", data);
    }

    /**
     * 发送生成进度消息
     */
    public void sendProgressUpdate(String taskId, int currentTokens, int totalTokens, String content) {
        Map<String, Object> data = Map.of(
                "currentTokens", currentTokens,
                "totalTokens", totalTokens,
                "progress", Math.min(100, (currentTokens * 100) / totalTokens),
                "content", content,
                "status", "generating"
        );

        sendGenerationProgress(taskId, "progress", data);
    }

    /**
     * 发送生成完成消息
     */
    public void sendGenerationCompleted(String taskId, String result) {
        Map<String, Object> data = Map.of(
                "result", result,
                "status", "completed"
        );

        sendGenerationProgress(taskId, "completed", data);
    }

    /**
     * 发送生成错误消息
     */
    public void sendGenerationError(String taskId, String errorMessage) {
        Map<String, Object> data = Map.of(
                "error", errorMessage,
                "status", "error"
        );

        sendGenerationProgress(taskId, "error", data);
    }

    /**
     * 发送实体提取进度消息
     */
    public void sendEntityProgress(String taskId, String entityType, int processed, int total) {
        Map<String, Object> data = Map.of(
                "entityType", entityType,
                "processed", processed,
                "total", total,
                "progress", (processed * 100) / total,
                "status", "extracting"
        );

        sendGenerationProgress(taskId, "entity_progress", data);
    }

    /**
     * 发送自定义消息
     */
    public void sendCustomMessage(String taskId, String event, Map<String, Object> customData) {
        sendGenerationProgress(taskId, event, customData);
    }
}