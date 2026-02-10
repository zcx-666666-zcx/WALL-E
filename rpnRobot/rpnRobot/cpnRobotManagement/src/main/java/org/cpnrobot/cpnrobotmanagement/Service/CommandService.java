package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.Command;
import pojos.ListResult;

public interface CommandService {
    ListResult<Command> search(Command command);
}
