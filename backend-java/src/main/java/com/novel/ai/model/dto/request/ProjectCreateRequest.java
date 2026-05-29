package com.novel.ai.model.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class ProjectCreateRequest {

    @NotBlank(message = "标题不能为空")
    @Size(max = 200, message = "标题长度不能超过200字符")
    private String title;

    @NotBlank(message = "作者名不能为空")
    @Size(max = 100, message = "作者名长度不能超过100字符")
    private String author;

    @Size(max = 500, message = "类型长度不能超过500字符")
    private String genre;

    @Size(max = 500, message = "标签长度不能超过500字符")
    private String tags;

    @Size(max = 2000, message = "简介长度不能超过2000字符")
    private String summary;

    @Size(max = 200, message = "目标读者长度不能超过200字符")
    private String targetReaders;

    @Size(max = 50, message = "默认视角长度不能超过50字符")
    private String defaultPov;

    @Size(max = 100, message = "文风预设长度不能超过100字符")
    private String style;

    @Size(max = 500, message = "文风关键词长度不能超过500字符")
    private String styleKeywords;

    @Size(max = 100, message = "语言风格长度不能超过100字符")
    private String languageStyle;

    @Size(max = 500, message = "感官重点长度不能超过500字符")
    private String sensoryFocus;

    private Integer styleIntensity;

    private Integer targetWordsPerChapter;

    @Size(max = 2000, message = "背景模板长度不能超过2000字符")
    private String backgroundTemplate;

    // Getters and Setters
    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getAuthor() {
        return author;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    public String getGenre() {
        return genre;
    }

    public void setGenre(String genre) {
        this.genre = genre;
    }

    public String getTags() {
        return tags;
    }

    public void setTags(String tags) {
        this.tags = tags;
    }

    public String getSummary() {
        return summary;
    }

    public void setSummary(String summary) {
        this.summary = summary;
    }

    public String getTargetReaders() {
        return targetReaders;
    }

    public void setTargetReaders(String targetReaders) {
        this.targetReaders = targetReaders;
    }

    public String getDefaultPov() {
        return defaultPov;
    }

    public void setDefaultPov(String defaultPov) {
        this.defaultPov = defaultPov;
    }

    public String getStyle() {
        return style;
    }

    public void setStyle(String style) {
        this.style = style;
    }

    public String getStyleKeywords() {
        return styleKeywords;
    }

    public void setStyleKeywords(String styleKeywords) {
        this.styleKeywords = styleKeywords;
    }

    public String getLanguageStyle() {
        return languageStyle;
    }

    public void setLanguageStyle(String languageStyle) {
        this.languageStyle = languageStyle;
    }

    public String getSensoryFocus() {
        return sensoryFocus;
    }

    public void setSensoryFocus(String sensoryFocus) {
        this.sensoryFocus = sensoryFocus;
    }

    public Integer getStyleIntensity() {
        return styleIntensity;
    }

    public void setStyleIntensity(Integer styleIntensity) {
        this.styleIntensity = styleIntensity;
    }

    public Integer getTargetWordsPerChapter() {
        return targetWordsPerChapter;
    }

    public void setTargetWordsPerChapter(Integer targetWordsPerChapter) {
        this.targetWordsPerChapter = targetWordsPerChapter;
    }

    public String getBackgroundTemplate() {
        return backgroundTemplate;
    }

    public void setBackgroundTemplate(String backgroundTemplate) {
        this.backgroundTemplate = backgroundTemplate;
    }
}