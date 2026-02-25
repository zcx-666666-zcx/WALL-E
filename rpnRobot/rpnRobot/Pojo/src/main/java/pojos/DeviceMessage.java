package pojos;

/**
 * 用于存储 OneNET 推送到本系统的原始消息。
 *
 * 对应数据库中的 device_message 表，字段建议如下：
 *   id           INT AUTO_INCREMENT PRIMARY KEY
 *   msg          TEXT             -- OneNET 推送中的 msg 字段（可为 JSON 文本）
 *   nonce        VARCHAR(32)      -- OneNET 推送中的 nonce
 *   signature    VARCHAR(128)     -- OneNET 推送中的 signature
 *   push_time    BIGINT           -- OneNET 推送中的 time（毫秒时间戳）
 *   message_id   VARCHAR(64)      -- OneNET 推送中的 id
 */
public class DeviceMessage {

    private Integer id;
    private String msg;
    private String nonce;
    private String signature;
    private Long pushTime;
    private String messageId;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

    public String getNonce() {
        return nonce;
    }

    public void setNonce(String nonce) {
        this.nonce = nonce;
    }

    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }

    public Long getPushTime() {
        return pushTime;
    }

    public void setPushTime(Long pushTime) {
        this.pushTime = pushTime;
    }

    public String getMessageId() {
        return messageId;
    }

    public void setMessageId(String messageId) {
        this.messageId = messageId;
    }
}

