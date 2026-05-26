package org.cpnrobot.cpnrobotmanagement.Controller;

import org.cpnrobot.cpnrobotmanagement.Service.SystemConfigService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import pojos.Result;

import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/coze")
@CrossOrigin(origins = "*", maxAge = 3600)
public class CozeProxyController {

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private SystemConfigService systemConfigService;

    @PostMapping("/workflow/run")
    public Result runWorkflow(@RequestBody Map<String, Object> body) {
        Map<String, Object> requestBody = body == null ? new LinkedHashMap<>() : new LinkedHashMap<>(body);
        String token = systemConfigService.getValue("coze.token", "");
        String apiBaseUrl = systemConfigService.getValue("coze.api-url", "https://api.coze.cn");
        String workflowId = systemConfigService.getValue("coze.workflow-id", "");

        if (token == null || token.isBlank()) {
            return Result.error("请先在系统配置中填写 Coze Token");
        }
        if (!requestBody.containsKey("workflow_id") && workflowId != null && !workflowId.isBlank()) {
            requestBody.put("workflow_id", workflowId);
        }
        if (!requestBody.containsKey("workflow_id") || String.valueOf(requestBody.get("workflow_id")).isBlank()) {
            return Result.error("请先在系统配置中填写 Coze 工作流 ID");
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(token);

        String url = apiBaseUrl.replaceAll("/$", "") + "/v1/workflow/run";
        try {
            ResponseEntity<String> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    new HttpEntity<>(requestBody, headers),
                    String.class
            );
            return Result.success(response.getBody());
        } catch (RestClientException e) {
            return Result.error("Coze 调用失败：" + e.getMessage());
        }
    }
}
