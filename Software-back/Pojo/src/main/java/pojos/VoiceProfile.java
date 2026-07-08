package pojos;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class VoiceProfile {
    private Long id;
    private Integer userId;
    private String name;
    private String engine;
    private String status;
    private String referenceAudioPath;
    private String referenceText;
    private String modelPath;
    private Boolean defaultProfile;
    private String lastError;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
