package org.cpnrobot.cpnrobotmanagement.config;

import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;

class SocketIOConfigTest {
    @Test
    void acceptsCameraFramesUpToApplicationLimit() {
        var config = new SocketIOConfig().socketIOServer().getConfiguration();
        assertThat(config.getMaxFramePayloadLength()).isGreaterThan(524288);
        assertThat(config.getMaxHttpContentLength()).isGreaterThan(524288);
    }
}
