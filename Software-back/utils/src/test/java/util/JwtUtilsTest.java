package util;

import io.jsonwebtoken.Jwts;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class JwtUtilsTest {
    @AfterEach
    void clearSecret() {
        System.clearProperty("walle.jwt.secret");
    }

    @Test
    void configuredSecretSignsTokensAndRejectsPublicLegacyKey() throws Exception {
        System.setProperty("walle.jwt.secret", "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY=");
        String token = JwtUtils.createJwt(Map.of("id", 123));
        assertThat(JwtUtils.parseJwt(token).get("id")).isEqualTo(123);
        assertThatThrownBy(() -> Jwts.parser().setSigningKey("TEhUIGlzIHlvdSBmYXRoZXI=")
                .parseClaimsJws(token)).isInstanceOf(Exception.class);
    }
}
