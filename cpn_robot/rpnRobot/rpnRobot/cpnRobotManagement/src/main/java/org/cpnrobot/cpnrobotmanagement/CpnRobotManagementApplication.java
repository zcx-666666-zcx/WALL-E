package org.cpnrobot.cpnrobotmanagement;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.servlet.ServletComponentScan;

@SpringBootApplication
//@ServletComponentScan
@MapperScan("org.cpnrobot.cpnrobotmanagement.Mapper")
public class CpnRobotManagementApplication {

    public static void main(String[] args) {
        SpringApplication.run(CpnRobotManagementApplication.class, args);
    }

}
