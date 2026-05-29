package com.novel.ai.service;

import com.novel.ai.exception.BusinessException;
import com.novel.ai.exception.NotFoundException;
import com.novel.ai.mapper.ChapterMapper;
import com.novel.ai.mapper.PlotNodeMapper;
import com.novel.ai.mapper.ProjectMapper;
import com.novel.ai.model.dto.request.PlotNodeCreateRequest;
import com.novel.ai.model.dto.request.PlotNodeUpdateRequest;
import com.novel.ai.model.dto.response.PlotNodeResponse;
import com.novel.ai.model.entity.Chapter;
import com.novel.ai.model.entity.PlotNode;
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

import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.Mockito;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@org.mockito.junit.jupiter.MockitoSettings(strictness = org.mockito.quality.Strictness.LENIENT)
class PlotNodeServiceImplTest {

    @Mock
    private PlotNodeMapper plotNodeMapper;

    @Mock
    private ProjectMapper projectMapper;

    @Mock
    private ChapterMapper chapterMapper;

    @InjectMocks
    private PlotNodeServiceImpl plotNodeService;

    private PlotNode testPlotNode;
    private Project testProject;
    private Chapter testChapter;
    private PlotNodeCreateRequest createRequest;
    private PlotNodeUpdateRequest updateRequest;
    private final Integer TEST_USER_ID = 1;
    private final Integer TEST_PROJECT_ID = 1;
    private final Integer TEST_PLOT_NODE_ID = 1;
    private final Integer TEST_CHAPTER_ID = 1;

    @BeforeEach
    void setUp() {
        // 创建测试项目
        testProject = new Project();
        testProject.setId(TEST_PROJECT_ID);
        testProject.setUserId(TEST_USER_ID);
        testProject.setTitle("测试项目");

        // 创建测试章节
        testChapter = new Chapter();
        testChapter.setId(TEST_CHAPTER_ID);
        testChapter.setProjectId(TEST_PROJECT_ID);
        testChapter.setTitle("测试章节");

        // 创建测试情节节点
        testPlotNode = new PlotNode();
        testPlotNode.setId(TEST_PLOT_NODE_ID);
        testPlotNode.setProjectId(TEST_PROJECT_ID);
        testPlotNode.setTitle("初遇");
        testPlotNode.setDescription("主角和反派的第一次相遇");
        testPlotNode.setPlotType("meeting");
        testPlotNode.setImportance("main");
        testPlotNode.setChapterId(TEST_CHAPTER_ID);
        testPlotNode.setCreatedAt(LocalDateTime.now());
        testPlotNode.setUpdatedAt(LocalDateTime.now());

        // 创建创建请求
        createRequest = new PlotNodeCreateRequest();
        createRequest.setProjectId(TEST_PROJECT_ID);
        createRequest.setTitle("冲突");
        createRequest.setDescription("主角和反派的激烈冲突");
        createRequest.setPlotType("conflict");
        createRequest.setImportance("main");
        createRequest.setChapterId(TEST_CHAPTER_ID);

        // 创建更新请求
        updateRequest = new PlotNodeUpdateRequest();
        updateRequest.setTitle("和解");
        updateRequest.setPlotType("reconciliation");
        updateRequest.setImportance("main");
    }

    @Test
    void testCreatePlotNode_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(chapterMapper.findById(TEST_CHAPTER_ID)).thenReturn(testChapter);
        when(plotNodeMapper.findByProjectIdAndTitle(TEST_PROJECT_ID, createRequest.getTitle())).thenReturn(null);
        when(plotNodeMapper.insert(any(PlotNode.class))).thenReturn(1);

        // When
        PlotNodeResponse response = plotNodeService.createPlotNode(TEST_USER_ID, createRequest);

        // Then
        assertNotNull(response);
        verify(plotNodeMapper, times(1)).insert(any(PlotNode.class));
    }

    @Test
    void testCreatePlotNode_ProjectNotFound() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            plotNodeService.createPlotNode(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testCreatePlotNode_TitleExists() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(plotNodeMapper.findByProjectIdAndTitle(TEST_PROJECT_ID, createRequest.getTitle())).thenReturn(testPlotNode);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            plotNodeService.createPlotNode(TEST_USER_ID, createRequest);
        });

        // Verify that insert was never called
        verify(plotNodeMapper, never()).insert(any(PlotNode.class));
    }

    @Test
    void testCreatePlotNode_InvalidPlotType() {
        // Given
        createRequest.setPlotType("invalid_type");
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(plotNodeMapper.findByProjectIdAndTitle(TEST_PROJECT_ID, createRequest.getTitle())).thenReturn(null);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            plotNodeService.createPlotNode(TEST_USER_ID, createRequest);
        });

        // Verify that insert was never called
        verify(plotNodeMapper, never()).insert(any(PlotNode.class));
    }

    @Test
    void testGetPlotNodeById_Success() {
        // Given
        when(plotNodeMapper.findById(TEST_PLOT_NODE_ID)).thenReturn(testPlotNode);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When
        PlotNodeResponse response = plotNodeService.getPlotNodeById(TEST_PLOT_NODE_ID, TEST_USER_ID);

        // Then
        assertNotNull(response);
        assertEquals(TEST_PLOT_NODE_ID, response.getId());
        assertEquals("初遇", response.getTitle());
        verify(plotNodeMapper, times(1)).findById(TEST_PLOT_NODE_ID);
    }

    @Test
    void testGetPlotNodesByProjectId_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        List<PlotNode> plotNodes = Arrays.asList(testPlotNode);
        when(plotNodeMapper.findByProjectId(TEST_PROJECT_ID)).thenReturn(plotNodes);

        // When
        List<PlotNodeResponse> responses = plotNodeService.getPlotNodesByProjectId(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals(TEST_PLOT_NODE_ID, responses.get(0).getId());
        verify(plotNodeMapper, times(1)).findByProjectId(TEST_PROJECT_ID);
    }

    @Test
    void testGetMainPlots_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        testPlotNode.setImportance("main");
        List<PlotNode> mainPlots = Arrays.asList(testPlotNode);
        when(plotNodeMapper.findMainPlots(TEST_PROJECT_ID)).thenReturn(mainPlots);

        // When
        List<PlotNodeResponse> responses = plotNodeService.getMainPlots(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals("main", responses.get(0).getImportance());
        verify(plotNodeMapper, times(1)).findMainPlots(TEST_PROJECT_ID);
    }

    @Test
    void testGetClimaxPlots_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        testPlotNode.setPlotType("climax");
        List<PlotNode> climaxPlots = Arrays.asList(testPlotNode);
        when(plotNodeMapper.findClimaxPlots(TEST_PROJECT_ID)).thenReturn(climaxPlots);

        // When
        List<PlotNodeResponse> responses = plotNodeService.getClimaxPlots(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals("climax", responses.get(0).getPlotType());
        verify(plotNodeMapper, times(1)).findClimaxPlots(TEST_PROJECT_ID);
    }

    @Test
    void testUpdatePlotNode_Success() {
        // Given
        when(plotNodeMapper.findById(TEST_PLOT_NODE_ID)).thenReturn(testPlotNode);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(plotNodeMapper.countByTitleExcludingId(anyInt(), anyString(), anyInt())).thenReturn(0);
        when(plotNodeMapper.update(any(PlotNode.class))).thenReturn(1);

        // When
        PlotNodeResponse response = plotNodeService.updatePlotNode(TEST_PLOT_NODE_ID, TEST_USER_ID, updateRequest);

        // Then
        assertNotNull(response);
        verify(plotNodeMapper, times(1)).update(any(PlotNode.class));
    }

    @Test
    void testUpdatePlotNode_NotFound() {
        // Given
        when(plotNodeMapper.findById(TEST_PLOT_NODE_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            plotNodeService.updatePlotNode(TEST_PLOT_NODE_ID, TEST_USER_ID, updateRequest);
        });
    }

    @Test
    void testDeletePlotNode_Success() {
        // Given
        when(plotNodeMapper.findById(TEST_PLOT_NODE_ID)).thenReturn(testPlotNode);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(plotNodeMapper.delete(TEST_PLOT_NODE_ID)).thenReturn(1);

        // When
        plotNodeService.deletePlotNode(TEST_PLOT_NODE_ID, TEST_USER_ID);

        // Then
        verify(plotNodeMapper, times(1)).delete(TEST_PLOT_NODE_ID);
    }

    @Test
    void testDeletePlotNode_NotFound() {
        // Given
        when(plotNodeMapper.findById(TEST_PLOT_NODE_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            plotNodeService.deletePlotNode(TEST_PLOT_NODE_ID, TEST_USER_ID);
        });
    }

    @Test
    void testCountPlotNodes_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(plotNodeMapper.countByProjectId(TEST_PROJECT_ID)).thenReturn(12);

        // When
        int count = plotNodeService.countPlotNodes(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertEquals(12, count);
        verify(plotNodeMapper, times(1)).countByProjectId(TEST_PROJECT_ID);
    }
}