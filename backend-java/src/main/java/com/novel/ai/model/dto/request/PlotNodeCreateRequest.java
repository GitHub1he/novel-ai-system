package com.novel.ai.model.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * 情节节点创建请求DTO
 */
public class PlotNodeCreateRequest {

    @NotNull(message = "项目ID不能为空")
    private Integer projectId;

    @NotBlank(message = "情节节点标题不能为空")
    @Size(max = 200, message = "标题长度不能超过200字符")
    private String title;

    @Size(max = 2000, message = "描述长度不能超过2000字符")
    private String description;

    @Size(max = 20, message = "情节类型长度不能超过20字符")
    private String plotType; // meeting/betrayal/reconciliation/conflict/revelation/transformation/climax/resolution/other

    @Size(max = 20, message = "重要程度长度不能超过20字符")
    private String importance; // main/branch/background

    private Integer chapterId;

    private String relatedCharacters; // JSON数组格式

    private String relatedLocations; // JSON数组格式

    private String relatedWorldSettings; // JSON数组格式

    @Size(max = 1000, message = "冲突点描述长度不能超过1000字符")
    private String conflictPoints;

    private String themeTags; // JSON数组格式

    // Getter和Setter方法
    public Integer getProjectId() {
        return projectId;
    }

    public void setProjectId(Integer projectId) {
        this.projectId = projectId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getPlotType() {
        return plotType;
    }

    public void setPlotType(String plotType) {
        this.plotType = plotType;
    }

    public String getImportance() {
        return importance;
    }

    public void setImportance(String importance) {
        this.importance = importance;
    }

    public Integer getChapterId() {
        return chapterId;
    }

    public void setChapterId(Integer chapterId) {
        this.chapterId = chapterId;
    }

    public String getRelatedCharacters() {
        return relatedCharacters;
    }

    public void setRelatedCharacters(String relatedCharacters) {
        this.relatedCharacters = relatedCharacters;
    }

    public String getRelatedLocations() {
        return relatedLocations;
    }

    public void setRelatedLocations(String relatedLocations) {
        this.relatedLocations = relatedLocations;
    }

    public String getRelatedWorldSettings() {
        return relatedWorldSettings;
    }

    public void setRelatedWorldSettings(String relatedWorldSettings) {
        this.relatedWorldSettings = relatedWorldSettings;
    }

    public String getConflictPoints() {
        return conflictPoints;
    }

    public void setConflictPoints(String conflictPoints) {
        this.conflictPoints = conflictPoints;
    }

    public String getThemeTags() {
        return themeTags;
    }

    public void setThemeTags(String themeTags) {
        this.themeTags = themeTags;
    }
}