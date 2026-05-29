package com.novel.ai.model.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * 世界观设定创建请求DTO
 */
public class WorldSettingCreateRequest {

    @NotNull(message = "项目ID不能为空")
    private Integer projectId;

    @NotBlank(message = "设定名称不能为空")
    @Size(max = 100, message = "设定名称长度不能超过100字符")
    private String name;

    @NotBlank(message = "设定类型不能为空")
    @Size(max = 20, message = "设定类型长度不能超过20字符")
    private String settingType; // era/region/rule/culture/power/location/faction/item/event

    @Size(max = 2000, message = "描述长度不能超过2000字符")
    private String description;

    private String attributes; // JSON格式

    private String relatedEntities; // JSON数组格式

    private Integer isCoreRule; // 0或1

    @Size(max = 500, message = "图片URL长度不能超过500字符")
    private String image;

    // Getter和Setter方法
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
}