package org.cpnrobot.cpnrobotmanagement.Filter;

import jakarta.servlet.FilterChain;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.concurrent.atomic.AtomicBoolean;

import static org.assertj.core.api.Assertions.assertThat;

class TokenFilterTest {

    private final TokenFilter tokenFilter = new TokenFilter();

    @Test
    void healthyQueryRequiresToken() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/healthy/getRate/WALLE_1");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);
        FilterChain chain = (servletRequest, servletResponse) -> chainCalled.set(true);

        tokenFilter.doFilter(request, response, chain);

        assertThat(chainCalled).isFalse();
        assertThat(response.getStatus()).isEqualTo(401);
    }

    @Test
    void healthyIngestDoesNotRequireToken() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/healthy/addRate");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);
        FilterChain chain = (servletRequest, servletResponse) -> chainCalled.set(true);

        tokenFilter.doFilter(request, response, chain);

        assertThat(chainCalled).isTrue();
        assertThat(response.getStatus()).isEqualTo(200);
    }

    @Test
    void registerDoesNotRequireToken() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/users/register");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);
        FilterChain chain = (servletRequest, servletResponse) -> chainCalled.set(true);

        tokenFilter.doFilter(request, response, chain);

        assertThat(chainCalled).isTrue();
        assertThat(response.getStatus()).isEqualTo(200);
    }

    @Test
    void deviceEventSyncUsesDeviceAuthenticationInsteadOfUserJwt() throws Exception {
        ReflectionTestUtils.setField(tokenFilter, "deviceApiToken", "device-secret");
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/device/events/WALLE_1");
        request.addHeader("X-Walle-Device-Token", "device-secret");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);
        FilterChain chain = (servletRequest, servletResponse) -> chainCalled.set(true);

        tokenFilter.doFilter(request, response, chain);

        assertThat(chainCalled).isTrue();
        assertThat(response.getStatus()).isEqualTo(200);
    }

    @Test
    void deviceEventSyncRejectsMissingDeviceToken() throws Exception {
        ReflectionTestUtils.setField(tokenFilter, "deviceApiToken", "device-secret");
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/device/events/WALLE_1");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);
        FilterChain chain = (servletRequest, servletResponse) -> chainCalled.set(true);

        tokenFilter.doFilter(request, response, chain);

        assertThat(chainCalled).isFalse();
        assertThat(response.getStatus()).isEqualTo(401);
    }

    @Test
    void legacySensorReadsRequireUserAuthentication() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/sensor/latest");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);
        tokenFilter.doFilter(request, response, (req, res) -> chainCalled.set(true));
        assertThat(chainCalled).isFalse();
        assertThat(response.getStatus()).isEqualTo(401);
    }

    @Test
    void publicVideoProxyRequiresUserAuthentication() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/robot/video-feed/1");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);
        tokenFilter.doFilter(request, response, (req, res) -> chainCalled.set(true));
        assertThat(chainCalled).isFalse();
        assertThat(response.getStatus()).isEqualTo(401);
    }

    @Test
    void secureModeRequiresDeviceTokenForHealthIngest() throws Exception {
        assertThat(org.springframework.util.ReflectionUtils.findField(TokenFilter.class, "requireDeviceAuth")).isNotNull();
        ReflectionTestUtils.setField(tokenFilter, "requireDeviceAuth", true);
        ReflectionTestUtils.setField(tokenFilter, "deviceApiToken", "device-secret");
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/healthy/addRate");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);
        tokenFilter.doFilter(request, response, (req, res) -> chainCalled.set(true));
        assertThat(chainCalled).isFalse();
        assertThat(response.getStatus()).isEqualTo(401);
        request.addHeader("X-Walle-Device-Token", "device-secret");
        response = new MockHttpServletResponse();
        tokenFilter.doFilter(request, response, (req, res) -> chainCalled.set(true));
        assertThat(chainCalled).isTrue();
    }

    @Test
    void secureModeRequiresProvisioningTokenForRegistration() throws Exception {
        ReflectionTestUtils.setField(tokenFilter, "requireDeviceAuth", true);
        ReflectionTestUtils.setField(tokenFilter, "deviceApiToken", "device-secret");
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/users/register");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);
        tokenFilter.doFilter(request, response, (req, res) -> chainCalled.set(true));
        assertThat(response.getStatus()).isEqualTo(401);
        request.addHeader("X-Walle-Device-Token", "device-secret");
        response = new MockHttpServletResponse();
        tokenFilter.doFilter(request, response, (req, res) -> chainCalled.set(true));
        assertThat(chainCalled).isTrue();
    }

    @Test
    void secureModeRequiresAuthenticationForUserLookup() throws Exception {
        ReflectionTestUtils.setField(tokenFilter, "requireDeviceAuth", true);
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/users/getId/admin");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);
        tokenFilter.doFilter(request, response, (req, res) -> chainCalled.set(true));
        assertThat(chainCalled).isFalse();
        assertThat(response.getStatus()).isEqualTo(401);
    }
}
