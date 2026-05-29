package com.novel.ai.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.novel.ai.model.dto.request.ProjectCreateRequest;
import com.novel.ai.model.dto.request.ProjectUpdateRequest;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.model.dto.response.ProjectResponse;
import com.novel.ai.service.ProjectService;
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
class ProjectControllerTest {

    private MockMvc mockMvc;

    @Mock
    private ProjectService projectService;

    @InjectMocks
    private ProjectController projectController;

    private ObjectMapper objectMapper;

    private ProjectResponse testProjectResponse;
    private ProjectCreateRequest createRequest;
    private ProjectUpdateRequest updateRequest;
    private final Integer TEST_USER_ID = 1;
    private final Integer TEST_PROJECT_ID = 1;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.standaloneSetup(projectController).build();
        objectMapper = new ObjectMapper();
        // 创建测试项目响应
        testProjectResponse = new ProjectResponse();
        testProjectResponse.setId(TEST_PROJECT_ID);
        testProjectResponse.setUserId(TEST_USER_ID);
        testProjectResponse.setTitle("测试小说");
        testProjectResponse.setAuthor("测试作者");
        testProjectResponse.setGenre("玄幻");
        testProjectResponse.setSummary("这是一个测试小说");
        testProjectResponse.setStatus("draft");
        testProjectResponse.setStyleIntensity(70);
        testProjectResponse.setTargetWordsPerChapter(2000);
        testProjectResponse.setTotalWords(0);
        testProjectResponse.setTotalChapters(0);
        testProjectResponse.setCompletionRate(0);
        testProjectResponse.setCreatedAt(LocalDateTime.now());
        testProjectResponse.setUpdatedAt(LocalDateTime.now());

        // 创建创建请求
        createRequest = new ProjectCreateRequest();
        createRequest.setTitle("测试小说");
        createRequest.setAuthor("测试作者");
        createRequest.setGenre("玄幻");
        createRequest.setSummary("这是一个测试小说");
        createRequest.setStyleIntensity(70);
        createRequest.setTargetWordsPerChapter(2000);

        // 创建更新请求
        updateRequest = new ProjectUpdateRequest();
        updateRequest.setTitle("更新后的小说");
        updateRequest.setAuthor("更新后的作者");
        updateRequest.setGenre("修仙");
        updateRequest.setSummary("这是更新后的小说");
        updateRequest.setStatus("writing");
    }

    @Test
    void testCreateProject_Success() throws Exception {
        // Given
        when(projectService.createProject(anyInt(), any(ProjectCreateRequest.class)))
                .thenReturn(testProjectResponse);

        // When & Then
        mockMvc.perform(post("/api/projects/create")
                        .requestAttr("userId", TEST_USER_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("项目创建成功"))
                .andExpect(jsonPath("$.data.id").value(TEST_PROJECT_ID))
                .andExpect(jsonPath("$.data.title").value("测试小说"));
    }

    @Test
    void testGetProjectDetail_Success() throws Exception {
        // Given
        when(projectService.getProjectById(TEST_PROJECT_ID, TEST_USER_ID))
                .thenReturn(testProjectResponse);

        // When & Then
        mockMvc.perform(get("/api/projects/detail/{id}", TEST_PROJECT_ID)
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.id").value(TEST_PROJECT_ID))
                .andExpect(jsonPath("$.data.title").value("测试小说"));
    }

    @Test
    void testGetProjectList_Success() throws Exception {
        // Given
        List<ProjectResponse> projects = Arrays.asList(testProjectResponse);
        when(projectService.getProjectsByUserId(TEST_USER_ID)).thenReturn(projects);

        // When & Then
        mockMvc.perform(get("/api/projects/list")
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.length()").value(1))
                .andExpect(jsonPath("$.data[0].id").value(TEST_PROJECT_ID));
    }

    @Test
    void testGetProjectList_Empty() throws Exception {
        // Given
        when(projectService.getProjectsByUserId(TEST_USER_ID)).thenReturn(Collections.emptyList());

        // When & Then
        mockMvc.perform(get("/api/projects/list")
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.length()").value(0));
    }

    @Test
    void testGetProjectListByStatus_Success() throws Exception {
        // Given
        String status = "draft";
        List<ProjectResponse> projects = Arrays.asList(testProjectResponse);
        when(projectService.getProjectsByUserIdAndStatus(TEST_USER_ID, status)).thenReturn(projects);

        // When & Then
        mockMvc.perform(get("/api/projects/list/{status}", status)
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.length()").value(1))
                .andExpect(jsonPath("$.data[0].status").value(status));
    }

    @Test
    void testUpdateProject_Success() throws Exception {
        // Given
        ProjectResponse updatedResponse = new ProjectResponse();
        updatedResponse.setId(TEST_PROJECT_ID);
        updatedResponse.setTitle("更新后的小说");
        updatedResponse.setAuthor("更新后的作者");
        updatedResponse.setGenre("修仙");
        updatedResponse.setSummary("这是更新后的小说");
        updatedResponse.setStatus("writing");

        when(projectService.updateProject(anyInt(), anyInt(), any(ProjectUpdateRequest.class)))
                .thenReturn(updatedResponse);

        // When & Then
        mockMvc.perform(post("/api/projects/update/{id}", TEST_PROJECT_ID)
                        .requestAttr("userId", TEST_USER_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("项目更新成功"))
                .andExpect(jsonPath("$.data.title").value("更新后的小说"))
                .andExpect(jsonPath("$.data.status").value("writing"));
    }

    @Test
    void testDeleteProject_Success() throws Exception {
        // Given - void method doesn't need return value mocking
        org.mockito.Mockito.doNothing().when(projectService).deleteProject(TEST_PROJECT_ID, TEST_USER_ID);

        // When & Then
        mockMvc.perform(post("/api/projects/del/{id}", TEST_PROJECT_ID)
                        .requestAttr("userId", TEST_USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("操作成功"));
    }

    @Test
    void testCreateProject_ValidationFailed_EmptyTitle() throws Exception {
        // Given
        createRequest.setTitle(""); // Empty title should fail validation

        // When & Then
        mockMvc.perform(post("/api/projects/create")
                        .requestAttr("userId", TEST_USER_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void testCreateProject_ValidationFailed_TitleTooLong() throws Exception {
        // Given
        createRequest.setTitle("a".repeat(201)); // Title too long (max 200 characters)

        // When & Then
        mockMvc.perform(post("/api/projects/create")
                        .requestAttr("userId", TEST_USER_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void testUpdateProject_ValidationFailed_EmptyAuthor() throws Exception {
        // Given
        updateRequest.setAuthor(""); // Empty author should fail validation

        // When & Then
        mockMvc.perform(post("/api/projects/update/{id}", TEST_PROJECT_ID)
                        .requestAttr("userId", TEST_USER_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateRequest)))
                .andExpect(status().isBadRequest());
    }
}