package pojos;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ContractUser {
    private Integer id;
    private String contractName;
    private String contractPhoneNumber;
    private int userId;
}
