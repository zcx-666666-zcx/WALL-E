package org.cpnrobot.cpnrobotmanagement.Filter;

import jakarta.servlet.FilterChain;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

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
}
