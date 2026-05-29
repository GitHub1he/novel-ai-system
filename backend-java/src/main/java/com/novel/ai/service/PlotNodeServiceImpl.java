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
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 情节节点服务实现类
 * 实现情节节点管理的业务逻辑
 */
@Service
public class PlotNodeServiceImpl implements PlotNodeService {

    private final PlotNodeMapper plotNodeMapper;
    private final ProjectMapper projectMapper;
    private final ChapterMapper chapterMapper;

    public PlotNodeServiceImpl(PlotNodeMapper plotNodeMapper, ProjectMapper projectMapper, ChapterMapper chapterMapper) {
        this.plotNodeMapper = plotNodeMapper;
        this.projectMapper = projectMapper;
        this.chapterMapper = chapterMapper;
    }

    @Override
    public PlotNodeResponse createPlotNode(Integer userId, PlotNodeCreateRequest request) {
        // 验证项目是否存在且用户有权限
        Project project = projectMapper.findById(request.getProjectId());
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限在此项目中创建情节节点");
        }

        // 验证章节ID（如果提供）
        if (request.getChapterId() != null) {
            Chapter chapter = chapterMapper.findById(request.getChapterId());
            if (chapter == null || !chapter.getProjectId().equals(request.getProjectId())) {
                throw new BusinessException("章节不存在或不属于该项目");
            }
        }

        // 检查情节节点标题是否已存在
        PlotNode existingPlotNode = plotNodeMapper.findByProjectIdAndTitle(
                request.getProjectId(), request.getTitle());
        if (existingPlotNode != null) {
            throw new BusinessException("情节节点标题已存在");
        }

        // 验证情节类型和重要程度
        validatePlotType(request.getPlotType());
        validateImportance(request.getImportance());

        // 创建情节节点实体
        PlotNode plotNode = new PlotNode();
        plotNode.setProjectId(request.getProjectId());
        plotNode.setTitle(request.getTitle());
        plotNode.setDescription(request.getDescription());
        plotNode.setPlotType(request.getPlotType() != null ? request.getPlotType() : "other");
        plotNode.setImportance(request.getImportance() != null ? request.getImportance() : "branch");
        plotNode.setChapterId(request.getChapterId());
        plotNode.setRelatedCharacters(request.getRelatedCharacters());
        plotNode.setRelatedLocations(request.getRelatedLocations());
        plotNode.setRelatedWorldSettings(request.getRelatedWorldSettings());
        plotNode.setConflictPoints(request.getConflictPoints());
        plotNode.setThemeTags(request.getThemeTags());
        plotNode.setCreatedAt(LocalDateTime.now());
        plotNode.setUpdatedAt(LocalDateTime.now());

        // 插入数据库
        int result = plotNodeMapper.insert(plotNode);
        if (result <= 0) {
            throw new BusinessException("情节节点创建失败");
        }

        return convertToResponse(plotNode);
    }

    @Override
    public PlotNodeResponse getPlotNodeById(Integer plotNodeId, Integer userId) {
        // 查找情节节点
        PlotNode plotNode = plotNodeMapper.findById(plotNodeId);
        if (plotNode == null) {
            throw new NotFoundException("情节节点不存在");
        }

        // 验证权限
        Project project = projectMapper.findById(plotNode.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此情节节点");
        }

        return convertToResponse(plotNode);
    }

    @Override
    public List<PlotNodeResponse> getPlotNodesByProjectId(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的情节节点");
        }

        // 查找情节节点列表
        List<PlotNode> plotNodes = plotNodeMapper.findByProjectId(projectId);
        return plotNodes.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<PlotNodeResponse> getPlotNodesByProjectIdAndImportance(Integer projectId, String importance, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的情节节点");
        }

        // 验证重要程度
        validateImportance(importance);

        // 按重要程度查找
        List<PlotNode> plotNodes = plotNodeMapper.findByProjectIdAndImportance(projectId, importance);
        return plotNodes.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<PlotNodeResponse> getPlotNodesByProjectIdAndType(Integer projectId, String plotType, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的情节节点");
        }

        // 验证情节类型
        validatePlotType(plotType);

        // 按情节类型查找
        List<PlotNode> plotNodes = plotNodeMapper.findByProjectIdAndType(projectId, plotType);
        return plotNodes.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<PlotNodeResponse> getPlotNodesByChapterId(Integer chapterId, Integer userId) {
        // 验证章节存在
        Chapter chapter = chapterMapper.findById(chapterId);
        if (chapter == null) {
            throw new NotFoundException("章节不存在");
        }

        // 验证项目权限
        Project project = projectMapper.findById(chapter.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此章节的情节节点");
        }

        // 查找章节相关的情节节点
        List<PlotNode> plotNodes = plotNodeMapper.findByChapterId(chapterId);
        return plotNodes.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<PlotNodeResponse> getMainPlots(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的情节节点");
        }

        // 查找主线情节
        List<PlotNode> plotNodes = plotNodeMapper.findMainPlots(projectId);
        return plotNodes.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<PlotNodeResponse> getClimaxPlots(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目的情节节点");
        }

        // 查找高潮情节
        List<PlotNode> plotNodes = plotNodeMapper.findClimaxPlots(projectId);
        return plotNodes.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public PlotNodeResponse updatePlotNode(Integer plotNodeId, Integer userId, PlotNodeUpdateRequest request) {
        // 查找情节节点
        PlotNode plotNode = plotNodeMapper.findById(plotNodeId);
        if (plotNode == null) {
            throw new NotFoundException("情节节点不存在");
        }

        // 验证权限
        Project project = projectMapper.findById(plotNode.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权限修改此情节节点");
        }

        // 检查标题冲突（排除当前情节节点）
        if (request.getTitle() != null && !request.getTitle().equals(plotNode.getTitle())) {
            int titleCount = plotNodeMapper.countByTitleExcludingId(
                    plotNode.getProjectId(), request.getTitle(), plotNodeId);
            if (titleCount > 0) {
                throw new BusinessException("情节节点标题已存在");
            }
        }

        // 验证情节类型和重要程度（如果要修改）
        if (request.getPlotType() != null) {
            validatePlotType(request.getPlotType());
        }
        if (request.getImportance() != null) {
            validateImportance(request.getImportance());
        }

        // 更新字段
        if (request.getTitle() != null) plotNode.setTitle(request.getTitle());
        if (request.getDescription() != null) plotNode.setDescription(request.getDescription());
        if (request.getPlotType() != null) plotNode.setPlotType(request.getPlotType());
        if (request.getImportance() != null) plotNode.setImportance(request.getImportance());
        if (request.getChapterId() != null) plotNode.setChapterId(request.getChapterId());
        if (request.getRelatedCharacters() != null) plotNode.setRelatedCharacters(request.getRelatedCharacters());
        if (request.getRelatedLocations() != null) plotNode.setRelatedLocations(request.getRelatedLocations());
        if (request.getRelatedWorldSettings() != null) plotNode.setRelatedWorldSettings(request.getRelatedWorldSettings());
        if (request.getConflictPoints() != null) plotNode.setConflictPoints(request.getConflictPoints());
        if (request.getThemeTags() != null) plotNode.setThemeTags(request.getThemeTags());
        plotNode.setUpdatedAt(LocalDateTime.now());

        // 更新数据库
        int result = plotNodeMapper.update(plotNode);
        if (result <= 0) {
            throw new BusinessException("情节节点更新失败");
        }

        return convertToResponse(plotNode);
    }

    @Override
    public void deletePlotNode(Integer plotNodeId, Integer userId) {
        // 查找情节节点
        PlotNode plotNode = plotNodeMapper.findById(plotNodeId);
        if (plotNode == null) {
            throw new NotFoundException("情节节点不存在");
        }

        // 验证权限
        Project project = projectMapper.findById(plotNode.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权限删除此情节节点");
        }

        // 删除情节节点
        int result = plotNodeMapper.delete(plotNodeId);
        if (result <= 0) {
            throw new BusinessException("情节节点删除失败");
        }
    }

    @Override
    public int countPlotNodes(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权限访问此项目");
        }

        return plotNodeMapper.countByProjectId(projectId);
    }

    /**
     * 验证情节类型是否有效
     */
    private void validatePlotType(String plotType) {
        if (plotType == null) {
            throw new BusinessException("情节类型不能为空");
        }

        String[] validTypes = {"meeting", "betrayal", "reconciliation", "conflict", "revelation",
                              "transformation", "climax", "resolution", "other"};
        boolean isValid = false;
        for (String type : validTypes) {
            if (type.equals(plotType)) {
                isValid = true;
                break;
            }
        }

        if (!isValid) {
            throw new BusinessException("无效的情节类型: " + plotType);
        }
    }

    /**
     * 验证重要程度是否有效
     */
    private void validateImportance(String importance) {
        if (importance == null) {
            throw new BusinessException("重要程度不能为空");
        }

        String[] validTypes = {"main", "branch", "background"};
        boolean isValid = false;
        for (String type : validTypes) {
            if (type.equals(importance)) {
                isValid = true;
                break;
            }
        }

        if (!isValid) {
            throw new BusinessException("无效的重要程度: " + importance);
        }
    }

    /**
     * 将PlotNode实体转换为PlotNodeResponse
     */
    private PlotNodeResponse convertToResponse(PlotNode plotNode) {
        PlotNodeResponse response = new PlotNodeResponse();
        response.setId(plotNode.getId());
        response.setProjectId(plotNode.getProjectId());
        response.setTitle(plotNode.getTitle());
        response.setDescription(plotNode.getDescription());
        response.setPlotType(plotNode.getPlotType());
        response.setImportance(plotNode.getImportance());
        response.setChapterId(plotNode.getChapterId());
        response.setRelatedCharacters(plotNode.getRelatedCharacters());
        response.setRelatedLocations(plotNode.getRelatedLocations());
        response.setRelatedWorldSettings(plotNode.getRelatedWorldSettings());
        response.setConflictPoints(plotNode.getConflictPoints());
        response.setThemeTags(plotNode.getThemeTags());
        response.setCreatedAt(plotNode.getCreatedAt());
        response.setUpdatedAt(plotNode.getUpdatedAt());
        return response;
    }
}