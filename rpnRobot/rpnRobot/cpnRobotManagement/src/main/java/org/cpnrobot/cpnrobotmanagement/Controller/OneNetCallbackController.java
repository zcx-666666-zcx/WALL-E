package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.DeviceMessageService;
import org.cpnrobot.cpnrobotmanagement.Service.SensorDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import pojos.DeviceMessage;
import util.OneNetUtils;

/**
 * OneNET HTTP 数据推送回调接口。
 *
 * 建议在 OneNET 控制台的「数据流转 -> 数据推送」中，将推送地址配置为：
 *   http://你的后端域名或IP:端口/onenet/callback
 *
 * 本 Controller 同时支持：
 * - GET /onenet/callback ：用于 URL 验证（OneNET 创建实例时自动发起）
 * - POST /onenet/callback：用于接收设备数据推送
 */
@RestController
@RequestMapping("/onenet")
@CrossOrigin(origins = "http://localhost:5173")
public class OneNetCallbackController {

    /**
     * 从 application.yml 读取的 OneNET token，用于 URL 验证和消息签名校验。
     */
    @Value("${onenet.token}")
    private String token;

    @Autowired
    private DeviceMessageService deviceMessageService;
    
    @Autowired
    private SensorDataService sensorDataService;

    /**
     * URL 验证接口（GET）。
     *
     * OneNET 会向该地址发送 GET 请求：
     *   http(s)://url?msg=xxx&nonce=xxx&signature=xxx
     *
     * 后端需要按照文档中的算法对 signature 进行校验：
     *   A = token + nonce + msg
     *   B = MD5(A)
     *   C = Base64(B) 再 URL Decode
     *   若 C 等于 signature，则说明请求来自 OneNET，原样返回 msg 即表示 URL 验证通过。
     *
     * @param msg       OneNET 生成的随机字符串
     * @param nonce     OneNET 生成的随机字符串（8 字节）
     * @param signature OneNET 计算出的签名
     * @return 校验通过时原样返回 msg；校验失败时返回 403
     */
    @GetMapping("/callback")
    public ResponseEntity<String> validateUrl(@RequestParam("msg") String msg,
                                              @RequestParam("nonce") String nonce,
                                              @RequestParam("signature") String signature) {

        System.out.println("[OneNET][URL验证] 收到 GET 验证请求");
        System.out.println("[OneNET][URL验证] 请求参数 msg=" + msg + ", nonce=" + nonce + ", signature=" + signature);
        System.out.println("[OneNET][URL验证] 当前使用的 token=" + token);

        boolean ok = OneNetUtils.checkSignature(token, msg, nonce, signature);
        if (!ok) {
            System.out.println("[OneNET][URL验证] 签名校验失败，拒绝本次 URL 验证请求");
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("invalid signature");
        }

        System.out.println("[OneNET][URL验证] 签名校验通过，原样返回 msg，URL 验证成功");

        // 校验通过后，必须原样返回 msg，OneNET 才会认为 URL 验证成功
        return ResponseEntity.ok(msg);
    }

    /**
     * 数据推送接收接口（POST）。
     *
     * OneNET 在设备上报数据后，会向该地址发送 POST 请求，Body 中为 JSON 数据：
     *
     * {
     *   "msg": "XXXXXXXXXXX",      // 消息内容（JSON 字符串或密文）
     *   "signature": "xxx",       // 加密签名
     *   "nonce": "7nJL0dGt",      // 随机字符串
     *   "time": 1725962719211,    // 推送时间戳（毫秒）
     *   "id": "9841f9ca7c09..."   // 消息 id
     * }
     *
     * 当前实现策略：
     * 1. 优先校验签名，确保数据来自 OneNET；
     * 2. 将原始数据写入 device_message 表；
     * 3. 立即返回 HTTP 200，避免 OneNET 认为超时并重试；
     * 4. 后续可在其他地方对 msg 字段进行 JSON 解析或业务处理。
     *
     * @param body OneNET 推送消息体
     * @return 始终返回 HTTP 200，内容为 "success"
     */
    @PostMapping("/callback")
    public ResponseEntity<String> receiveData(@RequestBody OneNetPushBody body) {
        System.out.println("[OneNET][数据推送] 收到 POST 推送请求");
        System.out.println("[OneNET][数据推送] 原始消息体：msg=" + body.getMsg()
                + ", nonce=" + body.getNonce()
                + ", signature=" + body.getSignature()
                + ", time=" + body.getTime()
                + ", id=" + body.getId());

        boolean ok = OneNetUtils.checkSignature(token, body.getMsg(), body.getNonce(), body.getSignature());
        if (!ok) {
            System.out.println("[OneNET][数据推送] 签名校验失败，本次数据将不会入库，但仍返回 200 避免平台长时间重试");
            // 校验失败依然返回 200，避免平台长时间重试；可以在这里打日志排查
            return ResponseEntity.ok("signature invalid");
        }

        DeviceMessage deviceMessage = new DeviceMessage();
        deviceMessage.setMsg(body.getMsg());
        deviceMessage.setNonce(body.getNonce());
        deviceMessage.setSignature(body.getSignature());
        deviceMessage.setPushTime(body.getTime());
        deviceMessage.setMessageId(body.getId());

        System.out.println("[OneNET][数据推送] 签名校验通过，准备将数据写入 device_message 表");
        System.out.println("[OneNET][数据推送] DeviceMessage 对象：" +
                "msg=" + deviceMessage.getMsg() +
                ", nonce=" + deviceMessage.getNonce() +
                ", signature=" + deviceMessage.getSignature() +
                ", pushTime=" + deviceMessage.getPushTime() +
                ", messageId=" + deviceMessage.getMessageId());

        deviceMessageService.save(deviceMessage);
        
        // 解析并保存传感器数据
        sensorDataService.parseAndSaveFromOneNetMessage(body.getMsg(), body.getTime(), body.getId());

        System.out.println("[OneNET][数据推送] 已调用 DeviceMessageService 保存数据，向 OneNET 返回 success");

        // 建议尽快返回 200，后续解析与业务处理可在其他线程或服务中异步完成
        return ResponseEntity.ok("success");
    }

    /**
     * 用于接收 OneNET POST 推送的 JSON 结构的内部类。
     * 字段名与官方文档示例保持一致，便于直接反序列化。
     */
    public static class OneNetPushBody {

        /**
         * 消息内容，可能是 JSON 字符串或密文（取决于是否开启加密）
         */
        private String msg;

        /**
         * 消息签名，校验方式与 URL 验证一致
         */
        private String signature;

        /**
         * 随机字符串
         */
        private String nonce;

        /**
         * 推送时间戳（毫秒）
         */
        private Long time;

        /**
         * 消息 id
         */
        private String id;

        public String getMsg() {
            return msg;
        }

        public void setMsg(String msg) {
            this.msg = msg;
        }

        public String getSignature() {
            return signature;
        }

        public void setSignature(String signature) {
            this.signature = signature;
        }

        public String getNonce() {
            return nonce;
        }

        public void setNonce(String nonce) {
            this.nonce = nonce;
        }

        public Long getTime() {
            return time;
        }

        public void setTime(Long time) {
            this.time = time;
        }

        public String getId() {
            return id;
        }

        public void setId(String id) {
            this.id = id;
        }
    }
}

