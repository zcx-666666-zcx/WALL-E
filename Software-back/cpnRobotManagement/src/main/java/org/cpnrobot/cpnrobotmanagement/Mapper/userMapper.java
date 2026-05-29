package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import pojos.User;

@Mapper
public interface userMapper {

    @Select("select id, username, phone_number, password, role from user where username = #{username}")
    User findByUsername(String username);

    @Update("update user set password = #{password} where id = #{id}")
    int updatePassword(@Param("id") Integer id, @Param("password") String password);

    @Insert("insert into user(username,phone_number,password) values(#{username},#{phoneNumber},#{password})")
    int register(User user);

    @Select("select username from user where username = #{username}")
    User register_check(User user);

    @Select("select * from user where username = #{username}")
    User getId(String username);

    @Select("select * from user where id = #{id}")
    User getName(Integer id);
}
