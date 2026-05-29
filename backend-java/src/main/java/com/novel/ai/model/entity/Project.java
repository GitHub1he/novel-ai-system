package com.novel.ai.model.entity;

import java.time.LocalDateTime;

public class Project {
    private Integer id;
    private Integer userId;
    private String title;
    private String author;
    private String genre;
    private String tags;
    private String summary;
    private String targetReaders;
    private String status;
    private String defaultPov;
    private String style;
    private String styleKeywords;
    private String languageStyle;
    private String sensoryFocus;
    private Integer styleIntensity;
    private Integer targetWordsPerChapter;
    private String backgroundTemplate;
    private Integer totalWords;
    private Integer totalChapters;
    private Integer completionRate;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    // Constructors
    public Project() {}

    public Project(Integer userId, String title, String author) {
        this.userId = userId;
        this.title = title;
        this.author = author;
        this.status = "draft";
        this.styleIntensity = 70;
        this.targetWordsPerChapter = 2000;
        this.totalWords = 0;
        this.totalChapters = 0;
        this.completionRate = 0;
    }

    // Getters and Setters
    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

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

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
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

    public Integer getTotalWords() {
        return totalWords;
    }

    public void setTotalWords(Integer totalWords) {
        this.totalWords = totalWords;
    }

    public Integer getTotalChapters() {
        return totalChapters;
    }

    public void setTotalChapters(Integer totalChapters) {
        this.totalChapters = totalChapters;
    }

    public Integer getCompletionRate() {
        return completionRate;
    }

    public void setCompletionRate(Integer completionRate) {
        this.completionRate = completionRate;
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