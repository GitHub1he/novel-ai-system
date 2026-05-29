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
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 世界观设定服务实现类
 * 实现世界观设定管理的业务逻辑
 */
@Service
public class WorldSettingServiceImpl implements WorldSettingService {

    private final WorldSettingMapper worldSettingMapper;
    private final ProjectMapper projectMapper;

    public WorldSettingServiceImpl(WorldSettingMapper worldSettingMapper, ProjectMapper projectMapper) {
        this.worldSettingMapper = worldSettingMapper;
        this.projectMapper = projectMapper;
    }

    @Override
    public WorldSettingResponse createWorldSetting(Integer userId, WorldSettingCreateRequest request) {
        // 验证项目是否存在且用户有权限
        Project project = projectMapper.findById(request.getProjectId());
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限在此项目中创建世界观设定");
        }

        // 检查设定名称是否已存在
        WorldSetting existingSetting = worldSettingMapper.findByProjectIdAndName(
                request.getProjectId(), request.getName());
        if (existingSetting != null) {
            throw new BusinessException("世界观设定名称已存在");
        }

        // 验证设定类型
        validateSettingType(request.getSettingType());

        // 创建世界观设定实体
        WorldSetting worldSetting = new WorldSetting();
        worldSetting.setProjectId(request.getProjectId());
        worldSetting.setName(request.getName());
        worldSetting.setSettingType(request.getSettingType());
        worldSetting.setDescription(request.getDescription());
        worldSetting.setAttributes(request.getAttributes());
        worldSetting.setRelatedEntities(request.getRelatedEntities());
        worldSetting.setIsCoreRule(request.getIsCoreRule() != null ? request.getIsCoreRule() : 0);
        worldSetting.setImage(request.getImage());
        worldSetting.setCreatedAt(LocalDateTime.now());
        worldSetting.setUpdatedAt(LocalDateTime.now());

        // 插入数据库
        int result = worldSettingMapper.insert(worldSetting);
        if (result <= 0) {
            throw new BusinessException("世界观设定创建失败");
        }

        return convertToResponse(worldSetting);
    }

    @Override
    public WorldSettingResponse getWorldSettingById(Integer worldSettingId, Integer userId) {
        // 查找世界观设定
        WorldSetting worldSetting = worldSettingMapper.findById(worldSettingId);
        if (worldSetting == null) {
            throw new NotFoundException("世界观设定不存在");
        }

        // 验证权限
        Project project = projectMapper.findById(worldSetting.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此世界观设定");
        }

        return convertToResponse(worldSetting);
    }

    @Override
    public List<WorldSettingResponse> getWorldSettingsByProjectId(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的世界观设定");
        }

        // 查找世界观设定列表
        List<WorldSetting> worldSettings = worldSettingMapper.findByProjectId(projectId);
        return worldSettings.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<WorldSettingResponse> getWorldSettingsByProjectIdAndType(Integer projectId, String settingType, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的世界观设定");
        }

        // 验证设定类型
        validateSettingType(settingType);

        // 按设定类型查找
        List<WorldSetting> worldSettings = worldSettingMapper.findByProjectIdAndType(projectId, settingType);
        return worldSettings.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<WorldSettingResponse> getCoreRules(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的世界观设定");
        }

        // 查找核心规则
        List<WorldSetting> worldSettings = worldSettingMapper.findCoreRules(projectId);
        return worldSettings.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public WorldSettingResponse updateWorldSetting(Integer worldSettingId, Integer userId, WorldSettingUpdateRequest request) {
        // 查找世界观设定
        WorldSetting worldSetting = worldSettingMapper.findById(worldSettingId);
        if (worldSetting == null) {
            throw new NotFoundException("世界观设定不存在");
        }

        // 验证权限
        Project project = projectMapper.findById(worldSetting.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权限修改此世界观设定");
        }

        // 检查是否为核心规则
        if (worldSetting.isCoreRule()) {
            throw new BusinessException("核心规则不可修改");
        }

        // 检查名称冲突（排除当前世界观设定）
        if (request.getName() != null && !request.getName().equals(worldSetting.getName())) {
            int nameCount = worldSettingMapper.countByNameExcludingId(
                    worldSetting.getProjectId(), request.getName(), worldSettingId);
            if (nameCount > 0) {
                throw new BusinessException("世界观设定名称已存在");
            }
        }

        // 验证设定类型（如果要修改）
        if (request.getSettingType() != null) {
            validateSettingType(request.getSettingType());
        }

        // 更新字段
        if (request.getName() != null) worldSetting.setName(request.getName());
        if (request.getSettingType() != null) worldSetting.setSettingType(request.getSettingType());
        if (request.getDescription() != null) worldSetting.setDescription(request.getDescription());
        if (request.getAttributes() != null) worldSetting.setAttributes(request.getAttributes());
        if (request.getRelatedEntities() != null) worldSetting.setRelatedEntities(request.getRelatedEntities());
        if (request.getImage() != null) worldSetting.setImage(request.getImage());
        worldSetting.setUpdatedAt(LocalDateTime.now());

        // 更新数据库
        int result = worldSettingMapper.update(worldSetting);
        if (result <= 0) {
            throw new BusinessException("世界观设定更新失败");
        }

        return convertToResponse(worldSetting);
    }

    @Override
    public void deleteWorldSetting(Integer worldSettingId, Integer userId) {
        // 查找世界观设定
        WorldSetting worldSetting = worldSettingMapper.findById(worldSettingId);
        if (worldSetting == null) {
            throw new NotFoundException("世界观设定不存在");
        }

        // 验证权限
        Project project = projectMapper.findById(worldSetting.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权限删除此世界观设定");
        }

        // 检查是否为核心规则
        if (worldSetting.isCoreRule()) {
            throw new BusinessException("核心规则不可删除");
        }

        // 删除世界观设定
        int result = worldSettingMapper.delete(worldSettingId);
        if (result <= 0) {
            throw new BusinessException("世界观设定删除失败");
        }
    }

    @Override
    public int countWorldSettings(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目");
        }

        return worldSettingMapper.countByProjectId(projectId);
    }

    /**
     * 验证设定类型是否有效
     */
    private void validateSettingType(String settingType) {
        if (settingType == null) {
            throw new BusinessException("设定类型不能为空");
        }

        String[] validTypes = {"era", "region", "rule", "culture", "power", "location", "faction", "item", "event"};
        boolean isValid = false;
        for (String type : validTypes) {
            if (type.equals(settingType)) {
                isValid = true;
                break;
            }
        }

        if (!isValid) {
            throw new BusinessException("无效的设定类型: " + settingType);
        }
    }

    /**
     * 将WorldSetting实体转换为WorldSettingResponse
     */
    private WorldSettingResponse convertToResponse(WorldSetting worldSetting) {
        WorldSettingResponse response = new WorldSettingResponse();
        response.setId(worldSetting.getId());
        response.setProjectId(worldSetting.getProjectId());
        response.setName(worldSetting.getName());
        response.setSettingType(worldSetting.getSettingType());
        response.setDescription(worldSetting.getDescription());
        response.setAttributes(worldSetting.getAttributes());
        response.setRelatedEntities(worldSetting.getRelatedEntities());
        response.setIsCoreRule(worldSetting.getIsCoreRule());
        response.setImage(worldSetting.getImage());
        response.setCreatedAt(worldSetting.getCreatedAt());
        response.setUpdatedAt(worldSetting.getUpdatedAt());
        return response;
    }
}