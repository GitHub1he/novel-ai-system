package com.novel.ai.service;

public interface AIService {

    /**
     * 生成章节内容
     *
     * @param prompt 用户提示词
     * @param context 上下文信息
     * @return AI生成的内容
     */
    String generateContent(String prompt, String context);

    /**
     * 生成章节大纲
     *
     * @param prompt 用户提示词
     * @param context 上下文信息
     * @return AI生成的大纲
     */
    String generateOutline(String prompt, String context);

    /**
     * 扩展内容
     *
     * @param content 原始内容
     * @param targetWords 目标字数
     * @param context 上下文信息
     * @return 扩展后的内容
     */
    String expandContent(String content, int targetWords, String context);

    /**
     * 生成章节摘要
     *
     * @param content 章节内容
     * @param title 章节标题
     * @return 生成的摘要
     */
    String generateSummary(String content, String title);

    /**
     * 生成展示摘要（用于前端显示）
     *
     * @param content 章节内容
     * @param title 章节标题
     * @return 生成的展示摘要
     */
    String generateDisplaySummary(String content, String title);

    /**
     * 智能续写
     *
     * @param existingContent 现有内容
     * @param context 上下文信息
     * @param targetLength 目标长度
     * @return 续写的内容
     */
    String continueWriting(String existingContent, String context, int targetLength);
}