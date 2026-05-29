package com.novel.ai.model.entity;

import java.time.LocalDateTime;

public class Chapter {
    private Integer id;
    private Integer projectId;
    private Integer chapterNumber;
    private String title;
    private String volume;
    private String content;
    private String outline;
    private String summary;
    private String displaySummary;
    private Integer povCharacterId;
    private String featuredCharacters;
    private String locations;
    private String status;
    private Integer wordCount;
    private Integer version;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    // Constructors
    public Chapter() {}

    public Chapter(Integer projectId, Integer chapterNumber, String title) {
        this.projectId = projectId;
        this.chapterNumber = chapterNumber;
        this.title = title;
        this.status = "draft";
        this.wordCount = 0;
        this.version = 1;
    }

    // Getters and Setters
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

    public Integer getChapterNumber() {
        return chapterNumber;
    }

    public void setChapterNumber(Integer chapterNumber) {
        this.chapterNumber = chapterNumber;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getVolume() {
        return volume;
    }

    public void setVolume(String volume) {
        this.volume = volume;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
        // Auto-calculate word count when content is set
        if (content != null) {
            this.wordCount = content.length();
        }
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

    public Integer getWordCount() {
        return wordCount;
    }

    public void setWordCount(Integer wordCount) {
        this.wordCount = wordCount;
    }

    public Integer getVersion() {
        return version;
    }

    public void setVersion(Integer version) {
        this.version = version;
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