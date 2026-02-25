package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.DeviceMessage;

/**
 * OneNET 推送消息持久化相关业务接口。
 */
public interface DeviceMessageService {

    /**
     * 保存一条 OneNET 推送的原始消息。
     *
     * @param deviceMessage 由回调接口转换得到的实体对象
     */
    void save(DeviceMessage deviceMessage);
}

