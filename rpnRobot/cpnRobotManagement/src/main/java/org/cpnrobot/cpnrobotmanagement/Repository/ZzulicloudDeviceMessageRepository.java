package org.cpnrobot.cpnrobotmanagement.Repository;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import pojos.DeviceMessage;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;

/**
 * 将 OneNET 推送的数据额外同步写入 MySQL 数据库 zzulicloud。
 *
 * 说明：
 * - 这里不走 Spring 多数据源配置，而是使用最直接的 JDBC 方式单独连接 zzulicloud，
 *   避免对现有 cpnrobot 数据源配置造成影响。
 * - 目标表建议为 zzulicloud 数据库中的 onenet_device_message，结构与本系统的 device_message 表一致：
 *
 *   CREATE TABLE onenet_device_message (
 *       id INT PRIMARY KEY AUTO_INCREMENT,
 *       msg TEXT,
 *       nonce VARCHAR(32),
 *       signature VARCHAR(128),
 *       push_time BIGINT,
 *       message_id VARCHAR(64)
 *   );
 */
@Component
public class ZzulicloudDeviceMessageRepository {

    @Value("${zzulicloud.datasource.url}")
    private String url;

    @Value("${zzulicloud.datasource.username}")
    private String username;

    @Value("${zzulicloud.datasource.password}")
    private String password;

    /**
     * 将一条 DeviceMessage 同步写入 zzulicloud.onenet_device_message 表。
     *
     * @param deviceMessage 已通过 OneNET 签名校验的数据对象
     */
    public void insert(DeviceMessage deviceMessage) {
        String sql = "INSERT INTO onenet_device_message(msg, nonce, signature, push_time, message_id) " +
                "VALUES(?, ?, ?, ?, ?)";

        System.out.println("[zzulicloud][数据入库] 准备写入 onenet_device_message 表，连接 URL=" + url);

        try (Connection connection = DriverManager.getConnection(url, username, password);
             PreparedStatement ps = connection.prepareStatement(sql)) {

            ps.setString(1, deviceMessage.getMsg());
            ps.setString(2, deviceMessage.getNonce());
            ps.setString(3, deviceMessage.getSignature());
            ps.setLong(4, deviceMessage.getPushTime() != null ? deviceMessage.getPushTime() : 0L);
            ps.setString(5, deviceMessage.getMessageId());

            int rows = ps.executeUpdate();
            System.out.println("[zzulicloud][数据入库] onenet_device_message 表写入完成，受影响行数=" + rows);
        } catch (Exception e) {
            System.out.println("[zzulicloud][数据入库][异常] 写入 onenet_device_message 失败，异常信息=" + e.getMessage());
        }
    }
}

