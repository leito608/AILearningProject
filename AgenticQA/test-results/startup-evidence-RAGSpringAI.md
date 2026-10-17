# RAGSpringAI Startup Evidence

**Date**: 2026-10-17

**Command**: `cd RAGSpringAI && ./mvnw spring-boot:run` with `GEMINI_API_KEY` empty

**Exit code**: 1

## Application Log Excerpt

```text
2026-10-17T12:25:29.623+07:00 WARN ConfigServletWebServerApplicationContext: Exception encountered during context initialization - cancelling refresh attempt: UnsatisfiedDependencyException creating 'chatController' through constructor parameter 1; 'googleGenAiChatModel' could not be created because Google GenAI configuration is incomplete.
2026-10-17T12:25:29.664+07:00 ERROR SpringApplication: Application run failed
Incomplete Google GenAI configuration: Provide 'api-key' for Gemini API or 'project-id' and 'location' for Vertex AI.
[ERROR] BUILD FAILURE
[ERROR] Process terminated with exit code: 1
```

## Readiness Probe

`curl http://localhost:8080` returned HTTP `000` (connection refused) after the process exited. No API request reached the application.
