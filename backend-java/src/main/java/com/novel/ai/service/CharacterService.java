package com.novel.ai.service;

import com.novel.ai.model.dto.request.CharacterCreateRequest;
import com.novel.ai.model.dto.request.CharacterUpdateRequest;
import com.novel.ai.model.dto.response.CharacterResponse;

import java.util.List;

/**
 * 人物服务接口
 * 定义人物管理的业务逻辑操作
 */
public interface CharacterService {

    /**
     * 创建新人物
     *
     * @param userId 用户ID
     * @param request 人物创建请求
     * @return 创建的人物响应
     */
    CharacterResponse createCharacter(Integer userId, CharacterCreateRequest request);

    /**
     * 根据ID获取人物详情
     *
     * @param characterId 人物ID
     * @param userId 用户ID（用于权限验证）
     * @return 人物响应
     */
    CharacterResponse getCharacterById(Integer characterId, Integer userId);

    /**
     * 获取项目的所有人物
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 人物列表
     */
    List<CharacterResponse> getCharactersByProjectId(Integer projectId, Integer userId);

    /**
     * 根据角色类型获取项目的人物
     *
     * @param projectId 项目ID
     * @param role 角色类型
     * @param userId 用户ID（用于权限验证）
     * @return 人物列表
     */
    List<CharacterResponse> getCharactersByProjectIdAndRole(Integer projectId, String role, Integer userId);

    /**
     * 获取项目的主角列表
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 主角列表
     */
    List<CharacterResponse> getProtagonists(Integer projectId, Integer userId);

    /**
     * 获取项目的反派列表
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 反派列表
     */
    List<CharacterResponse> getAntagonists(Integer projectId, Integer userId);

    /**
     * 更新人物信息
     *
     * @param characterId 人物ID
     * @param userId 用户ID（用于权限验证）
     * @param request 人物更新请求
     * @return 更新后的人物响应
     */
    CharacterResponse updateCharacter(Integer characterId, Integer userId, CharacterUpdateRequest request);

    /**
     * 删除人物
     *
     * @param characterId 人物ID
     * @param userId 用户ID（用于权限验证）
     */
    void deleteCharacter(Integer characterId, Integer userId);

    /**
     * 统计项目的人物数量
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 人物数量
     */
    int countCharacters(Integer projectId, Integer userId);
}