package com.novel.ai.config;

import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

import javax.sql.DataSource;

@Configuration
@MapperScan("com.novel.ai.repository.mapper")
public class MyBatisConfig {

    @Bean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        SqlSessionFactoryBean factory = new SqlSessionFactoryBean();
        factory.setDataSource(dataSource);

        // Try to load mapper files if they exist, don't fail if they don't
        try {
            factory.setMapperLocations(
                    new PathMatchingResourcePatternResolver().getResources("classpath:mapper/*.xml")
            );
        } catch (Exception e) {
            // No mapper files found yet, that's okay for now
            System.out.println("No MyBatis mapper files found, will be created when needed");
        }

        org.apache.ibatis.session.Configuration configuration =
                new org.apache.ibatis.session.Configuration();
        configuration.setMapUnderscoreToCamelCase(true);
        configuration.setLogImpl(org.apache.ibatis.logging.stdout.StdOutImpl.class);

        factory.setConfiguration(configuration);
        return factory.getObject();
    }
}