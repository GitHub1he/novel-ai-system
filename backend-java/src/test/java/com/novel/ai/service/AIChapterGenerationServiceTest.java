package com.novel.ai.service;

import com.novel.ai.model.dto.request.ChapterGenerationRequest;
import com.novel.ai.model.dto.response.ChapterGenerationResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AIChapterGenerationServiceTest {

    @Mock
    private AIService aiService;

    @Mock
    private WebSocketService webSocketService;

    @InjectMocks
    private AIChapterGenerationService generationService;

    private ChapterGenerationRequest testRequest;

    @BeforeEach
    void setUp() {
        testRequest = new ChapterGenerationRequest();
        testRequest.setPrompt("写一段关于武侠的小说内容");
        testRequest.setTitle("第一章");
        testRequest.setGenre("武侠");
        testRequest.setStyle("热血");
        testRequest.setProjectInfo("这是一个关于侠义的故事");
        testRequest.setTargetWords(2000);
    }

    @Test
    void testGenerateChapterWithProgress_Success() {
        // Given
        String expectedContent = "在苍茫的江湖中，一位少年侠客踏上了征途...";
        when(aiService.generateContent(anyString(), anyString())).thenReturn(expectedContent);

        // When
        ChapterGenerationResponse response = generationService.generateChapterWithProgress(testRequest);

        // Then
        assertNotNull(response);
        assertNotNull(response.getTaskId());
        assertEquals(expectedContent, response.getContent());
        assertEquals(expectedContent.length(), response.getWordCount());
        assertNull(response.getError());

        verify(webSocketService, times(1)).sendGenerationStarted(anyString(), eq(1));
        verify(webSocketService, times(1)).sendVersionStarted(anyString(), eq(1));
        verify(webSocketService, atLeastOnce()).sendProgressUpdate(anyString(), anyInt(), anyInt(), anyString());
        verify(webSocketService, times(1)).sendGenerationCompleted(anyString(), eq(expectedContent));
    }

    @Test
    void testGenerateChapterWithProgress_Failure() {
        // Given
        when(aiService.generateContent(anyString(), anyString()))
                .thenThrow(new RuntimeException("AI服务不可用"));

        // When
        ChapterGenerationResponse response = generationService.generateChapterWithProgress(testRequest);

        // Then
        assertNotNull(response);
        assertNotNull(response.getTaskId());
        assertNotNull(response.getError());
        assertEquals("AI服务不可用", response.getError());

        verify(webSocketService, times(1)).sendGenerationError(anyString(), anyString());
    }

    @Test
    void testGenerateMultipleVersions_Success() {
        // Given
        String content1 = "版本1的内容...";
        String content2 = "版本2的内容...";
        String content3 = "版本3的内容...";

        when(aiService.generateContent(anyString(), anyString()))
                .thenReturn(content1, content2, content3);

        // When
        ChapterGenerationResponse response = generationService.generateMultipleVersions(testRequest, 3);

        // Then
        assertNotNull(response);
        assertNotNull(response.getTaskId());
        assertNotNull(response.getVersions());
        assertEquals(3, response.getVersions().size());
        assertEquals(3, response.getVersionCount());
        assertNull(response.getError());

        verify(webSocketService, times(1)).sendGenerationStarted(anyString(), eq(3));
        verify(webSocketService, times(3)).sendVersionStarted(anyString(), anyInt());
        verify(webSocketService, times(3)).sendProgressUpdate(anyString(), anyInt(), anyInt(), anyString());
        verify(webSocketService, times(1)).sendGenerationCompleted(anyString(), anyString());
    }

    @Test
    void testContinueWritingWithProgress_Success() {
        // Given
        String existingContent = "故事开始...";
        String context = "这是一个关于成长的故事";
        String expectedContinued = "故事开始... 接下来的情节更加精彩";

        when(aiService.continueWriting(anyString(), anyString(), anyInt()))
                .thenReturn(expectedContinued);

        // When
        ChapterGenerationResponse response = generationService.continueWritingWithProgress(
                existingContent, context, 2000);

        // Then
        assertNotNull(response);
        assertNotNull(response.getTaskId());
        assertEquals(expectedContinued, response.getContent());
        assertEquals(expectedContinued.length(), response.getWordCount());
        assertNull(response.getError());

        verify(webSocketService, times(1)).sendGenerationStarted(anyString(), eq(1));
        verify(webSocketService, times(1)).sendVersionStarted(anyString(), eq(1));
        verify(webSocketService, atLeastOnce()).sendProgressUpdate(anyString(), anyInt(), anyInt(), anyString());
        verify(webSocketService, times(1)).sendGenerationCompleted(anyString(), eq(expectedContinued));
    }

    @Test
    void testContinueWritingWithProgress_Failure() {
        // Given
        when(aiService.continueWriting(anyString(), anyString(), anyInt()))
                .thenThrow(new RuntimeException("续写失败"));

        // When
        ChapterGenerationResponse response = generationService.continueWritingWithProgress(
                "existing content", "context", 1000);

        // Then
        assertNotNull(response);
        assertNotNull(response.getTaskId());
        assertNotNull(response.getError());
        assertEquals("续写失败", response.getError());

        verify(webSocketService, times(1)).sendGenerationError(anyString(), anyString());
    }

    @Test
    void testContextBuildingThroughGeneration() {
        // Given
        testRequest.setCharacters("主角：李明");
        testRequest.setWorldSettings("修仙世界");
        testRequest.setPreviousChapter("前情提要...");

        String expectedContent = "生成的内容包含人物和世界观...";
        when(aiService.generateContent(anyString(), anyString())).thenReturn(expectedContent);

        // When
        ChapterGenerationResponse response = generationService.generateChapterWithProgress(testRequest);

        // Then - indirectly test context building through successful generation
        assertNotNull(response);
        assertEquals(expectedContent, response.getContent());
        verify(aiService, times(1)).generateContent(anyString(), anyString());
    }
}