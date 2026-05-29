package com.novel.ai.service;

import com.novel.ai.config.AIConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.SystemMessage;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.stereotype.Service;

@Service
public class AISpringServiceImpl implements AIService {

    private static final Logger logger = LoggerFactory.getLogger(AISpringServiceImpl.class);

    private final ChatClient.Builder chatClientBuilder;
    private final AIConfig aiConfig;

    public AISpringServiceImpl(ChatClient.Builder chatClientBuilder, AIConfig aiConfig) {
        this.chatClientBuilder = chatClientBuilder;
        this.aiConfig = aiConfig;
    }

    @Override
    public String generateContent(String prompt, String context) {
        String fullPrompt = buildFullPrompt(prompt, context);
        return callAI(fullPrompt);
    }

    @Override
    public String generateOutline(String prompt, String context) {
        String systemPrompt = "你是一个专业的小说大纲创作助手。请根据用户提供的信息创作详细的章节大纲。";
        String fullPrompt = systemPrompt + "\n\n" + buildFullPrompt(prompt, context);
        return callAI(fullPrompt);
    }

    @Override
    public String expandContent(String content, int targetWords, String context) {
        String prompt = String.format(
                "请将以下内容扩展到大约%d字，保持原有的风格和情节走向：\n\n%s\n\n" +
                        "要求：\n" +
                        "1. 保持原有风格和语调\n" +
                        "2. 增加细节描写和对话\n" +
                        "3. 延伸情节发展\n" +
                        "4. 保持逻辑连贯",
                targetWords, content
        );

        String fullPrompt = buildFullPrompt(prompt, context);
        return callAI(fullPrompt);
    }

    @Override
    public String generateSummary(String content, String title) {
        String prompt = String.format(
                "请为以下章节生成摘要（用于续写参考）：\n\n标题：%s\n\n内容：\n%s\n\n" +
                        "要求：\n" +
                        "1. 提取主要情节发展\n" +
                        "2. 包含关键对话和事件\n" +
                        "3. 便于后续章节续写参考\n" +
                        "4. 控制在300字以内",
                title, content
        );

        return callAI(prompt);
    }

    @Override
    public String generateDisplaySummary(String content, String title) {
        String prompt = String.format(
                "请为以下章节生成展示摘要（用于前端页面显示）：\n\n标题：%s\n\n内容：\n%s\n\n" +
                        "要求：\n" +
                        "1. 吸引读者兴趣\n" +
                        "2. 突出章节亮点\n" +
                        "3. 不透露关键剧情转折\n" +
                        "4. 控制在100字以内",
                title, content
        );

        return callAI(prompt);
    }

    @Override
    public String continueWriting(String existingContent, String context, int targetLength) {
        String prompt = String.format(
                "请根据以下现有内容进行续写，目标长度约%d字：\n\n现有内容：\n%s\n\n" +
                        "要求：\n" +
                        "1. 保持风格连贯\n" +
                        "2. 自然承接现有内容\n" +
                        "3. 推进情节发展\n" +
                        "4. 保持人物性格一致性",
                targetLength, existingContent
        );

        String fullPrompt = buildFullPrompt(prompt, context);
        return callAI(fullPrompt);
    }

    /**
     * 构建完整的提示词
     */
    private String buildFullPrompt(String userPrompt, String context) {
        StringBuilder fullPrompt = new StringBuilder();

        if (context != null && !context.trim().isEmpty()) {
            fullPrompt.append("## 上下文信息\n");
            fullPrompt.append(context);
            fullPrompt.append("\n\n");
        }

        fullPrompt.append("## 用户请求\n");
        fullPrompt.append(userPrompt);

        return fullPrompt.toString();
    }

    /**
     * 调用AI服务
     */
    private String callAI(String prompt) {
        try {
            logger.info("Calling AI service with prompt length: {}", prompt.length());

            // 创建系统消息和用户消息
            Message systemMessage = new SystemMessage("你是一个专业的小说创作助手，擅长各种类型的小说写作。");
            Message userMessage = new UserMessage(prompt);

            // 构建完整的Prompt
            Prompt fullPrompt = new Prompt(java.util.List.of(systemMessage, userMessage));

            // 调用AI服务
            String response = chatClientBuilder
                    .build()
                    .prompt(fullPrompt)
                    .call()
                    .content();

            logger.info("AI response received, length: {}", response.length());
            return response;

        } catch (Exception e) {
            logger.error("Error calling AI service: {}", e.getMessage(), e);
            throw new RuntimeException("AI服务调用失败: " + e.getMessage(), e);
        }
    }

    /**
     * 带自定义温度参数的AI调用
     */
    private String callAIWithTemperature(String prompt, double temperature) {
        try {
            logger.info("Calling AI service with temperature: {}", temperature);

            Message systemMessage = new SystemMessage("你是一个专业的小说创作助手，擅长各种类型的小说写作。");
            Message userMessage = new UserMessage(prompt);

            Prompt fullPrompt = new Prompt(java.util.List.of(systemMessage, userMessage));

            // 这里可以添加温度参数的支持
            // 目前Spring AI的默认配置使用application.yml中的设置
            String response = chatClientBuilder
                    .build()
                    .prompt(fullPrompt)
                    .call()
                    .content();

            logger.info("AI response received with temperature: {}, length: {}", temperature, response.length());
            return response;

        } catch (Exception e) {
            logger.error("Error calling AI service with temperature: {}", temperature, e);
            throw new RuntimeException("AI服务调用失败: " + e.getMessage(), e);
        }
    }

    /**
     * 检查AI服务是否可用
     */
    public boolean isAvailable() {
        try {
            String testResponse = callAI("测试连接");
            return testResponse != null && !testResponse.isEmpty();
        } catch (Exception e) {
            logger.warn("AI service not available: {}", e.getMessage());
            return false;
        }
    }
}