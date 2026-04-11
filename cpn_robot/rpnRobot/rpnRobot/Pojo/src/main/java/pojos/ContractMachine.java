package pojos;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ContractMachine {
    private Integer id;
    private String machines;
    private String connectionId;
    private  String userId;
}
