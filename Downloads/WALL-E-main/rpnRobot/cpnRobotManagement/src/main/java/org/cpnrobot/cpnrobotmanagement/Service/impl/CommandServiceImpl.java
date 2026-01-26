package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.CommandMapper;
import org.cpnrobot.cpnrobotmanagement.Service.CommandService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.Command;
import pojos.ListResult;

import java.util.List;

@Service
public class CommandServiceImpl implements CommandService {

    @Autowired
    private CommandMapper commandMapper;

    @Override
    public ListResult<Command> search(Command command) {
        List<Command> commands = commandMapper.search(command);
        return new ListResult<>(commands);
    }
}
