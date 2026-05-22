package org.cpnrobot.cpnrobotmanagement.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.Resource;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.resource.PathResourceResolver;

import java.io.IOException;

@Configuration
public class SpaConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/**")
                .addResourceLocations("classpath:/static/")
                .resourceChain(true)
                .addResolver(new PathResourceResolver() {
                    @Override
                    protected Resource getResource(String resourcePath, Resource location) throws IOException {
                        Resource resource = location.createRelative(resourcePath);
                        if (resource.exists() && resource.isReadable()) {
                            return resource;
                        }
                        // SPA fallback: 非 API、非静态资源路径 → 返回 index.html
                        if (!resourcePath.startsWith("api/") && !resourcePath.contains(".")) {
                            Resource indexHtml = location.createRelative("index.html");
                            if (indexHtml.exists() && indexHtml.isReadable()) {
                                return indexHtml;
                            }
                        }
                        return null;
                    }
                });
    }
}
