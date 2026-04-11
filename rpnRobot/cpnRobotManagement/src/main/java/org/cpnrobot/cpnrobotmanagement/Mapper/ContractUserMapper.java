package org.cpnrobot.cpnrobotmanagement.Mapper;


import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.springframework.web.bind.annotation.DeleteMapping;
import pojos.ContractUser;

import java.util.List;

@Mapper
public interface ContractUserMapper {

    @Insert("insert into contract_user(contract_name,contract_phone_number,user_id) values(#{contractName},#{contractPhoneNumber},#{userId})")
    int add(ContractUser contractUser);


    @Select("select * from contract_user where user_id = #{userId}")
    List<ContractUser> search(String userId);

    @Delete("delete from contract_user where contract_name = #{contractName} and user_id = #{userId}")
    int delete(ContractUser contractUser);
}
