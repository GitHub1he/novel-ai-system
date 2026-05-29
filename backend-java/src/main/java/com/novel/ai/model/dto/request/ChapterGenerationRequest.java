package com.novel.ai.model.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class ChapterGenerationRequest {

    @NotBlank(message = "生成提示词不能为空")
    @Size(max = 10000, message = "提示词长度不能超过10000字符")
    private String prompt;

    @Size(max = 100000, message = "现有内容长度不能超过100000字符")
    private String content;

    @Size(max = 200, message = "章节标题长度不能超过200字符")
    private String title;

    @Size(max = 100, message = "类型长度不能超过100字符")
    private String genre;

    @Size(max = 200, message = "风格描述长度不能超过200字符")
    private String style;

    @Size(max = 50000, message = "项目信息长度不能超过50000字符")
    private String projectInfo;

    @Size(max = 10000, message = "人物设定长度不能超过10000字符")
    private String characters;

    @Size(max = 10000, message = "世界观设定长度不能超过10000字符")
    private String worldSettings;

    @Size(max = 5000, message = "前情提要长度不能超过5000字符")
    private String previousChapter;

    private Integer targetWords;
    private Double temperature;
    private String mode; // simple, standard, advanced

    // Getters and Setters
    public String getPrompt() {
        return prompt;
    }

    public void setPrompt(String prompt) {
        this.prompt = prompt;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getGenre() {
        return genre;
    }

    public void setGenre(String genre) {
        this.genre = genre;
    }

    public String getStyle() {
        return style;
    }

    public void setStyle(String style) {
        this.style = style;
    }

    public String getProjectInfo() {
        return projectInfo;
    }

    public void setProjectInfo(String projectInfo) {
        this.projectInfo = projectInfo;
    }

    public String getCharacters() {
        return characters;
    }

    public void setCharacters(String characters) {
        this.characters = characters;
    }

    public String getWorldSettings() {
        return worldSettings;
    }

    public void setWorldSettings(String worldSettings) {
        this.worldSettings = worldSettings;
    }

    public String getPreviousChapter() {
        return previousChapter;
    }

    public void setPreviousChapter(String previousChapter) {
        this.previousChapter = previousChapter;
    }

    public Integer getTargetWords() {
        return targetWords;
    }

    public void setTargetWords(Integer targetWords) {
        this.targetWords = targetWords;
    }

    public Double getTemperature() {
        return temperature;
    }

    public void setTemperature(Double temperature) {
        this.temperature = temperature;
    }

    public String getMode() {
        return mode;
    }

    public void setMode(String mode) {
        this.mode = mode;
    }
}