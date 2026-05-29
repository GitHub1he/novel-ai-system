package com.novel.ai.model.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class ChapterUpdateRequest {

    @NotBlank(message = "章节标题不能为空")
    @Size(max = 200, message = "章节标题长度不能超过200字符")
    private String title;

    @Size(max = 100000, message = "章节内容长度不能超过100000字符")
    private String content;

    @Size(max = 10000, message = "大纲长度不能超过10000字符")
    private String outline;

    @Size(max = 2000, message = "摘要长度不能超过2000字符")
    private String summary;

    @Size(max = 200, message = "展示摘要长度不能超过200字符")
    private String displaySummary;

    @Size(max = 100, message = "卷名长度不能超过100字符")
    private String volume;

    private Integer povCharacterId;

    @Size(max = 500, message = "出场人物长度不能超过500字符")
    private String featuredCharacters;

    @Size(max = 500, message = "场景地点长度不能超过500字符")
    private String locations;

    @Size(max = 50, message = "状态长度不能超过50字符")
    private String status;

    // Getters and Setters
    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getOutline() {
        return outline;
    }

    public void setOutline(String outline) {
        this.outline = outline;
    }

    public String getSummary() {
        return summary;
    }

    public void setSummary(String summary) {
        this.summary = summary;
    }

    public String getDisplaySummary() {
        return displaySummary;
    }

    public void setDisplaySummary(String displaySummary) {
        this.displaySummary = displaySummary;
    }

    public String getVolume() {
        return volume;
    }

    public void setVolume(String volume) {
        this.volume = volume;
    }

    public Integer getPovCharacterId() {
        return povCharacterId;
    }

    public void setPovCharacterId(Integer povCharacterId) {
        this.povCharacterId = povCharacterId;
    }

    public String getFeaturedCharacters() {
        return featuredCharacters;
    }

    public void setFeaturedCharacters(String featuredCharacters) {
        this.featuredCharacters = featuredCharacters;
    }

    public String getLocations() {
        return locations;
    }

    public void setLocations(String locations) {
        this.locations = locations;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}