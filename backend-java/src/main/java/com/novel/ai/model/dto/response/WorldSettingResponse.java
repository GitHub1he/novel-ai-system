package com.novel.ai.model.dto.response;

import java.time.LocalDateTime;

/**
 * 世界观设定响应DTO
 */
public class WorldSettingResponse {

    private Integer id;
    private Integer projectId;
    private String name;
    private String settingType;
    private String description;
    private String attributes;
    private String relatedEntities;
    private Integer isCoreRule;
    private String image;
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

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getSettingType() {
        return settingType;
    }

    public void setSettingType(String settingType) {
        this.settingType = settingType;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getAttributes() {
        return attributes;
    }

    public void setAttributes(String attributes) {
        this.attributes = attributes;
    }

    public String getRelatedEntities() {
        return relatedEntities;
    }

    public void setRelatedEntities(String relatedEntities) {
        this.relatedEntities = relatedEntities;
    }

    public Integer getIsCoreRule() {
        return isCoreRule;
    }

    public void setIsCoreRule(Integer isCoreRule) {
        this.isCoreRule = isCoreRule;
    }

    public String getImage() {
        return image;
    }

    public void setImage(String image) {
        this.image = image;
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