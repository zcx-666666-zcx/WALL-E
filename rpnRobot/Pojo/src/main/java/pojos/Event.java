package pojos;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Event {
    private Integer id;
    private String eventName;
    private LocalDate eventDate;
    private LocalTime eventTime;
    private Integer repeatDays;
    private String priority;
    private String machines;
    private String description;
    private String userId;

}
