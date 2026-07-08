package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.VoiceProfileService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import pojos.Result;
import util.CurrentHolder;

import java.nio.charset.StandardCharsets;
import java.util.Map;

@RestController
@RequestMapping("/api/voice-profiles")
@CrossOrigin(origins = "*", maxAge = 3600)
public class VoiceProfileController {

    @Autowired
    private VoiceProfileService voiceProfileService;

    @GetMapping
    public Result list() {
        Integer userId = requireUserId();
        return Result.success(voiceProfileService.list(userId));
    }

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Result create(
            @RequestParam("name") String name,
            @RequestParam(value = "engine", required = false) String engine,
            @RequestParam(value = "referenceText", required = false) String referenceText,
            @RequestParam("audio") MultipartFile audio
    ) {
        try {
            Integer userId = requireUserId();
            return Result.success(voiceProfileService.create(userId, name, engine, referenceText, audio));
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/{id}/default")
    public Result setDefault(@PathVariable Long id) {
        try {
            Integer userId = requireUserId();
            return Result.success(voiceProfileService.setDefault(id, userId));
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result delete(@PathVariable Long id) {
        try {
            Integer userId = requireUserId();
            voiceProfileService.delete(id, userId);
            return Result.success();
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @PostMapping(value = "/{id}/preview", produces = "audio/wav")
    public ResponseEntity<byte[]> preview(@PathVariable Long id, @RequestBody Map<String, String> body) {
        try {
            Integer userId = requireUserId();
            String text = body == null ? "" : body.getOrDefault("text", "");
            byte[] wav = voiceProfileService.synthesize(id, userId, text);
            return audioResponse(wav, "voice-preview.wav");
        } catch (Exception e) {
            return textResponse(e.getMessage());
        }
    }

    @PostMapping("/speak")
    public Result speak(@RequestBody Map<String, Object> body) {
        try {
            Integer userId = requireUserId();
            Long profileId = longValue(body.get("profileId"));
            Integer machineId = intValue(body.get("machineId"));
            String text = stringValue(body.get("text"));
            voiceProfileService.speakToRobot(profileId, userId, machineId, text);
            return Result.success();
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    private ResponseEntity<byte[]> audioResponse(byte[] bytes, String filename) {
        ContentDisposition disposition = ContentDisposition.inline()
                .filename(filename, StandardCharsets.UTF_8)
                .build();
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, disposition.toString())
                .header(HttpHeaders.CACHE_CONTROL, "no-store")
                .contentType(MediaType.parseMediaType("audio/wav"))
                .body(bytes);
    }

    private ResponseEntity<byte[]> textResponse(String message) {
        String safeMessage = message == null || message.isBlank() ? "语音合成失败" : message;
        return ResponseEntity.badRequest()
                .header(HttpHeaders.CACHE_CONTROL, "no-store")
                .contentType(MediaType.parseMediaType("text/plain; charset=utf-8"))
                .body(safeMessage.getBytes(StandardCharsets.UTF_8));
    }

    private Integer requireUserId() {
        Integer userId = CurrentHolder.getCurrentId();
        if (userId == null) {
            throw new RuntimeException("未登录或 token 无效");
        }
        return userId;
    }

    private Long longValue(Object value) {
        if (value == null || String.valueOf(value).isBlank()) {
            return null;
        }
        return Long.valueOf(String.valueOf(value));
    }

    private Integer intValue(Object value) {
        if (value == null || String.valueOf(value).isBlank()) {
            throw new RuntimeException("请选择设备");
        }
        return Integer.valueOf(String.valueOf(value));
    }

    private String stringValue(Object value) {
        return value == null ? "" : String.valueOf(value);
    }
}
