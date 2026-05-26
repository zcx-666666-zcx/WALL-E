package org.cpnrobot.cpnrobotmanagement.Service;

import org.cpnrobot.cpnrobotmanagement.Mapper.ContractMachineMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import pojos.ContractMachine;

import java.io.InputStream;
import java.io.OutputStream;
import java.util.Map;

@Service
public class RobotProxyService {

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private ContractMachineMapper contractMachineMapper;

    @Autowired
    private SystemConfigService systemConfigService;

    private String getRobotUrl(Integer machineId, String path) {
        ContractMachine machine = contractMachineMapper.getById(machineId);
        if (machine == null || machine.getRobotIp() == null || machine.getRobotIp().isEmpty()) {
            throw new RuntimeException("机器人未找到或 IP 未配置，machineId: " + machineId);
        }
        int robotPort = systemConfigService.getIntValue("robot.http-port", 5000);
        return "http://" + machine.getRobotIp() + ":" + robotPort + path;
    }

    public String proxyPost(Integer machineId, String path, Map<String, String> formData) {
        String url = getRobotUrl(machineId, path);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        if (formData != null) {
            formData.forEach(body::add);
        }

        HttpEntity<MultiValueMap<String, String>> request = new HttpEntity<>(body, headers);
        return restTemplate.postForObject(url, request, String.class);
    }

    public String getRobotIp(Integer machineId) {
        ContractMachine machine = contractMachineMapper.getById(machineId);
        if (machine == null) {
            throw new RuntimeException("机器人未找到，machineId: " + machineId);
        }
        return machine.getRobotIp();
    }

    public void streamVideo(Integer machineId, OutputStream outputStream) {
        streamVideoFromPath(machineId, "/video_feed", outputStream);
    }

    public void streamVideoLow(Integer machineId, OutputStream outputStream) {
        streamVideoFromPath(machineId, "/video_feed_low", outputStream);
    }

    private void streamVideoFromPath(Integer machineId, String path, OutputStream outputStream) {
        String url = getRobotUrl(machineId, path);

        RestTemplate streamTemplate = new RestTemplate(new org.springframework.http.client.SimpleClientHttpRequestFactory() {{
            setConnectTimeout(3000);
            setReadTimeout(0);
            setBufferRequestBody(false);
        }});

        streamTemplate.execute(url, HttpMethod.GET, null, response -> {
            InputStream body = response.getBody();
            byte[] buffer = new byte[8192]; // 8KB 缓冲，每一帧立即写出
            int bytesRead;
            while ((bytesRead = body.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
                outputStream.flush(); // 立即 flush，不积攒帧
            }
            outputStream.flush();
            return null;
        });
    }
}
