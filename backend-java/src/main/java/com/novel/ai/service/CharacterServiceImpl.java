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
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 人物服务实现类
 * 实现人物管理的业务逻辑
 */
@Service
public class CharacterServiceImpl implements CharacterService {

    private final CharacterMapper characterMapper;
    private final ProjectMapper projectMapper;

    public CharacterServiceImpl(CharacterMapper characterMapper, ProjectMapper projectMapper) {
        this.characterMapper = characterMapper;
        this.projectMapper = projectMapper;
    }

    @Override
    public CharacterResponse createCharacter(Integer userId, CharacterCreateRequest request) {
        // 验证项目是否存在且用户有权限
        Project project = projectMapper.findById(request.getProjectId());
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限在此项目中创建人物");
        }

        // 检查人物名称是否已存在
        Character existingCharacter = characterMapper.findByProjectIdAndName(
                request.getProjectId(), request.getName());
        if (existingCharacter != null) {
            throw new BusinessException("人物名称已存在");
        }

        // 创建人物实体
        Character character = new Character();
        character.setProjectId(request.getProjectId());
        character.setName(request.getName());
        character.setAge(request.getAge());
        character.setGender(request.getGender());
        character.setAppearance(request.getAppearance());
        character.setIdentity(request.getIdentity());
        character.setHometown(request.getHometown());
        character.setRole(request.getRole() != null ? request.getRole() : "supporting");
        character.setPersonality(request.getPersonality());
        character.setCoreMotivation(request.getCoreMotivation());
        character.setFears(request.getFears());
        character.setDesires(request.getDesires());
        character.setCharacterArcs(request.getCharacterArcs());
        character.setVoiceStyles(request.getVoiceStyles());
        character.setCreatedAt(LocalDateTime.now());
        character.setUpdatedAt(LocalDateTime.now());

        // 插入数据库
        int result = characterMapper.insert(character);
        if (result <= 0) {
            throw new BusinessException("人物创建失败");
        }

        return convertToResponse(character);
    }

    @Override
    public CharacterResponse getCharacterById(Integer characterId, Integer userId) {
        // 查找人物
        Character character = characterMapper.findById(characterId);
        if (character == null) {
            throw new NotFoundException("人物不存在");
        }

        // 验证权限
        Project project = projectMapper.findById(character.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此人物");
        }

        return convertToResponse(character);
    }

    @Override
    public List<CharacterResponse> getCharactersByProjectId(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的人物");
        }

        // 查找人物列表
        List<Character> characters = characterMapper.findByProjectId(projectId);
        return characters.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<CharacterResponse> getCharactersByProjectIdAndRole(Integer projectId, String role, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的人物");
        }

        // 按角色查找人物
        List<Character> characters = characterMapper.findByProjectIdAndRole(projectId, role);
        return characters.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<CharacterResponse> getProtagonists(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的人物");
        }

        // 查找主角
        List<Character> characters = characterMapper.findProtagonists(projectId);
        return characters.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<CharacterResponse> getAntagonists(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的人物");
        }

        // 查找反派
        List<Character> characters = characterMapper.findAntagonists(projectId);
        return characters.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public CharacterResponse updateCharacter(Integer characterId, Integer userId, CharacterUpdateRequest request) {
        // 查找人物
        Character character = characterMapper.findById(characterId);
        if (character == null) {
            throw new NotFoundException("人物不存在");
        }

        // 验证权限
        Project project = projectMapper.findById(character.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权限修改此人物");
        }

        // 检查名称冲突（排除当前人物）
        if (request.getName() != null && !request.getName().equals(character.getName())) {
            int nameCount = characterMapper.countByNameExcludingId(
                    character.getProjectId(), request.getName(), characterId);
            if (nameCount > 0) {
                throw new BusinessException("人物名称已存在");
            }
        }

        // 更新字段
        if (request.getName() != null) character.setName(request.getName());
        if (request.getAge() != null) character.setAge(request.getAge());
        if (request.getGender() != null) character.setGender(request.getGender());
        if (request.getAppearance() != null) character.setAppearance(request.getAppearance());
        if (request.getIdentity() != null) character.setIdentity(request.getIdentity());
        if (request.getHometown() != null) character.setHometown(request.getHometown());
        if (request.getRole() != null) character.setRole(request.getRole());
        if (request.getPersonality() != null) character.setPersonality(request.getPersonality());
        if (request.getCoreMotivation() != null) character.setCoreMotivation(request.getCoreMotivation());
        if (request.getFears() != null) character.setFears(request.getFears());
        if (request.getDesires() != null) character.setDesires(request.getDesires());
        if (request.getCharacterArcs() != null) character.setCharacterArcs(request.getCharacterArcs());
        if (request.getVoiceStyles() != null) character.setVoiceStyles(request.getVoiceStyles());
        character.setUpdatedAt(LocalDateTime.now());

        // 更新数据库
        int result = characterMapper.update(character);
        if (result <= 0) {
            throw new BusinessException("人物更新失败");
        }

        return convertToResponse(character);
    }

    @Override
    public void deleteCharacter(Integer characterId, Integer userId) {
        // 查找人物
        Character character = characterMapper.findById(characterId);
        if (character == null) {
            throw new NotFoundException("人物不存在");
        }

        // 验证权限
        Project project = projectMapper.findById(character.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权限删除此人物");
        }

        // 删除人物
        int result = characterMapper.delete(characterId);
        if (result <= 0) {
            throw new BusinessException("人物删除失败");
        }
    }

    @Override
    public int countCharacters(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目");
        }

        return characterMapper.countByProjectId(projectId);
    }

    /**
     * 将Character实体转换为CharacterResponse
     */
    private CharacterResponse convertToResponse(Character character) {
        CharacterResponse response = new CharacterResponse();
        response.setId(character.getId());
        response.setProjectId(character.getProjectId());
        response.setName(character.getName());
        response.setAge(character.getAge());
        response.setGender(character.getGender());
        response.setAppearance(character.getAppearance());
        response.setIdentity(character.getIdentity());
        response.setHometown(character.getHometown());
        response.setRole(character.getRole());
        response.setPersonality(character.getPersonality());
        response.setCoreMotivation(character.getCoreMotivation());
        response.setFears(character.getFears());
        response.setDesires(character.getDesires());
        response.setCharacterArcs(character.getCharacterArcs());
        response.setVoiceStyles(character.getVoiceStyles());
        response.setCreatedAt(character.getCreatedAt());
        response.setUpdatedAt(character.getUpdatedAt());
        return response;
    }
}