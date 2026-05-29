package com.novel.ai.model.dto.response;

import java.util.Map;

public class ChapterGenerationResponse {

    private String taskId;
    private String content;
    private Map<Integer, String> versions;
    private Integer wordCount;
    private Integer versionCount;
    private String error;
    private String status; // generating, completed, error

    // Getters and Setters
    public String getTaskId() {
        return taskId;
    }

    public void setTaskId(String taskId) {
        this.taskId = taskId;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public Map<Integer, String> getVersions() {
        return versions;
    }

    public void setVersions(Map<Integer, String> versions) {
        this.versions = versions;
    }

    public Integer getWordCount() {
        return wordCount;
    }

    public void setWordCount(Integer wordCount) {
        this.wordCount = wordCount;
    }

    public Integer getVersionCount() {
        return versionCount;
    }

    public void setVersionCount(Integer versionCount) {
        this.versionCount = versionCount;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}