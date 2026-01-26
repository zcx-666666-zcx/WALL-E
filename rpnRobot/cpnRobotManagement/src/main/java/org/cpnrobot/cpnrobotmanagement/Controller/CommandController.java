package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.CommandService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.Command;
import pojos.ListResult;
import pojos.Result;

@RestController
@RequestMapping("/command")
@CrossOrigin(origins = "http://localhost:5173")
public class CommandController {

    @Autowired
    private CommandService commandService;

    @PostMapping("/search")
    public Result search(@RequestBody Command command){
        ListResult<Command> listResult = commandService.search(command);
        return Result.success(listResult);
    }
}
