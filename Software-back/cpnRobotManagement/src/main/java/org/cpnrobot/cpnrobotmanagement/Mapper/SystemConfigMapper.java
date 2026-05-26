package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import pojos.SystemConfig;

import java.util.List;

@Mapper
public interface SystemConfigMapper {

    @Select("select id, config_key, config_value, label, config_group, secret, remark, updated_at from system_config order by config_group, id")
    List<SystemConfig> findAll();

    @Select("select id, config_key, config_value, label, config_group, secret, remark, updated_at from system_config where config_key = #{configKey}")
    SystemConfig findByKey(String configKey);

    @Insert("insert into system_config(config_key, config_value, label, config_group, secret, remark) values(#{configKey}, #{configValue}, #{label}, #{configGroup}, #{secret}, #{remark})")
    int insert(SystemConfig config);

    @Update("update system_config set config_value = #{configValue}, label = #{label}, config_group = #{configGroup}, secret = #{secret}, remark = #{remark}, updated_at = now() where config_key = #{configKey}")
    int update(SystemConfig config);
}
