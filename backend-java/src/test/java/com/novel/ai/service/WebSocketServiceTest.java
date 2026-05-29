package com.novel.ai.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.messaging.simp.SimpMessagingTemplate;

import java.util.HashMap;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class WebSocketServiceTest {

    @Mock
    private SimpMessagingTemplate messagingTemplate;

    @InjectMocks
    private WebSocketService webSocketService;

    private final String TEST_TASK_ID = "test-task-123";

    @BeforeEach
    void setUp() {
        // No setup needed for this test
    }

    @Test
    void testSendGenerationStarted() {
        // When
        webSocketService.sendGenerationStarted(TEST_TASK_ID, 3);

        // Then
        verify(messagingTemplate, times(1)).convertAndSend(
                eq("/topic/chapters/generate/" + TEST_TASK_ID),
                any(Map.class)
        );
    }

    @Test
    void testSendVersionStarted() {
        // When
        webSocketService.sendVersionStarted(TEST_TASK_ID, 1);

        // Then
        verify(messagingTemplate, times(1)).convertAndSend(
                eq("/topic/chapters/generate/" + TEST_TASK_ID),
                any(Map.class)
        );
    }

    @Test
    void testSendProgressUpdate() {
        // When
        webSocketService.sendProgressUpdate(TEST_TASK_ID, 100, 1000, "测试内容");

        // Then
        verify(messagingTemplate, times(1)).convertAndSend(
                eq("/topic/chapters/generate/" + TEST_TASK_ID),
                any(Map.class)
        );
    }

    @Test
    void testSendGenerationCompleted() {
        // When
        webSocketService.sendGenerationCompleted(TEST_TASK_ID, "生成的内容");

        // Then
        verify(messagingTemplate, times(1)).convertAndSend(
                eq("/topic/chapters/generate/" + TEST_TASK_ID),
                any(Map.class)
        );
    }

    @Test
    void testSendGenerationError() {
        // When
        webSocketService.sendGenerationError(TEST_TASK_ID, "生成失败");

        // Then
        verify(messagingTemplate, times(1)).convertAndSend(
                eq("/topic/chapters/generate/" + TEST_TASK_ID),
                any(Map.class)
        );
    }

    @Test
    void testSendEntityProgress() {
        // When
        webSocketService.sendEntityProgress(TEST_TASK_ID, "character", 5, 10);

        // Then
        verify(messagingTemplate, times(1)).convertAndSend(
                eq("/topic/chapters/generate/" + TEST_TASK_ID),
                any(Map.class)
        );
    }

    @Test
    void testSendCustomMessage() {
        // Given
        Map<String, Object> customData = new HashMap<>();
        customData.put("customKey", "customValue");

        // When
        webSocketService.sendCustomMessage(TEST_TASK_ID, "custom_event", customData);

        // Then
        verify(messagingTemplate, times(1)).convertAndSend(
                eq("/topic/chapters/generate/" + TEST_TASK_ID),
                any(Map.class)
        );
    }
}