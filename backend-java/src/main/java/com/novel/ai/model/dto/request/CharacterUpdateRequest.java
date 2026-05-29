package com.novel.ai.model.dto.request;

import jakarta.validation.constraints.Size;

/**
 * 人物更新请求DTO
 */
public class CharacterUpdateRequest {

    @Size(max = 100, message = "人物名称长度不能超过100字符")
    private String name;

    private Integer age;

    @Size(max = 20, message = "性别长度不能超过20字符")
    private String gender;

    @Size(max = 1000, message = "外貌描述长度不能超过1000字符")
    private String appearance;

    @Size(max = 100, message = "身份长度不能超过100字符")
    private String identity;

    @Size(max = 100, message = "籍贯长度不能超过100字符")
    private String hometown;

    @Size(max = 20, message = "角色类型长度不能超过20字符")
    private String role; // protagonist/antagonist/supporting/minor

    private String personality; // JSON格式

    @Size(max = 500, message = "核心动机长度不能超过500字符")
    private String coreMotivation;

    @Size(max = 500, message = "恐惧长度不能超过500字符")
    private String fears;

    @Size(max = 500, message = "欲望长度不能超过500字符")
    private String desires;

    private String characterArcs; // JSON格式

    private String voiceStyles; // JSON格式

    // Getter和Setter方法
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
}