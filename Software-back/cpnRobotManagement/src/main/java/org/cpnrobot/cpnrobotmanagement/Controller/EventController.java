package org.cpnrobot.cpnrobotmanagement.Controller;


import org.apache.ibatis.annotations.Select;
import org.cpnrobot.cpnrobotmanagement.Service.EventService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pojos.Event;
import pojos.ListResult;
import pojos.Result;

@RequestMapping("/api/events")
@RestController
@CrossOrigin(origins = "*",maxAge = 3600)
public class EventController {

    @Autowired
    private EventService eventservice;

    @PostMapping("/add")
    public Result addEvent(@RequestBody Event event){
        int num = eventservice.addEvent(event);
        if(num!=0){
            return Result.success();
        }
        return Result.error("添加失败");
    }

    @GetMapping("/search/{userId}")
    public Result searchEvent(@PathVariable("userId") String userId){
        ListResult<Event> listResult = eventservice.searchEvent(userId);
        return Result.success(listResult);
    }

    @DeleteMapping("/delete")
    public Result deleteEvent(@RequestBody Event event){
    	int num = eventservice.deleteEvent(event);
    	if(num!=0){
    		return Result.success();
    	}
    	return Result.error("删除失败");
    }


    @PostMapping("/searchOne")
    public Result searchOne(@RequestBody Event event){
        Event e = eventservice.searchOne(event);
        if(e!=null){
            return Result.success(e);
        }
        return Result.error("未找到该事件");
    }

    @PutMapping("/update")
    public Result updateEvent(@RequestBody Event event){
    	int num = eventservice.updateEvent(event);
    	if(num!=0){
    		return Result.success();
    	}
    	return Result.error("更新失败");
    }

}
