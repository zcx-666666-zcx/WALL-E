package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import pojos.DeviceMessage;

/**
 * 用于将 OneNET 推送的原始数据持久化到数据库。
 */
@Mapper
public interface DeviceMessageMapper {

    /**
     * 将一条 OneNET 推送的原始数据写入 device_message 表。
     *
     * 对应的建表 SQL 示例（可根据实际情况调整）：
     *
     * CREATE TABLE device_message (
     *   id INT PRIMARY KEY AUTO_INCREMENT,
     *   msg TEXT,
     *   nonce VARCHAR(32),
     *   signature VARCHAR(128),
     *   push_time BIGINT,
     *   message_id VARCHAR(64)
     * );
     */
    @Insert("INSERT INTO device_message(msg, nonce, signature, push_time, message_id) " +
            "VALUES(#{msg}, #{nonce}, #{signature}, #{pushTime}, #{messageId})")
    int insert(DeviceMessage deviceMessage);
}

