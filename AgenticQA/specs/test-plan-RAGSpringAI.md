# RAGSpringAI API Test Plan

## Source, scope, and status

- **Source story/spec**: [`RAGSpringAI/specs/spec.md`](../../RAGSpringAI/specs/spec.md), Draft; this plan preserves its acceptance criteria as the source of truth.
- **Relevant API/behavior sources**: `RAGSpringAI/src/main/java/com/example/ragspringai/controller/ChatController.java`, `RAGSpringAI/src/main/java/com/example/ragspringai/ingestion/DocumentIngestionService.java`, `RAGSpringAI/src/main/resources/application.properties`, `RAGSpringAI/compose.yaml`, and `RAGSpringAI/pom.xml`.
- **Target**: HTTP API only. The controller exposes `POST /api/chat` (local Ollama) and `POST /api/chat_online` (hosted Google GenAI); each accepts a raw text request body and returns a string response.
- **Base URL**: Not supplied. Configure as `baseUrl`; Spring Boot's default is `http://localhost:8080` when no port override is set.
- **Stage**: AgenticQA stages 1–2 only (story/criteria analysis and test-plan authoring). This is a plan, not evidence of execution.
- **Explicit exclusions**: No UI, browser/MCP exploration, Playwright script, test implementation or execution, service startup, report, commit, or production change is included or authorized by this task.

## Stage 1 — Story and acceptance-criteria analysis

- **Actor and goal**: A single learner asks natural-language questions about the bundled Spring Boot reference, can choose local or hosted answer generation, and can identify the source document.
- **Precondition**: The bundled `spring-boot-reference.pdf` is available and has been indexed into the configured pgvector store. Local answering requires Ollama chat and embedding models. Hosted answering requires Google GenAI configuration and network access.
- **Observable surface**: HTTP status and response body for the two POST endpoints; for ingestion, startup outcome plus subsequent searchability. There is no documented UI, ingestion endpoint, readiness endpoint, user account, or chat-history endpoint.
- **Ambiguities retained rather than invented**:
  - Exact wording for “answer not available” and service errors is unspecified. Tests should assert a meaningful refusal/failure and absence of a success-shaped answer, not exact LLM prose.
  - Empty/whitespace question behavior and response media type are not specified as acceptance criteria. Send a non-empty plain-text body for core scenarios; do not make undocumented validation behavior a release condition.
  - The story calls the hosted option configurable, but configuration failure may occur at application startup rather than only on a request. Record the actual failure boundary; do not assume the app must remain up without the hosted provider.
  - Success-criteria percentages in the source spec are proposed targets, not measured results. Use their stated sample sizes only if the team elects to validate those broader benchmarks.

## Test approach and environment

- **App type**: REST API only; no rendered HTML or client-side UI.
- **Primary validation**: Java 17 / Maven project, Spring Boot HTTP integration tests against a random-port application instance, using JDK `HttpClient` or an already-available Spring test HTTP client. Exercise actual HTTP requests and preserve real dependency wiring for acceptance scenarios.
- **Real dependencies**:
  - **PostgreSQL with pgvector** is required for fidelity. The checked-in `compose.yaml` provides `pgvector/pgvector:pg16` on port 5432 with database `vectordb`; use a dedicated disposable test database/instance, never a developer's shared or production data. The ingestion idempotency query uses PostgreSQL JSON metadata syntax, so H2 is not an equivalent fallback.
  - **Ollama** at the configured base URL (`http://localhost:11434`) with chat model `llama3.2:3b` and embedding model `nomic-embed-text` is required for local RAG acceptance tests. The compose definition's Ollama service is commented out; arrange it separately and ensure the models are available before testing.
  - **Google GenAI** using `GEMINI_API_KEY` and configured model `gemini-3.5-flash-lite` is required for hosted-assistant acceptance tests. Keep credentials in the environment/secret store; never put values in tests, command output, or artifacts. Calls may incur provider charges and require outbound network access.
  - The PDF reader and reference PDF are local classpath inputs. Tika extraction and the real vector-store path are part of ingestion acceptance.
- **Fault paths**: For dependency-unavailable scenarios, use an isolated test configuration or controlled outage against only the disposable test environment, then assert the observed HTTP/startup failure. Do not substitute mocked chat/search for the real-dependency happy paths. A narrowly scoped fault-injection seam may be needed to reproduce failure after a partial vector write.
- **Data isolation and cleanup**: Start from a dedicated empty vector database for first-ingestion tests. Reuse that same isolated database only for the restart/idempotency scenario. Use unique test identifiers for any additional seeded passages, delete them through the vector-store API where supported, and drop/reset the dedicated database after the suite. Never truncate shared data. Ensure a failed-startup test also cleans any partially written vectors.
- **Test data**:
  - For grounded-answer tests, select a short factual claim actually present in the bundled PDF and record the verified expected fact and source filename in test fixtures. Do not fabricate document contents or assert a single exact generated sentence.
  - For no-answer tests, use a specific question whose answer is demonstrably absent from the bundled PDF and whose expected refusal can be reviewed against a documented rubric.
  - For missing-source metadata, seed a matching passage in the isolated vector store without a `source` metadata value, then verify the API response does not append a `Sources:` attribution. Remove the seed after the scenario.
  - For ingestion failure, use a test-only missing/unreadable PDF resource or a controlled indexing failure in an isolated test launch; do not alter the production PDF.
- **Browser and accessibility**: **N/A** — the in-scope product surface is JSON/text HTTP API, with no HTML UI, browser flow, or rendered controls. Playwright, browser coverage, and UI accessibility checks do not apply. Use HTTP assertions and source-document attribution checks instead.
- **Authentication/authorization**: **N/A** — no authentication, authorization, account, or credential contract is present in the inspected application sources or story. Do not invent a missing/invalid-credentials scenario.
- **Persistence**: **N/A for user/account/conversation-history persistence** — none is described or exposed. **Not N/A for document indexing**: PostgreSQL/pgvector persistence is a real supported dependency and is required to test startup indexing and restart idempotency.
- **Pass/fail rule**: A scenario passes only when all listed observable outcomes hold. A service failure must not be counted as a successful answer; a startup/indexing failure must not be counted as a searchable-ready state. Capture actual status/body and startup outcome without asserting undocumented wording.

## Stage 2 — Independently runnable scenarios

### RAGSPR-01 — Index the bundled reference on first startup

- **Trace**: User Story 1, Acceptance Scenario 1; REQ-001; SC-001.
- **Preconditions / starting state**: Dedicated pgvector database is empty; bundled PDF is readable; PostgreSQL and Ollama embedding service are available.
- **Actions**:
  1. Start the application in the isolated test environment.
  2. Wait for process startup to complete.
  3. Submit a question through `POST /api/chat` whose verified answer is in the PDF.
- **Expected**: Startup completes; the subsequent question can retrieve/use the reference content and returns a relevant answer. A running process alone is not proof of successful indexing.
- **Pass condition**: The query demonstrates access to the verified reference fact after first startup, with no startup/indexing error.
- **Data / cleanup**: Empty isolated database before the test; drop/reset it afterward.

### RAGSPR-02 — Reuse indexed content after restart without duplicates

- **Trace**: User Story 1, Acceptance Scenario 2; REQ-002; SC-002.
- **Preconditions / starting state**: A successful RAGSPR-01 ingestion exists in the isolated database; dependency services are available.
- **Actions**:
  1. Record the isolated store's matching source-document count (or stable equivalent) after successful initial ingestion.
  2. Restart the application against the same database.
  3. Query a known fact from the PDF and inspect the source-document count again.
- **Expected**: Startup reuses the indexed reference, the count does not increase through duplicate ingestion, and content remains searchable.
- **Pass condition**: Search still succeeds and the before/after count is unchanged for the reference source.
- **Data / cleanup**: Do not clear the vector store between the two launches; drop/reset the database after the test.

### RAGSPR-03 — Fail startup when reading or indexing the reference fails

- **Trace**: User Story 1, Acceptance Scenario 3; REQ-003; REQ-009; SC-005.
- **Preconditions / starting state**: Isolated database; test-only unreadable/missing PDF fixture or reproducible indexing failure; no shared service data.
- **Actions**:
  1. Launch with the controlled read/index failure.
  2. Observe process/startup outcome and any available logs.
  3. If startup remains available, submit a question and inspect whether the app presents the reference as ready.
- **Expected**: The failure is surfaced; ingestion is not represented as complete/searchable when it did not complete. A failed request/startup must not return a successful-looking answer.
- **Pass condition**: Startup fails or the request is explicitly reported as failure, and incomplete ingestion is not treated as ready.
- **Data / cleanup**: Remove partial vectors and the test database after the attempt.

### RAGSPR-04 — Answer a question grounded in the reference with the local assistant

- **Trace**: User Story 2, Acceptance Scenario 1; REQ-004, REQ-005; SC-003.
- **Preconditions / starting state**: Reference indexed; Ollama chat and embedding models plus pgvector are available.
- **Actions**:
  1. POST a non-empty plain-text question whose answer is verified in the reference to `/api/chat`.
  2. Inspect status and body against the fact-based answer rubric.
- **Expected**: A successful response includes the expected fact or a semantically equivalent answer informed by retrieved reference content.
- **Pass condition**: Successful HTTP response and grounded answer; do not require byte-for-byte model output.
- **Data / cleanup**: Use bundled reference only; clean the isolated database after the test.

### RAGSPR-05 — Decline a question not answered by the reference (local)

- **Trace**: User Story 2, Acceptance Scenario 2; REQ-005; SC-004.
- **Preconditions / starting state**: Reference indexed; local model and search services available; selected question's answer is absent from the PDF.
- **Actions**:
  1. POST the unanswerable question to `/api/chat`.
  2. Inspect the response for an explicit lack-of-evidence/unknown outcome and unsupported claims.
- **Expected**: The assistant indicates that the available reference does not answer the question; it does not assert an unsupported fact as grounded.
- **Pass condition**: Response satisfies the reviewed refusal rubric; exact wording is not fixed.
- **Data / cleanup**: Record the question and why its answer is absent in the test fixture; clean the isolated database afterward.

### RAGSPR-06 — Report local chat or search dependency failure

- **Trace**: User Story 2, Acceptance Scenario 3; REQ-009; SC-005.
- **Preconditions / starting state**: Application is running with isolated test data; one required local chat, embedding, or search dependency is deliberately unavailable in a controlled test environment.
- **Actions**:
  1. Submit a non-empty question to `/api/chat`.
  2. Capture actual HTTP status and response body.
- **Expected**: Request is observably failed (non-success HTTP status or another explicit failure contract); no normal answer is returned as if the operation succeeded.
- **Pass condition**: Failure is distinguishable from a successful answer and is not an empty/success-shaped response.
- **Data / cleanup**: Restore the dependency and drop/reset the dedicated database after testing.

### RAGSPR-07 — Answer a grounded question with the configured hosted assistant

- **Trace**: User Story 3, Acceptance Scenario 1; REQ-006; SC-003.
- **Preconditions / starting state**: Reference indexed; `GEMINI_API_KEY` is safely configured; Google GenAI service/network and pgvector are available.
- **Actions**:
  1. POST a verified answerable question to `/api/chat_online`.
  2. Inspect status and body against the same fact-based rubric used for the local option.
- **Expected**: Successful response is informed by retrieved reference content.
- **Pass condition**: The expected fact is present or stated semantically equivalently; no credentials appear in evidence.
- **Data / cleanup**: Calls may incur charges; use a small, bounded request count and clean the isolated vector database.

### RAGSPR-08 — Report hosted-assistant missing configuration or outage

- **Trace**: User Story 3, Acceptance Scenario 2; REQ-006; REQ-009; SC-005.
- **Preconditions / starting state**: Isolated environment. Exercise missing `GEMINI_API_KEY` and configured-but-unavailable hosted service as separate cases where the application can be launched safely.
- **Actions**:
  1. Start with hosted configuration absent, if startup permits.
  2. Submit a non-empty question to `/api/chat_online` when reachable; separately repeat with the hosted service unavailable.
  3. Record whether failure occurs at application startup or request time.
- **Expected**: Each applicable case has an explicit failed outcome, not a successful-looking empty answer. If missing configuration prevents startup, capture that startup failure rather than claiming a request-level behavior.
- **Pass condition**: The configured/unavailable state is surfaced at its actual boundary; no fabricated successful answer is observed.
- **Data / cleanup**: Never write a real key into fixture files or logs; restore environment and clean the test database.

### RAGSPR-09 — Include source-document name when retrieved metadata has one

- **Trace**: User Story 4, Acceptance Scenario 1; REQ-007.
- **Preconditions / starting state**: Successful retrieval of a passage whose metadata contains `source`; bundled PDF is the normal fixture.
- **Actions**:
  1. Ask an answerable question using `/api/chat`.
  2. Inspect the returned body for the actual source filename associated with retrieved content.
- **Expected**: Response identifies the associated source document name (currently expected to be `spring-boot-reference.pdf` for the bundled reference); do not assert page-level citations.
- **Pass condition**: Correct source name is present and corresponds to retrieved content.
- **Data / cleanup**: Use the isolated store; reset after testing. Repeat against `/api/chat_online` only if source attribution parity across both assistants is part of the chosen coverage.

### RAGSPR-10 — Omit source attribution when retrieved metadata lacks a source

- **Trace**: User Story 4, Acceptance Scenario 2; REQ-008.
- **Preconditions / starting state**: Isolated vector store contains a matching passage without `source` metadata; relevant retrieval can be achieved without conflicting bundled passages.
- **Actions**:
  1. Query the matching passage through `/api/chat`.
  2. Inspect the full response for source claims or a `Sources:` suffix.
- **Expected**: The response does not claim or imply a source document when retrieved passages have no source name.
- **Pass condition**: No unsupported source label is present.
- **Data / cleanup**: Seed using test-only vector-store setup; delete the seeded passage and reset the isolated database.

## Coverage and execution notes

| Source acceptance criterion | Planned scenario |
|---|---|
| User Story 1, AC 1 — first startup makes reference searchable | RAGSPR-01 |
| User Story 1, AC 2 — restart reuses content without duplicates | RAGSPR-02 |
| User Story 1, AC 3 — read/index failure is surfaced, not ready | RAGSPR-03 |
| User Story 2, AC 1 — local answer informed by relevant content | RAGSPR-04 |
| User Story 2, AC 2 — local assistant declines unsupported answer | RAGSPR-05 |
| User Story 2, AC 3 — local/search service unavailable is a failure | RAGSPR-06 |
| User Story 3, AC 1 — configured hosted answer uses retrieved content | RAGSPR-07 |
| User Story 3, AC 2 — hosted configuration/service failure is clear | RAGSPR-08 |
| User Story 4, AC 1 — source name included when metadata exists | RAGSPR-09 |
| User Story 4, AC 2 — no implied source when metadata is absent | RAGSPR-10 |

The current Maven test source has only a `@SpringBootTest` context-load smoke test. This plan does not run or modify it. The plan's API scenarios should be implemented as isolated, independently runnable HTTP integration tests and later run from the project's Maven test workflow; no Playwright installation or browser is required.

## Known blockers and risks (not execution results)

1. **Application URL/environment unavailable**: No target URL or approved test environment was supplied. No application or dependency service was started, and no requests were sent.
2. **Partial-ingestion correctness risk**: `DocumentIngestionService` writes chunks in batches and determines “already ingested” by whether any vector row has the PDF's `source`. If an indexing failure occurs after at least one batch was stored, a later startup can skip the reference despite incomplete ingestion. RAGSPR-03 must expose this behavior; the current source may not satisfy the acceptance criterion. Do not mask it with a test-only success.
3. **Readiness observability**: No health/readiness or ingestion-status endpoint was found in the inspected API source. RAGSPR-01/03 therefore use startup outcome plus a real follow-up retrieval as observable evidence; a distinct readiness contract cannot be asserted without a product requirement/API.
4. **Hosted configuration boundary**: The hosted model is constructed in the controller alongside the local model. Whether absent Google credentials fail startup or only hosted requests is environment/framework-dependent and must be observed; the test must not assume the app remains available.
5. **Model nondeterminism and cost**: Local and hosted generation may vary; acceptance should use a reviewed factual rubric, bounded requests, and no exact-string assertions. Hosted calls may incur charges.
6. **Failure injection**: A deterministic mid-batch indexing failure may require test-only infrastructure/fault injection. If it cannot be reproduced without production changes or shared data, leave that subcase explicitly blocked rather than weakening the criterion.
