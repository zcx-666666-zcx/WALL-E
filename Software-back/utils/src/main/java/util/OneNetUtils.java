package util;

import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;

/**
 * OneNET 推送相关工具方法。
 *
 * 说明：
 * - URL 验证与消息签名校验算法来自 OneNET 官方文档「开发指南」。
 * - 校验公式：
 *   A = token + nonce + msg
 *   B = MD5(A) 的二进制摘要
 *   C = Base64(B) 再进行 URL Decode
 *   若 C 与 signature 相等，则认为签名校验通过。
 */
public class OneNetUtils {

    /**
     * 根据 OneNET 文档计算签名，并与请求中的 signature 进行比对。
     *
     * @param token     在 OneNET 平台配置的 token
     * @param msg       请求中的 msg 参数（明文或密文原始字符串，不做任何前置处理）
     * @param nonce     请求中的 nonce 参数（8 字节随机串）
     * @param signature 请求中的 signature 参数
     * @return true 表示签名校验通过；false 表示校验失败
     */
    public static boolean checkSignature(String token, String msg, String nonce, String signature) {
        if (token == null || msg == null || nonce == null || signature == null) {
            return false;
        }

        try {
            String A = token + nonce + msg;

            MessageDigest messageDigest = MessageDigest.getInstance("MD5");
            byte[] digest = messageDigest.digest(A.getBytes(StandardCharsets.UTF_8));

            String base64 = Base64.getEncoder().encodeToString(digest);

            String calculatedSignature = URLDecoder.decode(base64, StandardCharsets.UTF_8);

            return calculatedSignature.equals(signature);
        } catch (NoSuchAlgorithmException e) {
            return false;
        }
    }
}

