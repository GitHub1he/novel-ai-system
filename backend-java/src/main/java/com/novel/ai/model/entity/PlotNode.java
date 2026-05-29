package com.novel.ai.model.entity;

import java.time.LocalDateTime;

/**
 * 情节节点实体类
 * 用于存储小说项目的情节节点信息，包括情节类型、重要程度、关联信息、冲突点、主题标签等
 */
public class PlotNode {

    // 基础字段
    private Integer id;
    private Integer projectId;

    // 基本信息
    private String title;
    private String description;
    private String plotType;        // 情节类型：meeting/betrayal/reconciliation/conflict/revelation/transformation/climax/resolution/other
    private String importance;       // 重要程度：main/branch/background

    // 关联信息
    private Integer chapterId;       // 关联章节ID
    private String relatedCharacters; // 关联人物ID列表（JSON数组）
    private String relatedLocations;  // 关联地点ID列表（JSON数组）
    private String relatedWorldSettings; // 关联世界观ID列表（JSON数组）

    // 情节内容
    private String conflictPoints;  // 冲突点描述
    private String themeTags;       // 主题标签（JSON数组）

    // 时间戳
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    // 构造函数
    public PlotNode() {}

    public PlotNode(Integer projectId, String title) {
        this.projectId = projectId;
        this.title = title;
        this.plotType = "other";     // 默认为其他
        this.importance = "branch";  // 默认为支线
    }

    // Getter和Setter方法
    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

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

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    /**
     * 检查是否为主线情节
     */
    public boolean isMainPlot() {
        return "main".equals(this.importance);
    }

    /**
     * 检查是否为高潮情节
     */
    public boolean isClimax() {
        return "climax".equals(this.plotType);
    }
}