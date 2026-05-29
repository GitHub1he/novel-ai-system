package com.novel.ai.service;

import com.novel.ai.model.dto.request.PlotNodeCreateRequest;
import com.novel.ai.model.dto.request.PlotNodeUpdateRequest;
import com.novel.ai.model.dto.response.PlotNodeResponse;

import java.util.List;

/**
 * 情节节点服务接口
 * 定义情节节点管理的业务逻辑操作
 */
public interface PlotNodeService {

    /**
     * 创建新情节节点
     *
     * @param userId 用户ID
     * @param request 情节节点创建请求
     * @return 创建的情节节点响应
     */
    PlotNodeResponse createPlotNode(Integer userId, PlotNodeCreateRequest request);

    /**
     * 根据ID获取情节节点详情
     *
     * @param plotNodeId 情节节点ID
     * @param userId 用户ID（用于权限验证）
     * @return 情节节点响应
     */
    PlotNodeResponse getPlotNodeById(Integer plotNodeId, Integer userId);

    /**
     * 获取项目的所有情节节点
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 情节节点列表
     */
    List<PlotNodeResponse> getPlotNodesByProjectId(Integer projectId, Integer userId);

    /**
     * 根据重要程度获取项目的情节节点
     *
     * @param projectId 项目ID
     * @param importance 重要程度
     * @param userId 用户ID（用于权限验证）
     * @return 情节节点列表
     */
    List<PlotNodeResponse> getPlotNodesByProjectIdAndImportance(Integer projectId, String importance, Integer userId);

    /**
     * 根据情节类型获取项目的情节节点
     *
     * @param projectId 项目ID
     * @param plotType 情节类型
     * @param userId 用户ID（用于权限验证）
     * @return 情节节点列表
     */
    List<PlotNodeResponse> getPlotNodesByProjectIdAndType(Integer projectId, String plotType, Integer userId);

    /**
     * 根据章节ID获取情节节点
     *
     * @param chapterId 章节ID
     * @param userId 用户ID（用于权限验证）
     * @return 情节节点列表
     */
    List<PlotNodeResponse> getPlotNodesByChapterId(Integer chapterId, Integer userId);

    /**
     * 获取项目的主线情节
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 主线情节列表
     */
    List<PlotNodeResponse> getMainPlots(Integer projectId, Integer userId);

    /**
     * 获取项目的高潮情节
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 高潮情节列表
     */
    List<PlotNodeResponse> getClimaxPlots(Integer projectId, Integer userId);

    /**
     * 更新情节节点
     *
     * @param plotNodeId 情节节点ID
     * @param userId 用户ID（用于权限验证）
     * @param request 情节节点更新请求
     * @return 更新后的情节节点响应
     */
    PlotNodeResponse updatePlotNode(Integer plotNodeId, Integer userId, PlotNodeUpdateRequest request);

    /**
     * 删除情节节点
     *
     * @param plotNodeId 情节节点ID
     * @param userId 用户ID（用于权限验证）
     */
    void deletePlotNode(Integer plotNodeId, Integer userId);

    /**
     * 统计项目的情节节点数量
     *
     * @param projectId 项目ID
     * @param userId 用户ID（用于权限验证）
     * @return 情节节点数量
     */
    int countPlotNodes(Integer projectId, Integer userId);
}