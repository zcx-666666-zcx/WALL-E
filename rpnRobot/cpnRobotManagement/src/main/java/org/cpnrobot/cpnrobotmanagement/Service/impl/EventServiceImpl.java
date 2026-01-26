package org.cpnrobot.cpnrobotmanagement.Service.impl;

import org.cpnrobot.cpnrobotmanagement.Mapper.EventMapper;
import org.cpnrobot.cpnrobotmanagement.Service.EventService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.Event;
import pojos.ListResult;

import java.util.List;


@Service
public class EventServiceImpl implements EventService {

    @Autowired
    private EventMapper eventMapper;
    @Override
    public int addEvent(Event event) {
        int num = eventMapper.addEvent(event);
        if(num>0){
            return 1;
        }
        return 0;
    }

    @Override
    public ListResult<Event> searchEvent(String userId) {
        List<Event> result = eventMapper.searchEvent(userId);

        return new ListResult<>(result);

    }

    @Override
    public int deleteEvent(Event event) {
        int num = eventMapper.deleteEvent(event);
        if(num>0){
            return 1;
        }
        return 0;
    }

    @Override
    public Event searchOne(Event event) {
        Event e = eventMapper.searchOne(event);
        return e;
    }

    @Override
    public int updateEvent(Event event) {
        int num = eventMapper.updateEvent(event);
        if(num==1){
            return 1;
        }
        return 0;
    }


}
