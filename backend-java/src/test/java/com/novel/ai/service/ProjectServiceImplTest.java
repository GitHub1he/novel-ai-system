package com.novel.ai.service;

import com.novel.ai.exception.BusinessException;
import com.novel.ai.exception.NotFoundException;
import com.novel.ai.mapper.ProjectMapper;
import com.novel.ai.model.dto.request.ProjectCreateRequest;
import com.novel.ai.model.dto.request.ProjectUpdateRequest;
import com.novel.ai.model.dto.response.ProjectResponse;
import com.novel.ai.model.entity.Project;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ProjectServiceImplTest {

    @Mock
    private ProjectMapper projectMapper;

    @InjectMocks
    private ProjectServiceImpl projectService;

    private Project testProject;
    private ProjectCreateRequest createRequest;
    private ProjectUpdateRequest updateRequest;
    private final Integer TEST_USER_ID = 1;
    private final Integer TEST_PROJECT_ID = 1;

    @BeforeEach
    void setUp() {
        // 创建测试项目
        testProject = new Project();
        testProject.setId(TEST_PROJECT_ID);
        testProject.setUserId(TEST_USER_ID);
        testProject.setTitle("测试小说");
        testProject.setAuthor("测试作者");
        testProject.setGenre("玄幻");
        testProject.setSummary("这是一个测试小说");
        testProject.setStatus("draft");
        testProject.setStyleIntensity(70);
        testProject.setTargetWordsPerChapter(2000);
        testProject.setTotalWords(0);
        testProject.setTotalChapters(0);
        testProject.setCompletionRate(0);
        testProject.setCreatedAt(LocalDateTime.now());
        testProject.setUpdatedAt(LocalDateTime.now());

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
    void testCreateProject_Success() {
        // Given
        when(projectMapper.insert(any(Project.class))).thenReturn(1);

        // When
        ProjectResponse response = projectService.createProject(TEST_USER_ID, createRequest);

        // Then
        assertNotNull(response);
        verify(projectMapper, times(1)).insert(any(Project.class));
    }

    @Test
    void testCreateProject_Failure() {
        // Given
        when(projectMapper.insert(any(Project.class))).thenReturn(0);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            projectService.createProject(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testGetProjectById_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When
        ProjectResponse response = projectService.getProjectById(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(response);
        assertEquals(TEST_PROJECT_ID, response.getId());
        assertEquals(TEST_USER_ID, response.getUserId());
        assertEquals("测试小说", response.getTitle());
        verify(projectMapper, times(1)).findById(TEST_PROJECT_ID);
    }

    @Test
    void testGetProjectById_NotFound() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            projectService.getProjectById(TEST_PROJECT_ID, TEST_USER_ID);
        });
    }

    @Test
    void testGetProjectById_Unauthorized() {
        // Given
        Integer differentUserId = 999;
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            projectService.getProjectById(TEST_PROJECT_ID, differentUserId);
        });
    }

    @Test
    void testGetProjectsByUserId_Success() {
        // Given
        List<Project> projects = Arrays.asList(testProject);
        when(projectMapper.findByUserId(TEST_USER_ID)).thenReturn(projects);

        // When
        List<ProjectResponse> responses = projectService.getProjectsByUserId(TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals(TEST_PROJECT_ID, responses.get(0).getId());
        verify(projectMapper, times(1)).findByUserId(TEST_USER_ID);
    }

    @Test
    void testGetProjectsByUserId_Empty() {
        // Given
        when(projectMapper.findByUserId(TEST_USER_ID)).thenReturn(Collections.emptyList());

        // When
        List<ProjectResponse> responses = projectService.getProjectsByUserId(TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertTrue(responses.isEmpty());
    }

    @Test
    void testGetProjectsByUserIdAndStatus_Success() {
        // Given
        String status = "draft";
        List<Project> projects = Arrays.asList(testProject);
        when(projectMapper.findByUserIdAndStatus(TEST_USER_ID, status)).thenReturn(projects);

        // When
        List<ProjectResponse> responses = projectService.getProjectsByUserIdAndStatus(TEST_USER_ID, status);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals(status, responses.get(0).getStatus());
        verify(projectMapper, times(1)).findByUserIdAndStatus(TEST_USER_ID, status);
    }

    @Test
    void testUpdateProject_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(projectMapper.update(any(Project.class))).thenReturn(1);

        // When
        ProjectResponse response = projectService.updateProject(TEST_PROJECT_ID, TEST_USER_ID, updateRequest);

        // Then
        assertNotNull(response);
        verify(projectMapper, times(1)).findById(TEST_PROJECT_ID);
        verify(projectMapper, times(1)).update(any(Project.class));
    }

    @Test
    void testUpdateProject_NotFound() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            projectService.updateProject(TEST_PROJECT_ID, TEST_USER_ID, updateRequest);
        });
    }

    @Test
    void testUpdateProject_Unauthorized() {
        // Given
        Integer differentUserId = 999;
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            projectService.updateProject(TEST_PROJECT_ID, differentUserId, updateRequest);
        });
    }

    @Test
    void testUpdateProject_Failure() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(projectMapper.update(any(Project.class))).thenReturn(0);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            projectService.updateProject(TEST_PROJECT_ID, TEST_USER_ID, updateRequest);
        });
    }

    @Test
    void testDeleteProject_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(projectMapper.delete(TEST_PROJECT_ID)).thenReturn(1);

        // When
        projectService.deleteProject(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        verify(projectMapper, times(1)).findById(TEST_PROJECT_ID);
        verify(projectMapper, times(1)).delete(TEST_PROJECT_ID);
    }

    @Test
    void testDeleteProject_NotFound() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            projectService.deleteProject(TEST_PROJECT_ID, TEST_USER_ID);
        });
    }

    @Test
    void testDeleteProject_Unauthorized() {
        // Given
        Integer differentUserId = 999;
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            projectService.deleteProject(TEST_PROJECT_ID, differentUserId);
        });
    }

    @Test
    void testDeleteProject_Failure() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(projectMapper.delete(TEST_PROJECT_ID)).thenReturn(0);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            projectService.deleteProject(TEST_PROJECT_ID, TEST_USER_ID);
        });
    }

    @Test
    void testUpdateProjectStatistics_Success() {
        // Given
        Integer totalWords = 10000;
        Integer totalChapters = 5;
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(projectMapper.updateStatistics(any(Project.class))).thenReturn(1);

        // When
        projectService.updateProjectStatistics(TEST_PROJECT_ID, totalWords, totalChapters);

        // Then
        verify(projectMapper, times(1)).findById(TEST_PROJECT_ID);
        verify(projectMapper, times(1)).updateStatistics(any(Project.class));
    }

    @Test
    void testUpdateProjectStatistics_NotFound() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            projectService.updateProjectStatistics(TEST_PROJECT_ID, 10000, 5);
        });
    }
}