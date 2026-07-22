package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.DeviceNetworkStatus;

@Mapper
public interface DeviceNetworkStatusMapper {

    @Insert("""
            insert into device_network_status(device_id, user_id, lan_ip, observed_ip, network_name, last_seen_at)
            values(#{deviceId}, #{userId}, #{lanIp}, #{observedIp}, #{networkName}, #{lastSeenAt})
            on duplicate key update
              user_id = values(user_id),
              lan_ip = values(lan_ip),
              observed_ip = values(observed_ip),
              network_name = values(network_name),
              last_seen_at = values(last_seen_at)
            """)
    int upsert(DeviceNetworkStatus status);

    @Select("select * from device_network_status where device_id = #{deviceId} and user_id = #{userId}")
    DeviceNetworkStatus findByDeviceIdAndUserId(
            @org.apache.ibatis.annotations.Param("deviceId") String deviceId,
            @org.apache.ibatis.annotations.Param("userId") String userId);
}
