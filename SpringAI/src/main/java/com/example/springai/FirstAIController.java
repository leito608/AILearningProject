package com.example.springai;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;
import java.time.Duration;

@CrossOrigin(origins = "*")
@RestController
public class FirstAIController {

    private final ChatClient chatClient;

    public FirstAIController(ChatClient.Builder chatClientBuilder) {
        this.chatClient = chatClientBuilder.build();
    }

    @GetMapping(value = "/askAI/{query}")
    public Flux<String> askAI(@PathVariable String query) {
        long start = System.currentTimeMillis();
//        return chatClient.prompt(query)
//                .stream()
//                .content();
        return chatClient.prompt()
                .system("check with official online data only, don't think by yourself")
                .user(query)
                .stream()
                .content();
    }
    @GetMapping(value = "/test", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> test() {
        return Flux.interval(Duration.ofSeconds(1))
                .map(i -> "tick " + i)
                .take(5);
    }
}
