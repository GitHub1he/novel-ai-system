package com.novel.ai.model.entity;

import java.time.LocalDateTime;

/**
 * 世界观设定实体类
 * 用于存储小说项目的世界观设定信息，包括时代、地域、规则、文化、地点、势力、物品、历史事件等
 */
public class WorldSetting {

    // 基础字段
    private Integer id;
    private Integer projectId;

    // 基础信息
    private String name;
    private String settingType;      // 设定类型：era/region/rule/culture/power/location/faction/item/event
    private String description;      // 详细描述

    // 扩展属性（JSON格式，灵活存储不同类型的属性）
    // 示例：{"level": "高级", "effect": "...", "requirements": "..."}
    private String attributes;

    // 关联关系（JSON数组格式）
    // 示例：[{"type": "character", "id": 1}, {"type": "location", "id": 2}]
    private String relatedEntities;

    // 是否为核心规则（核心规则不可变更）
    private Integer isCoreRule;

    // 图片URL
    private String image;

    // 时间戳
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    // 构造函数
    public WorldSetting() {}

    public WorldSetting(Integer projectId, String name, String settingType) {
        this.projectId = projectId;
        this.name = name;
        this.settingType = settingType;
        this.isCoreRule = 0; // 默认不是核心规则
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

    /**
     * 检查是否为核心规则
     */
    public boolean isCoreRule() {
        return this.isCoreRule != null && this.isCoreRule == 1;
    }
}