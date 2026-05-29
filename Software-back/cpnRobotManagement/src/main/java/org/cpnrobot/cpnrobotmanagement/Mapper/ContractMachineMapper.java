package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import pojos.ContractMachine;

import java.util.List;

@Mapper
public interface ContractMachineMapper {

    @Select("select * from contract_machine where user_id = #{userId}")
    List<ContractMachine> search(String userId);

    @Insert("insert into contract_machine(machines,connectionId,user_id,robot_ip) values(#{machines},#{connectionId},#{userId},#{robotIp})")
    int add(ContractMachine contractMachine);

    @Insert("delete from contract_machine where machines = #{machines} and user_id = #{userId}")
    int delete(ContractMachine contractMachine);

    @Update("update contract_machine set robot_ip = #{robotIp} where id = #{id} and user_id = #{userId}")
    int updateRobotIp(ContractMachine contractMachine);

    @Select("select * from contract_machine where id = #{id}")
    ContractMachine getById(Integer id);
}
