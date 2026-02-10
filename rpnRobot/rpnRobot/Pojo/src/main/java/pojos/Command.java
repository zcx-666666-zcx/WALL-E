package pojos;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Command {
    private Integer id;
    private String commandName;
    private String commandCode;
    private LocalDateTime time;
    private String machines;
    private String userId;
}
