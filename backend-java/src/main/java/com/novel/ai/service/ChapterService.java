package com.novel.ai.service;

import com.novel.ai.model.dto.request.ChapterCreateRequest;
import com.novel.ai.model.dto.request.ChapterUpdateRequest;
import com.novel.ai.model.dto.response.ChapterResponse;

import java.util.List;

public interface ChapterService {

    /**
     * 创建新章节
     *
     * @param userId 用户ID
     * @param request 章节创建请求
     * @return 创建的章节响应
     */
    ChapterResponse createChapter(Integer userId, ChapterCreateRequest request);

    /**
     * 根据ID获取章节详情
     *
     * @param chapterId 章节ID
     * @param userId 用户ID（用于权限验证）
     * @return 章节响应
     */
    ChapterResponse getChapterById(Integer chapterId, Integer userId);

    /**
     * 获取项目的所有章节（列表视图，不包含content）
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 章节列表
     */
    List<ChapterResponse> getChaptersByProjectId(Integer projectId, Integer userId);

    /**
     * 根据状态获取项目的章节
     *
     * @param projectId 项目ID
     * @param status 章节状态
     * @param userId 用户ID（用于权限验证）
     * @return 章节列表
     */
    List<ChapterResponse> getChaptersByProjectIdAndStatus(Integer projectId, String status, Integer userId);

    /**
     * 更新章节信息
     *
     * @param chapterId 章节ID
     * @param userId 用户ID（用于权限验证）
     * @param request 章节更新请求
     * @return 更新后的章节响应
     */
    ChapterResponse updateChapter(Integer chapterId, Integer userId, ChapterUpdateRequest request);

    /**
     * 删除章节
     *
     * @param chapterId 章节ID
     * @param userId 用户ID（用于权限验证）
     */
    void deleteChapter(Integer chapterId, Integer userId);

    /**
     * 更新章节状态
     *
     * @param chapterId 章节ID
     * @param userId 用户ID（用于权限验证）
     * @param status 新状态
     */
    void updateChapterStatus(Integer chapterId, Integer userId, String status);

    /**
     * 获取项目的下一个章节号
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 下一个章节号
     */
    Integer getNextChapterNumber(Integer projectId, Integer userId);
}