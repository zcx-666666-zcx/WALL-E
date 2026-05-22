package org.cpnrobot.cpnrobotmanagement.config;
import com.corundumstudio.socketio.SocketConfig;
import com.corundumstudio.socketio.SocketIOServer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SocketIOConfig {

    @Bean
    public SocketIOServer socketIOServer() {
        com.corundumstudio.socketio.Configuration config = new com.corundumstudio.socketio.Configuration();
        config.setHostname("0.0.0.0"); // 允许所有 IP 连接
        config.setPort(8081); // 这里的端口要和前端 SERVER_URL 对应
        config.setContext("/socket.io");

        // 解决跨域问题（等同于 Python 中的 cors_allowed_origins='*'）
        SocketConfig socketConfig = new SocketConfig();
        socketConfig.setReuseAddress(true);
        config.setSocketConfig(socketConfig);
        config.setAllowHeaders("*");
        config.setOrigin("*");
        config.setAllowCustomRequests(true);

        return new SocketIOServer(config);
    }
}
