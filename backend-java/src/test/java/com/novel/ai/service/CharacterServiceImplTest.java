package com.novel.ai.service;

import com.novel.ai.exception.BusinessException;
import com.novel.ai.exception.NotFoundException;
import com.novel.ai.mapper.CharacterMapper;
import com.novel.ai.mapper.ProjectMapper;
import com.novel.ai.model.dto.request.CharacterCreateRequest;
import com.novel.ai.model.dto.request.CharacterUpdateRequest;
import com.novel.ai.model.dto.response.CharacterResponse;
import com.novel.ai.model.entity.Character;
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
class CharacterServiceImplTest {

    @Mock
    private CharacterMapper characterMapper;

    @Mock
    private ProjectMapper projectMapper;

    @InjectMocks
    private CharacterServiceImpl characterService;

    private Character testCharacter;
    private Project testProject;
    private CharacterCreateRequest createRequest;
    private CharacterUpdateRequest updateRequest;
    private final Integer TEST_USER_ID = 1;
    private final Integer TEST_PROJECT_ID = 1;
    private final Integer TEST_CHARACTER_ID = 1;

    @BeforeEach
    void setUp() {
        // 创建测试项目
        testProject = new Project();
        testProject.setId(TEST_PROJECT_ID);
        testProject.setUserId(TEST_USER_ID);
        testProject.setTitle("测试项目");

        // 创建测试人物
        testCharacter = new Character();
        testCharacter.setId(TEST_CHARACTER_ID);
        testCharacter.setProjectId(TEST_PROJECT_ID);
        testCharacter.setName("张三");
        testCharacter.setAge(25);
        testCharacter.setGender("男");
        testCharacter.setRole("protagonist");
        testCharacter.setPersonality("[\"勇敢\", \"善良\"]");
        testCharacter.setCreatedAt(LocalDateTime.now());
        testCharacter.setUpdatedAt(LocalDateTime.now());

        // 创建创建请求
        createRequest = new CharacterCreateRequest();
        createRequest.setProjectId(TEST_PROJECT_ID);
        createRequest.setName("李四");
        createRequest.setAge(30);
        createRequest.setGender("女");
        createRequest.setRole("supporting");

        // 创建更新请求
        updateRequest = new CharacterUpdateRequest();
        updateRequest.setName("王五");
        updateRequest.setAge(35);
        updateRequest.setRole("antagonist");
    }

    @Test
    void testCreateCharacter_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(characterMapper.findByProjectIdAndName(TEST_PROJECT_ID, createRequest.getName())).thenReturn(null);
        when(characterMapper.insert(any(Character.class))).thenReturn(1);

        // When
        CharacterResponse response = characterService.createCharacter(TEST_USER_ID, createRequest);

        // Then
        assertNotNull(response);
        verify(characterMapper, times(1)).insert(any(Character.class));
    }

    @Test
    void testCreateCharacter_ProjectNotFound() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            characterService.createCharacter(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testCreateCharacter_NoPermission() {
        // Given
        Project differentProject = new Project();
        differentProject.setId(TEST_PROJECT_ID);
        differentProject.setUserId(999); // 不同的用户
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(differentProject);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            characterService.createCharacter(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testCreateCharacter_NameExists() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(characterMapper.findByProjectIdAndName(TEST_PROJECT_ID, createRequest.getName())).thenReturn(testCharacter);

        // When & Then
        assertThrows(BusinessException.class, () -> {
            characterService.createCharacter(TEST_USER_ID, createRequest);
        });
    }

    @Test
    void testGetCharacterById_Success() {
        // Given
        when(characterMapper.findById(TEST_CHARACTER_ID)).thenReturn(testCharacter);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);

        // When
        CharacterResponse response = characterService.getCharacterById(TEST_CHARACTER_ID, TEST_USER_ID);

        // Then
        assertNotNull(response);
        assertEquals(TEST_CHARACTER_ID, response.getId());
        assertEquals("张三", response.getName());
        verify(characterMapper, times(1)).findById(TEST_CHARACTER_ID);
    }

    @Test
    void testGetCharacterById_NotFound() {
        // Given
        when(characterMapper.findById(TEST_CHARACTER_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            characterService.getCharacterById(TEST_CHARACTER_ID, TEST_USER_ID);
        });
    }

    @Test
    void testGetCharactersByProjectId_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        List<Character> characters = Arrays.asList(testCharacter);
        when(characterMapper.findByProjectId(TEST_PROJECT_ID)).thenReturn(characters);

        // When
        List<CharacterResponse> responses = characterService.getCharactersByProjectId(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals(TEST_CHARACTER_ID, responses.get(0).getId());
        verify(characterMapper, times(1)).findByProjectId(TEST_PROJECT_ID);
    }

    @Test
    void testGetCharactersByProjectId_Empty() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(characterMapper.findByProjectId(TEST_PROJECT_ID)).thenReturn(Collections.emptyList());

        // When
        List<CharacterResponse> responses = characterService.getCharactersByProjectId(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertTrue(responses.isEmpty());
    }

    @Test
    void testUpdateCharacter_Success() {
        // Given
        when(characterMapper.findById(TEST_CHARACTER_ID)).thenReturn(testCharacter);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(characterMapper.countByNameExcludingId(anyInt(), anyString(), anyInt())).thenReturn(0);
        when(characterMapper.update(any(Character.class))).thenReturn(1);

        // When
        CharacterResponse response = characterService.updateCharacter(TEST_CHARACTER_ID, TEST_USER_ID, updateRequest);

        // Then
        assertNotNull(response);
        verify(characterMapper, times(1)).update(any(Character.class));
    }

    @Test
    void testUpdateCharacter_NotFound() {
        // Given
        when(characterMapper.findById(TEST_CHARACTER_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            characterService.updateCharacter(TEST_CHARACTER_ID, TEST_USER_ID, updateRequest);
        });
    }

    @Test
    void testDeleteCharacter_Success() {
        // Given
        when(characterMapper.findById(TEST_CHARACTER_ID)).thenReturn(testCharacter);
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(characterMapper.delete(TEST_CHARACTER_ID)).thenReturn(1);

        // When
        characterService.deleteCharacter(TEST_CHARACTER_ID, TEST_USER_ID);

        // Then
        verify(characterMapper, times(1)).delete(TEST_CHARACTER_ID);
    }

    @Test
    void testDeleteCharacter_NotFound() {
        // Given
        when(characterMapper.findById(TEST_CHARACTER_ID)).thenReturn(null);

        // When & Then
        assertThrows(NotFoundException.class, () -> {
            characterService.deleteCharacter(TEST_CHARACTER_ID, TEST_USER_ID);
        });
    }

    @Test
    void testCountCharacters_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        when(characterMapper.countByProjectId(TEST_PROJECT_ID)).thenReturn(5);

        // When
        int count = characterService.countCharacters(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertEquals(5, count);
        verify(characterMapper, times(1)).countByProjectId(TEST_PROJECT_ID);
    }

    @Test
    void testGetProtagonists_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        List<Character> protagonists = Arrays.asList(testCharacter);
        when(characterMapper.findProtagonists(TEST_PROJECT_ID)).thenReturn(protagonists);

        // When
        List<CharacterResponse> responses = characterService.getProtagonists(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals("protagonist", responses.get(0).getRole());
    }

    @Test
    void testGetAntagonists_Success() {
        // Given
        when(projectMapper.findById(TEST_PROJECT_ID)).thenReturn(testProject);
        testCharacter.setRole("antagonist");
        List<Character> antagonists = Arrays.asList(testCharacter);
        when(characterMapper.findAntagonists(TEST_PROJECT_ID)).thenReturn(antagonists);

        // When
        List<CharacterResponse> responses = characterService.getAntagonists(TEST_PROJECT_ID, TEST_USER_ID);

        // Then
        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals("antagonist", responses.get(0).getRole());
    }
}