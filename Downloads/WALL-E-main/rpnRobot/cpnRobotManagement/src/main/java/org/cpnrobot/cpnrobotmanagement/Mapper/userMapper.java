package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojos.LoginInfo;
import pojos.Result;
import pojos.User;

@Mapper
public interface userMapper {

    @Select("select username,password from user where username = #{username} and password = #{password} ")
    User login(User user);

    @Insert("insert into user(username,phone_number,password) values(#{username},#{phoneNumber},#{password})")
    int register(User user);

    @Select("select username from user where username = #{username}")
    User register_check(User user);

    @Select("select * from user where username = #{username}")
    User getId(String username);
}
