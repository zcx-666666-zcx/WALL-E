package org.cpnrobot.cpnrobotmanagement.Service;

import org.cpnrobot.cpnrobotmanagement.Mapper.SystemConfigMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pojos.SystemConfig;
import pojos.SystemConfigDTO;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class SystemConfigService {

    @Autowired
    private SystemConfigMapper systemConfigMapper;

    public List<SystemConfig> listAll() {
        return systemConfigMapper.findAll();
    }

    public SystemConfigDTO getRuntimeConfig(boolean includeSecrets) {
        Map<String, String> values = new LinkedHashMap<>();
        Map<String, Object> publicConfig = new LinkedHashMap<>();

        for (SystemConfig config : listAll()) {
            values.put(config.getConfigKey(), config.getConfigValue());
            if (includeSecrets || !Boolean.TRUE.equals(config.getSecret())) {
                publicConfig.put(config.getConfigKey(), config.getConfigValue());
            }
        }

        SystemConfigDTO dto = new SystemConfigDTO();
        dto.setApiBaseUrl(value(values, "api.base-url"));
        dto.setWebBaseUrl(value(values, "web.base-url"));
        dto.setStaticBaseUrl(value(values, "static.base-url"));
        dto.setRobotDefaultIp(value(values, "robot.default-ip"));
        dto.setRobotHttpPort(intValue(values, "robot.http-port", 5000));
        dto.setSocketServerUrl(value(values, "socket.server-url"));
        dto.setCozeApiUrl(value(values, "coze.api-url"));
        dto.setCozeWorkflowId(value(values, "coze.workflow-id"));
        dto.setPublicConfig(publicConfig);
        return dto;
    }

    public void saveAll(List<SystemConfig> configs) {
        if (configs == null) {
            return;
        }
        for (SystemConfig config : configs) {
            if (config.getConfigKey() == null || config.getConfigKey().trim().isEmpty()) {
                continue;
            }
            config.setConfigKey(config.getConfigKey().trim());
            if (config.getConfigGroup() == null || config.getConfigGroup().trim().isEmpty()) {
                config.setConfigGroup("custom");
            }
            if (config.getLabel() == null || config.getLabel().trim().isEmpty()) {
                config.setLabel(config.getConfigKey());
            }
            if (config.getSecret() == null) {
                config.setSecret(false);
            }
            SystemConfig old = systemConfigMapper.findByKey(config.getConfigKey());
            if (old == null) {
                systemConfigMapper.insert(config);
            } else {
                systemConfigMapper.update(config);
            }
        }
    }

    public String getValue(String key, String fallback) {
        SystemConfig config = systemConfigMapper.findByKey(key);
        if (config == null || config.getConfigValue() == null || config.getConfigValue().isBlank()) {
            return fallback;
        }
        return config.getConfigValue();
    }

    public int getIntValue(String key, int fallback) {
        SystemConfig config = systemConfigMapper.findByKey(key);
        if (config == null) {
            return fallback;
        }
        try {
            return Integer.parseInt(config.getConfigValue());
        } catch (Exception ignored) {
            return fallback;
        }
    }

    private String value(Map<String, String> values, String key) {
        return values.getOrDefault(key, "");
    }

    private int intValue(Map<String, String> values, String key, int fallback) {
        try {
            return Integer.parseInt(values.getOrDefault(key, ""));
        } catch (Exception ignored) {
            return fallback;
        }
    }
}
