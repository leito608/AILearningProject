package com.example.springai;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SpringAiApplication implements CommandLineRunner {

    //@Autowired
    ChatClient chatClient;

    public SpringAiApplication(ChatClient.Builder chatClientBuilder) {
        this.chatClient = chatClientBuilder.build();
    }
    public static void main(String[] args) {
        SpringApplication.run(SpringAiApplication.class, args);
    }

    @Override
    public void run(String... args) throws Exception{
        String promptText = "what is the latest version of spring boot";
        ChatClient.ChatClientRequestSpec requestSpec = chatClient.prompt(promptText);
        ChatClient.CallResponseSpec responseSpec = requestSpec.call();
        System.out.println(responseSpec.chatResponse());
    }
}
