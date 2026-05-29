package com.novel.ai.service;

import com.novel.ai.model.dto.request.WorldSettingCreateRequest;
import com.novel.ai.model.dto.request.WorldSettingUpdateRequest;
import com.novel.ai.model.dto.response.WorldSettingResponse;

import java.util.List;

/**
 * 世界观设定服务接口
 * 定义世界观设定管理的业务逻辑操作
 */
public interface WorldSettingService {

    /**
     * 创建新世界观设定
     *
     * @param userId 用户ID
     * @param request 世界观设定创建请求
     * @return 创建的世界观设定响应
     */
    WorldSettingResponse createWorldSetting(Integer userId, WorldSettingCreateRequest request);

    /**
     * 根据ID获取世界观设定详情
     *
     * @param worldSettingId 世界观设定ID
     * @param userId 用户ID（用于权限验证）
     * @return 世界观设定响应
     */
    WorldSettingResponse getWorldSettingById(Integer worldSettingId, Integer userId);

    /**
     * 获取项目的所有世界观设定
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 世界观设定列表
     */
    List<WorldSettingResponse> getWorldSettingsByProjectId(Integer projectId, Integer userId);

    /**
     * 根据设定类型获取项目的世界观设定
     *
     * @param projectId 项目ID
     * @param settingType 设定类型
     * @param userId 用户ID（用于权限验证）
     * @return 世界观设定列表
     */
    List<WorldSettingResponse> getWorldSettingsByProjectIdAndType(Integer projectId, String settingType, Integer userId);

    /**
     * 获取项目的核心规则
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 核心规则列表
     */
    List<WorldSettingResponse> getCoreRules(Integer projectId, Integer userId);

    /**
     * 更新世界观设定
     *
     * @param worldSettingId 世界观设定ID
     * @param userId 用户ID（用于权限验证）
     * @param request 世界观设定更新请求
     * @return 更新后的世界观设定响应
     */
    WorldSettingResponse updateWorldSetting(Integer worldSettingId, Integer userId, WorldSettingUpdateRequest request);

    /**
     * 删除世界观设定
     *
     * @param worldSettingId 世界观设定ID
     * @param userId 用户ID（用于权限验证）
     */
    void deleteWorldSetting(Integer worldSettingId, Integer userId);

    /**
     * 统计项目的世界观设定数量
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 世界观设定数量
     */
    int countWorldSettings(Integer projectId, Integer userId);
}