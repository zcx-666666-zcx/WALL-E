package util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.util.Date;
import java.util.Map;

public class JwtUtils {

    private static final String LEGACY_JWT_SECRET_KEY = "TEhUIGlzIHlvdSBmYXRoZXI=";
    private static final long JWT_EXPIRED_TIME = 7L * 24 * 60 * 60 * 1000;

    public static String createJwt(Map<String, Object> claims){
        return Jwts.builder().signWith(SignatureAlgorithm.HS256, signingKey())
                .addClaims(claims)
                .setExpiration(new Date(System.currentTimeMillis() + JWT_EXPIRED_TIME))
                .compact();
    }

    public static Claims parseJwt(String token) throws Exception{
        return Jwts.parser().setSigningKey(signingKey()).
                parseClaimsJws(token).
                getBody();
    }

    private static String signingKey() {
        String configured = System.getProperty("walle.jwt.secret");
        if (configured == null || configured.isBlank()) {
            configured = System.getenv("WALLE_JWT_SECRET");
        }
        return configured == null || configured.isBlank() ? LEGACY_JWT_SECRET_KEY : configured;
    }
}
