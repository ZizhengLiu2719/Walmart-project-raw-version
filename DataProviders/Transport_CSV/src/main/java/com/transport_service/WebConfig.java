package com.transport_service;

import java.nio.charset.StandardCharsets;
import java.util.List;

import org.springframework.context.annotation.Configuration;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.converter.StringHttpMessageConverter;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    /**
     * This custom configuration ensures that Spring Boot correctly handles
     * text/plain content types for incoming requests. By explicitly adding the
     * StringHttpMessageConverter at the beginning of the list, we guarantee
     * that it is available to process CSV data sent as plain text to our
     * POST and PUT endpoints.
     *
     * Author: Michael's Assistant
     */
    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        // Add the StringHttpMessageConverter with UTF-8 support to the front of the list
        converters.add(0, new StringHttpMessageConverter(StandardCharsets.UTF_8));
    }
}
