package com.novel.ai.service;

import com.novel.ai.model.dto.request.ProjectCreateRequest;
import com.novel.ai.model.dto.request.ProjectUpdateRequest;
import com.novel.ai.model.dto.response.ProjectResponse;

import java.util.List;

public interface ProjectService {

    /**
     * 创建新项目
     *
     * @param userId 用户ID
     * @param request 项目创建请求
     * @return 创建的项目响应
     */
    ProjectResponse createProject(Integer userId, ProjectCreateRequest request);

    /**
     * 根据ID获取项目详情
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 项目响应
     */
    ProjectResponse getProjectById(Integer projectId, Integer userId);

    /**
     * 获取用户的所有项目
     *
     * @param userId 用户ID
     * @return 项目列表
     */
    List<ProjectResponse> getProjectsByUserId(Integer userId);

    /**
     * 根据状态获取用户的项目
     *
     * @param userId 用户ID
     * @param status 项目状态
     * @return 项目列表
     */
    List<ProjectResponse> getProjectsByUserIdAndStatus(Integer userId, String status);

    /**
     * 更新项目信息
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @param request 项目更新请求
     * @return 更新后的项目响应
     */
    ProjectResponse updateProject(Integer projectId, Integer userId, ProjectUpdateRequest request);

    /**
     * 删除项目
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     */
    void deleteProject(Integer projectId, Integer userId);

    /**
     * 更新项目统计信息
     *
     * @param projectId 项目ID
     * @param totalWords 总字数
     * @param totalChapters 总章节数
     */
    void updateProjectStatistics(Integer projectId, Integer totalWords, Integer totalChapters);
}