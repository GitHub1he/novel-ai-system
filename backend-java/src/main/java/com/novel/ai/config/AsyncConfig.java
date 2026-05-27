package com.novel.ai.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;

import java.util.concurrent.Executor;

@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean(name = "taskExecutor")
    public Executor taskExecutor() {
        // Note: Using regular thread pool for Java 17 compatibility
        // Virtual threads require Java 21+
        return java.util.concurrent.Executors.newFixedThreadPool(20);
    }
}