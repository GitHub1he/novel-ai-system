package com.novel.ai.model.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class AIGenerateRequest {

    @Size(max = 10000, message = "提示词长度不能超过10000字符")
    private String prompt;

    @Size(max = 50000, message = "内容长度不能超过50000字符")
    private String content;

    @Size(max = 5000, message = "上下文长度不能超过5000字符")
    private String context;

    @Size(max = 200, message = "标题长度不能超过200字符")
    private String title;

    private Integer targetWords;

    private Integer targetLength;

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

    public String getContext() {
        return context;
    }

    public void setContext(String context) {
        this.context = context;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public Integer getTargetWords() {
        return targetWords;
    }

    public void setTargetWords(Integer targetWords) {
        this.targetWords = targetWords;
    }

    public Integer getTargetLength() {
        return targetLength;
    }

    public void setTargetLength(Integer targetLength) {
        this.targetLength = targetLength;
    }
}