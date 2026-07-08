package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.VoiceProfileService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;
import util.CurrentHolder;

import java.nio.charset.StandardCharsets;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

class VoiceProfileControllerTest {

    private VoiceProfileService voiceProfileService;

    private VoiceProfileController controller;

    @BeforeEach
    void setUp() {
        controller = new VoiceProfileController();
        voiceProfileService = new VoiceProfileService() {
            @Override
            public byte[] synthesize(Long profileId, Integer userId, String text) {
                throw new RuntimeException("语音合成失败: 参考音频无法解析");
            }
        };
        ReflectionTestUtils.setField(controller, "voiceProfileService", voiceProfileService);
    }

    @AfterEach
    void tearDown() {
        CurrentHolder.remove();
    }

    @Test
    void previewReturnsReadableErrorWhenSynthesisFails() {
        CurrentHolder.setCurrentId(7);

        ResponseEntity<byte[]> response = controller.preview(3L, Map.of("text", "你好"));

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(new String(response.getBody(), StandardCharsets.UTF_8))
                .contains("语音合成失败")
                .contains("参考音频无法解析");
    }
}
