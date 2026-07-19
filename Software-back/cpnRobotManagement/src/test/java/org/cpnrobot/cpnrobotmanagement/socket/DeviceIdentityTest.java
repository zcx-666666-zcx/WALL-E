package org.cpnrobot.cpnrobotmanagement.socket;

import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

import static org.assertj.core.api.Assertions.assertThat;

class DeviceIdentityTest {

    @Test
    void canonicalizesDeployedWaleeTypo() throws Exception {
        Class<?> identity = Class.forName("org.cpnrobot.cpnrobotmanagement.socket.DeviceIdentity");
        Method canonicalize = identity.getDeclaredMethod("canonicalize", String.class);

        Object result = canonicalize.invoke(null, "WALEE_1");

        assertThat(result).isEqualTo("WALLE_1");
    }
}
