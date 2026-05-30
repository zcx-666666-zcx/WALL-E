package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.EventService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import pojos.Event;
import pojos.ListResult;
import pojos.Result;
import util.CurrentHolder;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class EventControllerTest {

    @Mock
    private EventService eventservice;

    @InjectMocks
    private EventController controller;

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
    }

    @Test
    void searchUsesCurrentTokenUserInsteadOfPathUser() {
        CurrentHolder.setCurrentId(7);
        when(eventservice.searchEvent("7")).thenReturn(new ListResult<>(List.of()));

        Result result = controller.searchEvent("999");

        assertThat(result.getCode()).isEqualTo(1);
        verify(eventservice).searchEvent("7");
    }

    @Test
    void addForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        Event request = new Event();
        request.setEventName("吃药");
        request.setUserId("999");
        when(eventservice.addEvent(argThat(event -> "7".equals(event.getUserId())))).thenReturn(1);

        Result result = controller.addEvent(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(eventservice).addEvent(argThat(event -> "7".equals(event.getUserId())));
    }

    @Test
    void deleteForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        Event request = new Event();
        request.setEventName("吃药");
        request.setUserId("999");
        when(eventservice.deleteEvent(argThat(event -> "7".equals(event.getUserId())))).thenReturn(1);

        Result result = controller.deleteEvent(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(eventservice).deleteEvent(argThat(event -> "7".equals(event.getUserId())));
    }

    @Test
    void searchOneForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        Event request = new Event();
        request.setEventName("吃药");
        request.setUserId("999");
        Event owned = new Event();
        owned.setEventName("吃药");
        owned.setUserId("7");
        when(eventservice.searchOne(argThat(event -> "7".equals(event.getUserId())))).thenReturn(owned);

        Result result = controller.searchOne(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(eventservice).searchOne(argThat(event -> "7".equals(event.getUserId())));
    }

    @Test
    void updateForcesCurrentTokenUser() {
        CurrentHolder.setCurrentId(7);
        Event request = new Event();
        request.setEventName("吃药");
        request.setUserId("999");
        when(eventservice.updateEvent(argThat(event -> "7".equals(event.getUserId())))).thenReturn(1);

        Result result = controller.updateEvent(request);

        assertThat(result.getCode()).isEqualTo(1);
        verify(eventservice).updateEvent(argThat(event -> "7".equals(event.getUserId())));
    }
}
