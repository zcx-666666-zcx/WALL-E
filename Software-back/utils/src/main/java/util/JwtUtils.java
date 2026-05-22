package util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.util.Date;
import java.util.Map;

public class JwtUtils {

    private static final String JWT_SECRET_KEY = "TEhUIGlzIHlvdSBmYXRoZXI=";
    private static final long JWT_EXPIRED_TIME = 1800*1000;

    public static String createJwt(Map<String, Object> claims){
        return Jwts.builder().signWith(SignatureAlgorithm.HS256, JWT_SECRET_KEY)
                .addClaims(claims)
                .setExpiration(new Date(System.currentTimeMillis() + JWT_EXPIRED_TIME))
                .compact();
    }

    public static Claims parseJwt(String token) throws Exception{
        return Jwts.parser().setSigningKey(JWT_SECRET_KEY).
                parseClaimsJws(token).
                getBody();
    }
}
