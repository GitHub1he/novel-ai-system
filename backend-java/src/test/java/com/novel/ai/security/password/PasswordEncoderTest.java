package com.novel.ai.security.password;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class PasswordEncoderTest {

    @Test
    void testEncodePassword() {
        PasswordEncoder encoder = new PasswordEncoder();
        String rawPassword = "testPassword123";

        String encodedPassword = encoder.encode(rawPassword);

        assertNotNull(encodedPassword, "Encoded password should not be null");
        assertNotEquals(rawPassword, encodedPassword, "Encoded password should be different from raw");
        assertTrue(encodedPassword.contains(":"), "Encoded password should contain colons");
    }

    @Test
    void testMatchPassword() {
        PasswordEncoder encoder = new PasswordEncoder();
        String rawPassword = "testPassword123";

        String encodedPassword = encoder.encode(rawPassword);
        boolean matches = encoder.matches(rawPassword, encodedPassword);

        assertTrue(matches, "Password should match");
    }

    @Test
    void testNotMatchPassword() {
        PasswordEncoder encoder = new PasswordEncoder();
        String rawPassword = "testPassword123";
        String wrongPassword = "wrongPassword";

        String encodedPassword = encoder.encode(rawPassword);
        boolean matches = encoder.matches(wrongPassword, encodedPassword);

        assertFalse(matches, "Wrong password should not match");
    }
}