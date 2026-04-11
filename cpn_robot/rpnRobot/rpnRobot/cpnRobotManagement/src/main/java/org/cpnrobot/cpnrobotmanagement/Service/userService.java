package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.LoginInfo;
import pojos.Result;
import pojos.User;

public interface userService {
    LoginInfo login(User user);


    int register(User user);

    User getId(String username);

    User getName(Integer id);
}
