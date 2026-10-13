package com.example.ragspringai.controller;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.ChatClientResponse;
import org.springframework.ai.chat.client.advisor.vectorstore.QuestionAnswerAdvisor;
import org.springframework.ai.document.Document;
import org.springframework.ai.google.genai.GoogleGenAiChatModel;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

@RestController
@RequestMapping("api")
public class ChatController {

    private final ChatClient localClient;
    private final ChatClient onlineClient;

    public ChatController(OllamaChatModel ollamaChatModel,
                          GoogleGenAiChatModel googleChatModel,
                          VectorStore vectorStore) {
        QuestionAnswerAdvisor ragAdvisor = QuestionAnswerAdvisor.builder(vectorStore)
                .searchRequest(SearchRequest.builder().topK(4).build())
                .build();

        this.localClient = ChatClient.builder(ollamaChatModel)
                .defaultAdvisors(ragAdvisor)
                .build();

        this.onlineClient = ChatClient.builder(googleChatModel)
                .defaultAdvisors(ragAdvisor)
                .build();
    }

    @PostMapping("/chat")
    public String chat(@RequestBody String message) {
        return ask(localClient, message);
    }

    @PostMapping("/chat_online")
    public String chatOnline(@RequestBody String message) {
        return ask(onlineClient, message);
    }

    @SuppressWarnings("unchecked")
    private String ask(ChatClient client, String message) {
        ChatClientResponse response = client.prompt()
                .user(message)
                .call()
                .chatClientResponse();

        String answer = response.chatResponse().getResult().getOutput().getText();

        List<Document> docs = (List<Document>) response.context()
                .get(QuestionAnswerAdvisor.RETRIEVED_DOCUMENTS);

        if (docs == null || docs.isEmpty()) {
            return answer;
        }

        Set<String> sources = new LinkedHashSet<>();
        for (Document doc : docs) {
            Object source = doc.getMetadata().get("source");
            if (source != null) {
                sources.add(source.toString());
            }
        }

        if (sources.isEmpty()) {
            return answer;
        }

        return answer + "\n\nSources: " + String.join(", ", sources);
    }
}