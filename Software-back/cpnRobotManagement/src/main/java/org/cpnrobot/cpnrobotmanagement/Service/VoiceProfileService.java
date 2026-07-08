package org.cpnrobot.cpnrobotmanagement.Service;

import com.corundumstudio.socketio.SocketIOServer;
import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.cpnrobot.cpnrobotmanagement.Mapper.VoiceProfileMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import pojos.ContractMachine;
import pojos.VoiceProfile;

import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.UnsupportedAudioFileException;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

@Service
public class VoiceProfileService {

    private static final Set<String> ALLOWED_EXTENSIONS = Set.of("wav", "mp3", "m4a", "aac", "ogg", "webm", "flac");
    private static final DateTimeFormatter SAFE_TIME = DateTimeFormatter.ofPattern("yyyyMMddHHmmss");

    @Autowired
    private VoiceProfileMapper voiceProfileMapper;

    @Autowired
    private ContractMachineMapper contractMachineMapper;

    @Autowired
    private SystemConfigService systemConfigService;

    @Autowired
    private SocketIOServer socketIOServer;

    public List<VoiceProfile> list(Integer userId) {
        return voiceProfileMapper.listByUserId(userId);
    }

    public VoiceProfile getOwned(Long id, Integer userId) {
        VoiceProfile profile = voiceProfileMapper.getByIdAndUserId(id, userId);
        if (profile == null) {
            throw new RuntimeException("音色不存在或无权访问");
        }
        return profile;
    }

    public VoiceProfile getDefault(Integer userId) {
        return voiceProfileMapper.getDefaultByUserId(userId);
    }

    public VoiceProfile create(Integer userId, String name, String engine, String referenceText, MultipartFile audio) {
        if (audio == null || audio.isEmpty()) {
            throw new RuntimeException("请上传参考音频");
        }
        String profileName = cleanName(name);
        String profileEngine = cleanEngine(engine);
        String extension = extensionOf(audio.getOriginalFilename());
        if (!ALLOWED_EXTENSIONS.contains(extension)) {
            throw new RuntimeException("仅支持 wav/mp3/m4a/aac/ogg/webm/flac 音频");
        }

        try {
            Path sampleDir = storageRoot("voice-profiles").resolve(String.valueOf(userId));
            Files.createDirectories(sampleDir);
            String filename = SAFE_TIME.format(java.time.LocalDateTime.now()) + "-" + UUID.randomUUID() + "." + extension;
            Path target = sampleDir.resolve(filename).normalize();
            if (!target.startsWith(sampleDir)) {
                throw new RuntimeException("音频路径非法");
            }
            audio.transferTo(target);

            VoiceProfile profile = new VoiceProfile();
            profile.setUserId(userId);
            profile.setName(profileName);
            profile.setEngine(profileEngine);
            profile.setStatus("uploaded");
            profile.setReferenceAudioPath(target.toAbsolutePath().toString());
            profile.setReferenceText(referenceText == null ? "" : referenceText.trim());
            profile.setDefaultProfile(false);
            voiceProfileMapper.insert(profile);

            train(profile);
            return getOwned(profile.getId(), userId);
        } catch (IOException e) {
            throw new RuntimeException("保存参考音频失败: " + e.getMessage());
        }
    }

    public VoiceProfile setDefault(Long id, Integer userId) {
        getOwned(id, userId);
        voiceProfileMapper.clearDefault(userId);
        voiceProfileMapper.setDefault(id, userId);
        return getOwned(id, userId);
    }

    public void delete(Long id, Integer userId) {
        VoiceProfile profile = getOwned(id, userId);
        voiceProfileMapper.deleteByIdAndUserId(id, userId);
        deleteQuietly(profile.getReferenceAudioPath());
        deleteQuietly(profile.getModelPath());
    }

    public byte[] synthesize(Long profileId, Integer userId, String text) {
        VoiceProfile profile = getOwned(profileId, userId);
        return synthesize(profile, text);
    }

    public byte[] synthesizeDefault(Integer userId, String text) {
        VoiceProfile profile = getDefault(userId);
        if (profile == null) {
            throw new RuntimeException("请先选择默认音色");
        }
        return synthesize(profile, text);
    }

    public void speakToRobot(Long profileId, Integer userId, Integer machineId, String text) {
        VoiceProfile profile = profileId == null ? getDefault(userId) : getOwned(profileId, userId);
        if (profile == null) {
            throw new RuntimeException("请先选择默认音色");
        }
        ContractMachine machine = contractMachineMapper.getByIdAndUserId(machineId, String.valueOf(userId));
        if (machine == null) {
            throw new RuntimeException("设备不存在或不属于当前用户");
        }
        byte[] wav = synthesize(profile, text);
        try {
            streamWavToRobot(machine, wav);
        } catch (Exception e) {
            String room = roomOf(machine);
            socketIOServer.getRoomOperations(room).sendEvent("cmd_settings", Map.of(
                    "type", "tts_clone",
                    "value", text,
                    "profileId", String.valueOf(profile.getId())
            ));
        }
    }

    private void train(VoiceProfile profile) {
        profile.setStatus("training");
        voiceProfileMapper.updateTrainingState(profile);
        try {
            String url = voiceServiceUrl() + "/profiles";
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("profile_id", String.valueOf(profile.getId()));
            body.add("engine", profile.getEngine());
            body.add("reference_audio_path", profile.getReferenceAudioPath());
            body.add("reference_text", profile.getReferenceText() == null ? "" : profile.getReferenceText());

            Map<?, ?> response = voiceRestTemplate().postForObject(url, body, Map.class);
            String status = stringValue(response, "status", "ready");
            String modelPath = stringValue(response, "model_path", "");
            profile.setStatus(status.isBlank() ? "ready" : status);
            profile.setModelPath(modelPath);
            profile.setLastError("");
        } catch (Exception e) {
            profile.setStatus("ready");
            profile.setLastError("voice-service 未就绪，已保存样本，可稍后重新训练: " + e.getMessage());
        }
        voiceProfileMapper.updateTrainingState(profile);
    }

    private byte[] synthesize(VoiceProfile profile, String text) {
        String cleanText = text == null ? "" : text.trim();
        if (cleanText.isEmpty()) {
            throw new RuntimeException("请输入要朗读的文字");
        }
        try {
            String url = voiceServiceUrl() + "/synthesize";
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("profile_id", String.valueOf(profile.getId()));
            body.add("engine", profile.getEngine());
            body.add("text", cleanText);
            body.add("reference_audio_path", profile.getReferenceAudioPath());
            body.add("reference_text", profile.getReferenceText() == null ? "" : profile.getReferenceText());
            body.add("model_path", profile.getModelPath() == null ? "" : profile.getModelPath());

            ResponseEntity<byte[]> response = voiceRestTemplate().postForEntity(url, body, byte[].class);
            byte[] audio = response.getBody();
            if (!response.getStatusCode().is2xxSuccessful() || audio == null || audio.length == 0) {
                throw new RuntimeException("voice-service 没有返回音频");
            }
            return audio;
        } catch (Exception e) {
            throw new RuntimeException("语音合成失败: " + e.getMessage());
        }
    }

    private void streamWavToRobot(ContractMachine machine, byte[] wav) throws Exception {
        if (machine.getRobotIp() == null || machine.getRobotIp().isBlank()) {
            throw new RuntimeException("设备未配置 robotIp");
        }
        int streamPort = systemConfigService.getIntValue("robot.tts-stream-port", 6007);
        PcmAudio pcm = wavToPcm(wav);
        try (Socket socket = new Socket(machine.getRobotIp(), streamPort);
             DataOutputStream out = new DataOutputStream(new BufferedOutputStream(socket.getOutputStream()))) {
            String header = """
                    {"sample_rate":%d,"channels":%d,"sample_width":%d,"format":"pcm_s16le","source":"voice_clone"}
                    """.formatted((int) pcm.format.getSampleRate(), pcm.format.getChannels(), pcm.format.getSampleSizeInBits() / 8);
            out.write(header.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            out.write(pcm.bytes);
            out.flush();
        }
    }

    private PcmAudio wavToPcm(byte[] wav) throws IOException, UnsupportedAudioFileException {
        try (AudioInputStream source = AudioSystem.getAudioInputStream(new BufferedInputStream(new ByteArrayInputStream(wav)))) {
            AudioFormat base = source.getFormat();
            AudioFormat target = new AudioFormat(
                    AudioFormat.Encoding.PCM_SIGNED,
                    base.getSampleRate(),
                    16,
                    base.getChannels(),
                    base.getChannels() * 2,
                    base.getSampleRate(),
                    false
            );
            try (AudioInputStream converted = AudioSystem.getAudioInputStream(target, source);
                 ByteArrayOutputStream out = new ByteArrayOutputStream()) {
                converted.transferTo(out);
                return new PcmAudio(target, out.toByteArray());
            }
        }
    }

    private Path storageRoot(String child) {
        String configured = systemConfigService.getValue("voice.storage-root", "D:/WALL-E/data");
        return Paths.get(configured).toAbsolutePath().normalize().resolve(child);
    }

    private String voiceServiceUrl() {
        return systemConfigService.getValue("voice.service-url", "http://127.0.0.1:7862").replaceAll("/+$", "");
    }

    private RestTemplate voiceRestTemplate() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
            factory.setReadTimeout(600000);
            return new RestTemplate(factory);
    }

    private String cleanName(String name) {
        String value = name == null ? "" : name.trim();
        if (value.isEmpty()) {
            return "自定义音色";
        }
        return value.length() > 64 ? value.substring(0, 64) : value;
    }

    private String cleanEngine(String engine) {
        String value = engine == null ? "" : engine.trim().toLowerCase();
        if (value.isEmpty()) {
            return "gpt_sovits";
        }
        if (!Set.of("zero_shot", "gpt_sovits", "voxcpm").contains(value)) {
            return "gpt_sovits";
        }
        return value;
    }

    private String extensionOf(String filename) {
        if (filename == null || !filename.contains(".")) {
            return "wav";
        }
        return filename.substring(filename.lastIndexOf('.') + 1).toLowerCase();
    }

    private String stringValue(Map<?, ?> map, String key, String fallback) {
        if (map == null || !map.containsKey(key) || map.get(key) == null) {
            return fallback;
        }
        return String.valueOf(map.get(key));
    }

    private String roomOf(ContractMachine machine) {
        if (machine.getConnectionId() == null || machine.getConnectionId().isBlank()) {
            throw new RuntimeException("设备连接号未配置");
        }
        return "robot_" + machine.getConnectionId();
    }

    private void deleteQuietly(String path) {
        if (path == null || path.isBlank()) {
            return;
        }
        try {
            Files.deleteIfExists(Paths.get(path));
        } catch (Exception ignored) {
        }
    }

    private record PcmAudio(AudioFormat format, byte[] bytes) {
    }
}
