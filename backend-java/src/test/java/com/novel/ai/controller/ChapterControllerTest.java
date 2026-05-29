package com.novel.ai.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.novel.ai.model.dto.request.ChapterCreateRequest;
import com.novel.ai.model.dto.request.ChapterUpdateRequest;
import com.novel.ai.model.dto.response.ChapterResponse;
import com.novel.ai.service.ChapterService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
class ChapterControllerTest {

    private MockMvc mockMvc;

    @Mock
    private ChapterService chapterService;

    @InjectMocks
    private ChapterController chapterController;

    private ObjectMapper objectMapper;

    private ChapterResponse testChapterResponse;
    private ChapterCreateRequest createRequest;
    private ChapterUpdateRequest updateRequest;
    private final Integer TEST_USER_ID = 1;
    private final Integer TEST_PROJECT_ID = 1;
    private final Integer TEST_CHAPTER_ID = 1;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.standaloneSetup(chapterController).build();
        objectMapper = new ObjectMapper();

        // 创建测试章节响应
        testChapterResponse = new ChapterResponse();
        testChapterResponse.setId(TEST_CHAPTER_ID);
        testChapterResponse.setProjectId(TEST_PROJECT_ID);
        testChapterResponse.setChapterNumber(1);
        testChapterResponse.setTitle("第一章");
        testChapterResponse.setContent("这是第一章的内容");
        testChapterResponse.setOutline("第一章大纲");
        testChapterResponse.setSummary("第一章摘要");
        testChapterResponse.setStatus("draft");
        testChapterResponse.setWordCount(8);
        testChapterResponse.setVersion(1);
        testChapterResponse.setCreatedAt(LocalDateTime.now());
        testChapterResponse.setUpdatedAt(LocalDateTime.now());

        // 创建创建请求
        createRequest = new ChapterCreateRequest();
        createRequest.setProjectId(TEST_PROJECT_ID);
        createRequest.setChapterNumber(1);
        createRequest.setTitle("第一章");
        createRequest.setOutline("第一章大纲");
        createRequest.setSummary("第一章摘要");

        // 创建更新请求
        updateRequest = new ChapterUpdateRequest();
        updateRequest.setTitle("更新后的第一章");
        updateRequest.setContent("更新后的内容");
        updateRequest.setOutline("更新后的大纲");
        updateRequest.setStatus("revising");
    }

    @Test
    void testCreateChapter_Success() throws Exception {
        // Given
        when(chapterService.createChapter(anyInt(), any(ChapterCreateRequest.class)))
                .thenReturn(testChapterResponse);

        // When & Then
        mockMvc.perform(post("/api/chapters/")
                        .requestAttr("userId", TEST_USER_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("创建成功"))
                .andExpect(jsonPath("$.data.id").value(TEST_CHAPTER_ID))
                .andExpect(jsonPath("$.data.title").value("第一章"));
    }

    @Test
    void testGetChapterDetail_Success() throws Exception {
        // Given
        when(chapterService.getChapterById(TEST_CHAPTER_ID, TEST_USER_ID))
                .thenReturn(testChapterResponse);

        // When & Then
        mockMvc.perform(get("/api/chapters/{chapter_id}", TEST_CHAPTER_ID)
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("获取成功"))
                .andExpect(jsonPath("$.data.id").value(TEST_CHAPTER_ID))
                .andExpect(jsonPath("$.data.title").value("第一章"));
    }

    @Test
    void testGetChapterList_Success() throws Exception {
        // Given
        List<ChapterResponse> chapters = Arrays.asList(testChapterResponse);
        when(chapterService.getChaptersByProjectId(TEST_PROJECT_ID, TEST_USER_ID)).thenReturn(chapters);

        // When & Then
        mockMvc.perform(get("/api/chapters/list/{project_id}", TEST_PROJECT_ID)
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.length()").value(1))
                .andExpect(jsonPath("$.data[0].id").value(TEST_CHAPTER_ID));
    }

    @Test
    void testGetChapterList_Empty() throws Exception {
        // Given
        when(chapterService.getChaptersByProjectId(TEST_PROJECT_ID, TEST_USER_ID))
                .thenReturn(Collections.emptyList());

        // When & Then
        mockMvc.perform(get("/api/chapters/list/{project_id}", TEST_PROJECT_ID)
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.length()").value(0));
    }

    @Test
    void testGetChapterListByStatus_Success() throws Exception {
        // Given
        String status = "draft";
        List<ChapterResponse> chapters = Arrays.asList(testChapterResponse);
        when(chapterService.getChaptersByProjectIdAndStatus(TEST_PROJECT_ID, status, TEST_USER_ID))
                .thenReturn(chapters);

        // When & Then
        mockMvc.perform(get("/api/chapters/list/{project_id}/{status}", TEST_PROJECT_ID, status)
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.length()").value(1))
                .andExpect(jsonPath("$.data[0].status").value(status));
    }

    @Test
    void testUpdateChapter_Success() throws Exception {
        // Given
        ChapterResponse updatedResponse = new ChapterResponse();
        updatedResponse.setId(TEST_CHAPTER_ID);
        updatedResponse.setTitle("更新后的第一章");
        updatedResponse.setContent("更新后的内容");
        updatedResponse.setStatus("revising");

        when(chapterService.updateChapter(anyInt(), anyInt(), any(ChapterUpdateRequest.class)))
                .thenReturn(updatedResponse);

        // When & Then
        mockMvc.perform(put("/api/chapters/{chapter_id}", TEST_CHAPTER_ID)
                        .requestAttr("userId", TEST_USER_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("更新成功"))
                .andExpect(jsonPath("$.data.title").value("更新后的第一章"))
                .andExpect(jsonPath("$.data.status").value("revising"));
    }

    @Test
    void testDeleteChapter_Success() throws Exception {
        // Given - void method doesn't need return value mocking
        org.mockito.Mockito.doNothing().when(chapterService).deleteChapter(TEST_CHAPTER_ID, TEST_USER_ID);

        // When & Then
        mockMvc.perform(delete("/api/chapters/{chapter_id}", TEST_CHAPTER_ID)
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("操作成功"));
    }

    @Test
    void testGetNextChapterNumber_Success() throws Exception {
        // Given
        Integer nextNumber = 5;
        when(chapterService.getNextChapterNumber(TEST_PROJECT_ID, TEST_USER_ID)).thenReturn(nextNumber);

        // When & Then
        mockMvc.perform(get("/api/chapters/next-number/{project_id}", TEST_PROJECT_ID)
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data").value(5));
    }

    @Test
    void testCreateChapter_ValidationFailed_EmptyTitle() throws Exception {
        // Given
        createRequest.setTitle(""); // Empty title should fail validation

        // When & Then
        mockMvc.perform(post("/api/chapters/")
                        .requestAttr("userId", TEST_USER_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void testCreateChapter_ValidationFailed_TitleTooLong() throws Exception {
        // Given
        createRequest.setTitle("a".repeat(201)); // Title too long (max 200 characters)

        // When & Then
        mockMvc.perform(post("/api/chapters/")
                        .requestAttr("userId", TEST_USER_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void testUpdateChapter_ValidationFailed_EmptyTitle() throws Exception {
        // Given
        updateRequest.setTitle(""); // Empty title should fail validation

        // When & Then
        mockMvc.perform(put("/api/chapters/{chapter_id}", TEST_CHAPTER_ID)
                        .requestAttr("userId", TEST_USER_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateRequest)))
                .andExpect(status().isBadRequest());
    }
}