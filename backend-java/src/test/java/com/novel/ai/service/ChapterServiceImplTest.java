package com.novel.ai.service;

import com.novel.ai.exception.BusinessException;
import com.novel.ai.exception.NotFoundException;
import com.novel.ai.mapper.ChapterMapper;
import com.novel.ai.mapper.ProjectMapper;
import com.novel.ai.model.dto.request.ChapterCreateRequest;
import com.novel.ai.model.dto.request.ChapterUpdateRequest;
import com.novel.ai.model.dto.response.ChapterResponse;
import com.novel.ai.model.entity.Chapter;
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
class ChapterServiceImplTest {

    @Mock
    private ChapterMapper chapterMapper;

    @Mock
    private ProjectMapper projectMapper;

    @InjectMocks
    private ChapterServiceImpl chapterService;

    private Chapter testChapter;
    private Project testProject;
    private ChapterCreateRequest createRequest;
    private ChapterUpdateRequest updateRequest;
    private final Integer TEST_USER_ID = 1;
    private final Integer TEST_PROJECT_ID = 1;
    private final Integer TEST_CHAPTER_ID = 1;

    @BeforeEach
    void setUp() {
        // 创建测试项目
        testProject = new Project();
        testProject.setId(TEST_PROJECT_ID);
        testProject.setUserId(TEST_USER_ID);
        testProject.setTitle("测试小说");

        // 创建测试章节
        testChapter = new Chapter();
        testChapter.setId(TEST_CHAPTER_ID);
        testChapter.setProjectId(TEST_PROJECT_ID);
        testChapter.setChapterNumber(1);
        testChapter.setTitle("第一章");
        testChapter.setContent("这是第一章的内容");
        testChapter.setOutline("第一章大纲");
        testChapter.setSummary("第一章摘要");
        testChapter.setStatus("draft");
        testChapter.setWordCount(8);
        testChapter.setVersion(1);
        testChapter.setCreatedAt(LocalDateTime.now());
        testChapter.setUpdatedAt(LocalDateTime.now());

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
    void testCreateChapter_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(chapterMapper.countByProjectIdAndChapterNumber(TEST_PROJECT_ID, 1)).thenReturn(0);
        when(chapterMapper.insert(any(Chapter.class))).thenReturn(1);

        // When
        ChapterResponse response = chapterService.createChapter(TEST_USER_ID, createRequest);

        // Then
        assertNotNull(response);
        verify(projectMapper, times(1)).findById(TEST_PROJECT_ID);
        verify(chapterMapper, times(1)).countByProjectIdAndChapterNumber(TEST_PROJECT_ID, 1);
        verify(chapterMapper, times(1)).insert(any(Chapter.class));
    }

    @Test
    void testCreateChapter_ProjectNotFound() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            chapterService.createChapter(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testCreateChapter_Unauthorized() {
        // Given
        testProject.setUserId(999); // Different user
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            chapterService.createChapter(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testCreateChapter_DuplicateChapterNumber() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(chapterMapper.countByProjectIdAndChapterNumber(TEST_PROJECT_ID, 1)).thenReturn(1);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            chapterService.createChapter(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testGetChapterById_Success() {
        // Given
        when(chapterMapper.findById(TEST_CHAPTER_ID)).thenReturn(testChapter);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When
        ChapterResponse response = chapterService.getChapterById(TEST_CHAPTER_ID, TEST_USER_ID);

        // Then
        assertNotNull(response);
        assertEquals(TEST_CHAPTER_ID, response.getId());
        assertEquals("第一章", response.getTitle());
        verify(chapterMapper, times(1)).findById(TEST_CHAPTER_ID);
    }

    @Test
    void testGetChapterById_NotFound() {
        // Given
        when(chapterMapper.findById(TEST_CHAPTER_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            chapterService.getChapterById(TEST_CHAPTER_ID, TEST_USER_ID);
        });
    }

    @Test
    void testGetChapterById_Unauthorized() {
        // Given
        testProject.setUserId(999); // Different user
        when(chapterMapper.findById(TEST_CHAPTER_ID)).thenReturn(testChapter);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            chapterService.getChapterById(TEST_CHAPTER_ID, TEST_USER_ID);
        });
    }

    @Test
    void testGetChaptersByProjectId_Success() {
        // Given
        List<Chapter> chapters = Arrays.asList(testChapter);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(chapterMapper.findByProjectId(TEST_PROJECT_ID)).thenReturn(chapters);

        // When
        List<ChapterResponse> responses = chapterService.getChaptersByProjectId(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertNull(responses.get(0).getContent()); // List view should not include content
        verify(projectMapper, times(1)).findById(TEST_PROJECT_ID);
        verify(chapterMapper, times(1)).findByProjectId(TEST_PROJECT_ID);
    }

    @Test
    void testGetChaptersByProjectId_Empty() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(chapterMapper.findByProjectId(TEST_PROJECT_ID)).thenReturn(Collections.emptyList());

        // When
        List<ChapterResponse> responses = chapterService.getChaptersByProjectId(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertTrue(responses.isEmpty());
    }

    @Test
    void testUpdateChapter_Success() {
        // Given
        when(chapterMapper.findById(TEST_CHAPTER_ID)).thenReturn(testChapter);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(chapterMapper.update(any(Chapter.class))).thenReturn(1);

        // When
        ChapterResponse response = chapterService.updateChapter(TEST_CHAPTER_ID, TEST_USER_ID, updateRequest);

        // Then
        assertNotNull(response);
        verify(chapterMapper, times(1)).findById(TEST_CHAPTER_ID);
        verify(chapterMapper, times(1)).update(any(Chapter.class));
    }

    @Test
    void testUpdateChapter_NotFound() {
        // Given
        when(chapterMapper.findById(TEST_CHAPTER_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            chapterService.updateChapter(TEST_CHAPTER_ID, TEST_USER_ID, updateRequest);
        });
    }

    @Test
    void testUpdateChapter_Unauthorized() {
        // Given
        testProject.setUserId(999); // Different user
        when(chapterMapper.findById(TEST_CHAPTER_ID)).thenReturn(testChapter);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            chapterService.updateChapter(TEST_CHAPTER_ID, TEST_USER_ID, updateRequest);
        });
    }

    @Test
    void testDeleteChapter_Success() {
        // Given
        when(chapterMapper.findById(TEST_CHAPTER_ID)).thenReturn(testChapter);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(chapterMapper.delete(TEST_CHAPTER_ID)).thenReturn(1);

        // When
        chapterService.deleteChapter(TEST_CHAPTER_ID, TEST_USER_ID);

        // Then
        verify(chapterMapper, times(1)).findById(TEST_CHAPTER_ID);
        verify(chapterMapper, times(1)).delete(TEST_CHAPTER_ID);
    }

    @Test
    void testDeleteChapter_NotFound() {
        // Given
        when(chapterMapper.findById(TEST_CHAPTER_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            chapterService.deleteChapter(TEST_CHAPTER_ID, TEST_USER_ID);
        });
    }

    @Test
    void testDeleteChapter_Unauthorized() {
        // Given
        testProject.setUserId(999); // Different user
        when(chapterMapper.findById(TEST_CHAPTER_ID)).thenReturn(testChapter);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            chapterService.deleteChapter(TEST_CHAPTER_ID, TEST_USER_ID);
        });
    }

    @Test
    void testGetNextChapterNumber_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(chapterMapper.findMaxChapterNumberByProjectId(TEST_PROJECT_ID)).thenReturn(3);

        // When
        Integer nextNumber = chapterService.getNextChapterNumber(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertEquals(4, nextNumber);
        verify(chapterMapper, times(1)).findMaxChapterNumberByProjectId(TEST_PROJECT_ID);
    }

    @Test
    void testGetNextChapterNumber_FirstChapter() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(chapterMapper.findMaxChapterNumberByProjectId(TEST_PROJECT_ID)).thenReturn(null);

        // When
        Integer nextNumber = chapterService.getNextChapterNumber(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertEquals(1, nextNumber);
    }
}