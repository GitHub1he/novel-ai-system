package com.novel.ai.model.dto.response;

import java.time.LocalDateTime;

/**
 * 情节节点响应DTO
 */
public class PlotNodeResponse {

    private Integer id;
    private Integer projectId;
    private String title;
    private String description;
    private String plotType;
    private String importance;
    private Integer chapterId;
    private String relatedCharacters;
    private String relatedLocations;
    private String relatedWorldSettings;
    private String conflictPoints;
    private String themeTags;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

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
}