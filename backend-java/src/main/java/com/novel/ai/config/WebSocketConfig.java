package com.novel.ai.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.*;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // WebSocket端点，用于AI生成进度推送
        registry.addEndpoint("/ws/chapters/generate")
                .setAllowedOriginPatterns("*")
                .withSockJS();
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        // 启用简单消息代理
        registry.enableSimpleBroker("/topic");
        // 设置应用目的地前缀
        registry.setApplicationDestinationPrefixes("/app");
    }
}