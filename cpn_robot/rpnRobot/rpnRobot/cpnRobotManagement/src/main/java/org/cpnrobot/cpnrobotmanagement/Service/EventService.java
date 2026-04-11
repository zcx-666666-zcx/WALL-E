package org.cpnrobot.cpnrobotmanagement.Service;

import pojos.Event;
import pojos.ListResult;

public interface EventService {
    int addEvent(Event event);


    ListResult<Event> searchEvent(String userId);

    int deleteEvent(Event event);

    Event searchOne(Event event);

    int updateEvent(Event event);
}
