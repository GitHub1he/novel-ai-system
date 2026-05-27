package com.novel.ai.database;

import org.junit.jupiter.api.Test;
import org.springframework.test.context.TestPropertySource;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

import static org.junit.jupiter.api.Assertions.*;

@TestPropertySource(locations = "classpath:application.yml")
public class DatabaseConnectionTest {

    private final String jdbcUrl = "jdbc:postgresql://localhost:5432/novel_ai_db";
    private final String username = "novel_ai_user";
    private final String password = "novel_ai_password";

    @Test
    void testDatabaseConnection() throws Exception {
        try (Connection conn = DriverManager.getConnection(jdbcUrl, username, password)) {
            assertNotNull(conn, "Database connection should not be null");
            assertTrue(conn.isValid(5), "Connection should be valid");
            System.out.println("✅ 数据库连接成功");
        }
    }

    @Test
    void testDatabaseQuery() throws Exception {
        try (Connection conn = DriverManager.getConnection(jdbcUrl, username, password);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT 1")) {

            assertTrue(rs.next(), "Query should return at least one row");
            int result = rs.getInt(1);
            assertEquals(1, result, "Query should return 1");
            System.out.println("✅ 数据库查询测试成功");
        }
    }
}