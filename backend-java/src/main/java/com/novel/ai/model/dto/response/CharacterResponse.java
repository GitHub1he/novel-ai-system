package com.novel.ai.model.dto.response;

import java.time.LocalDateTime;

/**
 * 人物响应DTO
 */
public class CharacterResponse {

    private Integer id;
    private Integer projectId;
    private String name;
    private Integer age;
    private String gender;
    private String appearance;
    private String identity;
    private String hometown;
    private String role;
    private String personality;
    private String coreMotivation;
    private String fears;
    private String desires;
    private String characterArcs;
    private String voiceStyles;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

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