package com.novel.ai.model.entity;

import java.time.LocalDateTime;

/**
 * 人物实体类
 * 用于存储小说项目中的人物信息，包括基础信息、核心人设、人物弧光、语音风格等
 */
public class Character {

    // 基础字段
    private Integer id;
    private Integer projectId;

    // 基础信息
    private String name;
    private Integer age;
    private String gender;
    private String appearance;      // 外貌描述
    private String identity;        // 身份
    private String hometown;        // 籍贯

    // 核心人设
    private String role;            // 角色类型：protagonist/antagonist/supporting/minor
    private String personality;    // 性格标签，JSON格式
    private String coreMotivation;  // 核心动机
    private String fears;           // 恐惧
    private String desires;         // 欲望

    // 人物弧光 - JSON格式存储多条转变记录
    // 示例：[{"period": "初期", "event": "关键事件", "before": "转变前", "after": "转变后"}]
    private String characterArcs;

    // 语音风格 - JSON格式存储多场景风格记录
    // 示例：[{"target": "对话对象", "scenario": "场景", "style": "风格", "sample": "样本对话"}]
    private String voiceStyles;

    // 时间戳
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    // 构造函数
    public Character() {}

    public Character(Integer projectId, String name) {
        this.projectId = projectId;
        this.name = name;
        this.role = "supporting";  // 默认为配角
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

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public String getGender() {
        return gender;
    }

    public void setGender(String gender) {
        this.gender = gender;
    }

    public String getAppearance() {
        return appearance;
    }

    public void setAppearance(String appearance) {
        this.appearance = appearance;
    }

    public String getIdentity() {
        return identity;
    }

    public void setIdentity(String identity) {
        this.identity = identity;
    }

    public String getHometown() {
        return hometown;
    }

    public void setHometown(String hometown) {
        this.hometown = hometown;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public String getPersonality() {
        return personality;
    }

    public void setPersonality(String personality) {
        this.personality = personality;
    }

    public String getCoreMotivation() {
        return coreMotivation;
    }

    public void setCoreMotivation(String coreMotivation) {
        this.coreMotivation = coreMotivation;
    }

    public String getFears() {
        return fears;
    }

    public void setFears(String fears) {
        this.fears = fears;
    }

    public String getDesires() {
        return desires;
    }

    public void setDesires(String desires) {
        this.desires = desires;
    }

    public String getCharacterArcs() {
        return characterArcs;
    }

    public void setCharacterArcs(String characterArcs) {
        this.characterArcs = characterArcs;
    }

    public String getVoiceStyles() {
        return voiceStyles;
    }

    public void setVoiceStyles(String voiceStyles) {
        this.voiceStyles = voiceStyles;
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