package com.novel.ai.security.password;

import org.springframework.stereotype.Component;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.SecureRandom;
import java.security.spec.KeySpec;
import java.util.Base64;

@Component
public class PasswordEncoder {

    private static final int ITERATIONS = 10000;
    private static final int KEY_LENGTH = 256;
    private static final String ALGORITHM = "PBKDF2WithHmacSHA256";
    private final SecureRandom secureRandom = new SecureRandom();

    /**
     * 加密密码
     * @param rawPassword 原始密码
     * @return 加密后的密码 (格式: salt:hash)
     */
    public String encode(String rawPassword) {
        byte[] salt = generateSalt();
        byte[] hash = hashPassword(rawPassword, salt);

        String saltBase64 = Base64.getEncoder().encodeToString(salt);
        String hashBase64 = Base64.getEncoder().encodeToString(hash);

        return saltBase64 + ":" + hashBase64;
    }

    /**
     * 验证密码
     * @param rawPassword 原始密码
     * @param encodedPassword 加密后的密码
     * @return 是否匹配
     */
    public boolean matches(String rawPassword, String encodedPassword) {
        try {
            String[] parts = encodedPassword.split(":");
            if (parts.length != 2) {
                return false;
            }

            byte[] salt = Base64.getDecoder().decode(parts[0]);
            byte[] expectedHash = Base64.getDecoder().decode(parts[1]);
            byte[] actualHash = hashPassword(rawPassword, salt);

            return java.util.Arrays.equals(expectedHash, actualHash);
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * 生成随机盐值
     */
    private byte[] generateSalt() {
        byte[] salt = new byte[16];
        secureRandom.nextBytes(salt);
        return salt;
    }

    /**
     * 使用PBKDF2算法哈希密码
     */
    private byte[] hashPassword(String password, byte[] salt) {
        try {
            KeySpec spec = new PBEKeySpec(password.toCharArray(), salt, ITERATIONS, KEY_LENGTH);
            SecretKeyFactory factory = SecretKeyFactory.getInstance(ALGORITHM);
            return factory.generateSecret(spec).getEncoded();
        } catch (Exception e) {
            throw new RuntimeException("Password hashing failed", e);
        }
    }
}