package com.novel.ai.service;

import com.novel.ai.exception.BusinessException;
import com.novel.ai.exception.NotFoundException;
import com.novel.ai.mapper.ProjectMapper;
import com.novel.ai.mapper.WorldSettingMapper;
import com.novel.ai.model.dto.request.WorldSettingCreateRequest;
import com.novel.ai.model.dto.request.WorldSettingUpdateRequest;
import com.novel.ai.model.dto.response.WorldSettingResponse;
import com.novel.ai.model.entity.Project;
import com.novel.ai.model.entity.WorldSetting;
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
class WorldSettingServiceImplTest {

    @Mock
    private WorldSettingMapper worldSettingMapper;

    @Mock
    private ProjectMapper projectMapper;

    @InjectMocks
    private WorldSettingServiceImpl worldSettingService;

    private WorldSetting testWorldSetting;
    private Project testProject;
    private WorldSettingCreateRequest createRequest;
    private WorldSettingUpdateRequest updateRequest;
    private final Integer TEST_USER_ID = 1;
    private final Integer TEST_PROJECT_ID = 1;
    private final Integer TEST_WORLD_SETTING_ID = 1;

    @BeforeEach
    void setUp() {
        // 创建测试项目
        testProject = new Project();
        testProject.setId(TEST_PROJECT_ID);
        testProject.setUserId(TEST_USER_ID);
        testProject.setTitle("测试项目");

        // 创建测试世界观设定
        testWorldSetting = new WorldSetting();
        testWorldSetting.setId(TEST_WORLD_SETTING_ID);
        testWorldSetting.setProjectId(TEST_PROJECT_ID);
        testWorldSetting.setName("魔法体系");
        testWorldSetting.setSettingType("rule");
        testWorldSetting.setDescription("基本的魔法体系设定");
        testWorldSetting.setIsCoreRule(1);
        testWorldSetting.setCreatedAt(LocalDateTime.now());
        testWorldSetting.setUpdatedAt(LocalDateTime.now());

        // 创建创建请求
        createRequest = new WorldSettingCreateRequest();
        createRequest.setProjectId(TEST_PROJECT_ID);
        createRequest.setName("科技体系");
        createRequest.setSettingType("rule");
        createRequest.setDescription("未来科技设定");
        createRequest.setIsCoreRule(0);

        // 创建更新请求
        updateRequest = new WorldSettingUpdateRequest();
        updateRequest.setName("修仙体系");
        updateRequest.setSettingType("rule");
        updateRequest.setDescription("修仙世界观设定");
    }

    @Test
    void testCreateWorldSetting_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(worldSettingMapper.findByProjectIdAndName(TEST_PROJECT_ID, createRequest.getName())).thenReturn(null);
        when(worldSettingMapper.insert(any(WorldSetting.class))).thenReturn(1);

        // When
        WorldSettingResponse response = worldSettingService.createWorldSetting(TEST_USER_ID, createRequest);

        // Then
        assertNotNull(response);
        verify(worldSettingMapper, times(1)).insert(any(WorldSetting.class));
    }

    @Test
    void testCreateWorldSetting_ProjectNotFound() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            worldSettingService.createWorldSetting(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testCreateWorldSetting_NoPermission() {
        // Given
        Project differentProject = new Project();
        differentProject.setId(TEST_PROJECT_ID);
        differentProject.setUserId(999); // 不同的用户
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(differentProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            worldSettingService.createWorldSetting(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testCreateWorldSetting_NameExists() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(worldSettingMapper.findByProjectIdAndName(TEST_PROJECT_ID, createRequest.getName()))
                .thenReturn(testWorldSetting);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            worldSettingService.createWorldSetting(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testCreateWorldSetting_InvalidSettingType() {
        // Given
        createRequest.setSettingType("invalid_type");
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(worldSettingMapper.findByProjectIdAndName(TEST_PROJECT_ID, createRequest.getName())).thenReturn(null);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            worldSettingService.createWorldSetting(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testGetWorldSettingById_Success() {
        // Given
        when(worldSettingMapper.findById(TEST_WORLD_SETTING_ID)).thenReturn(testWorldSetting);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When
        WorldSettingResponse response = worldSettingService.getWorldSettingById(TEST_WORLD_SETTING_ID, TEST_USER_ID);

        // Then
        assertNotNull(response);
        assertEquals(TEST_WORLD_SETTING_ID, response.getId());
        assertEquals("魔法体系", response.getName());
        verify(worldSettingMapper, times(1)).findById(TEST_WORLD_SETTING_ID);
    }

    @Test
    void testGetWorldSettingById_NotFound() {
        // Given
        when(worldSettingMapper.findById(TEST_WORLD_SETTING_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            worldSettingService.getWorldSettingById(TEST_WORLD_SETTING_ID, TEST_USER_ID);
        });
    }

    @Test
    void testGetWorldSettingsByProjectId_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        List<WorldSetting> worldSettings = Arrays.asList(testWorldSetting);
        when(worldSettingMapper.findByProjectId(TEST_PROJECT_ID)).thenReturn(worldSettings);

        // When
        List<WorldSettingResponse> responses = worldSettingService.getWorldSettingsByProjectId(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals(TEST_WORLD_SETTING_ID, responses.get(0).getId());
        verify(worldSettingMapper, times(1)).findByProjectId(TEST_PROJECT_ID);
    }

    @Test
    void testGetWorldSettingsByProjectId_Empty() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(worldSettingMapper.findByProjectId(TEST_PROJECT_ID)).thenReturn(Collections.emptyList());

        // When
        List<WorldSettingResponse> responses = worldSettingService.getWorldSettingsByProjectId(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertTrue(responses.isEmpty());
    }

    @Test
    void testGetCoreRules_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        List<WorldSetting> coreRules = Arrays.asList(testWorldSetting);
        when(worldSettingMapper.findCoreRules(TEST_PROJECT_ID)).thenReturn(coreRules);

        // When
        List<WorldSettingResponse> responses = worldSettingService.getCoreRules(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals(1, responses.get(0).getIsCoreRule());
        verify(worldSettingMapper, times(1)).findCoreRules(TEST_PROJECT_ID);
    }

    @Test
    void testUpdateWorldSetting_Success() {
        // Given
        WorldSetting nonCoreSetting = new WorldSetting();
        nonCoreSetting.setId(TEST_WORLD_SETTING_ID);
        nonCoreSetting.setProjectId(TEST_PROJECT_ID);
        nonCoreSetting.setName("原有设定");
        nonCoreSetting.setIsCoreRule(0); // 不是核心规则

        when(worldSettingMapper.findById(TEST_WORLD_SETTING_ID)).thenReturn(nonCoreSetting);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(worldSettingMapper.countByNameExcludingId(anyInt(), anyString(), anyInt())).thenReturn(0);
        when(worldSettingMapper.update(any(WorldSetting.class))).thenReturn(1);

        // When
        WorldSettingResponse response = worldSettingService.updateWorldSetting(TEST_WORLD_SETTING_ID, TEST_USER_ID, updateRequest);

        // Then
        assertNotNull(response);
        verify(worldSettingMapper, times(1)).update(any(WorldSetting.class));
    }

    @Test
    void testUpdateWorldSetting_CoreRuleCannotBeModified() {
        // Given
        when(worldSettingMapper.findById(TEST_WORLD_SETTING_ID)).thenReturn(testWorldSetting); // 核心规则
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            worldSettingService.updateWorldSetting(TEST_WORLD_SETTING_ID, TEST_USER_ID, updateRequest);
        });
    }

    @Test
    void testDeleteWorldSetting_Success() {
        // Given
        WorldSetting nonCoreSetting = new WorldSetting();
        nonCoreSetting.setId(TEST_WORLD_SETTING_ID);
        nonCoreSetting.setProjectId(TEST_PROJECT_ID);
        nonCoreSetting.setIsCoreRule(0); // 不是核心规则

        when(worldSettingMapper.findById(TEST_WORLD_SETTING_ID)).thenReturn(nonCoreSetting);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(worldSettingMapper.delete(TEST_WORLD_SETTING_ID)).thenReturn(1);

        // When
        worldSettingService.deleteWorldSetting(TEST_WORLD_SETTING_ID, TEST_USER_ID);

        // Then
        verify(worldSettingMapper, times(1)).delete(TEST_WORLD_SETTING_ID);
    }

    @Test
    void testDeleteWorldSetting_CoreRuleCannotBeDeleted() {
        // Given
        when(worldSettingMapper.findById(TEST_WORLD_SETTING_ID)).thenReturn(testWorldSetting); // 核心规则
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            worldSettingService.deleteWorldSetting(TEST_WORLD_SETTING_ID, TEST_USER_ID);
        });
    }

    @Test
    void testCountWorldSettings_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(worldSettingMapper.countByProjectId(TEST_PROJECT_ID)).thenReturn(8);

        // When
        int count = worldSettingService.countWorldSettings(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertEquals(8, count);
        verify(worldSettingMapper, times(1)).countByProjectId(TEST_PROJECT_ID);
    }
}