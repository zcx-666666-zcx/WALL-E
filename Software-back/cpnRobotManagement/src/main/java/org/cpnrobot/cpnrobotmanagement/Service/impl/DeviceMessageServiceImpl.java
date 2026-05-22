package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.DeviceMessageMapper;
import org.cpnrobot.cpnrobotmanagement.Service.DeviceMessageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.DeviceMessage;

/**
 * OneNET 推送消息持久化业务实现。
 *
 * 当前实现比较简单，直接写库即可；如果后续推送量很大，可以在这里改成
 * 异步入库（例如放入消息队列或线程池）以避免阻塞 OneNET 的 HTTP 请求。
 */
@Service
public class DeviceMessageServiceImpl implements DeviceMessageService {

    @Autowired
    private DeviceMessageMapper deviceMessageMapper;

    @Override
    public void save(DeviceMessage deviceMessage) {
        System.out.println("[OneNET][数据入库] 开始写入 device_message 表");
        System.out.println("[OneNET][数据入库] 即将写入的数据内容：" +
                "msg=" + deviceMessage.getMsg() +
                ", nonce=" + deviceMessage.getNonce() +
                ", signature=" + deviceMessage.getSignature() +
                ", pushTime=" + deviceMessage.getPushTime() +
                ", messageId=" + deviceMessage.getMessageId());

        deviceMessageMapper.insert(deviceMessage);

        System.out.println("[OneNET][数据入库] device_message 表写入完成（insert 已执行）");

        // 移除了zzulicloud数据库同步功能，只保留本地存储
    }
}

        