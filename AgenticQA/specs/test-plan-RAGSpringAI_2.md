# RAGSpringAI REST API Test Plan

**Source story:** `AgenticQA/user-stories/user-story-RAGSpringAI_2.md`

**Source specification:** `RAGSpringAI/specs/spec.md`

**Workflow constraints:** `AgenticQA/QAE2EPrompt.md`

**Scope:** REST API and application startup only. No HTML, browser, or browser-click testing. This is a plan, not execution evidence.

## 1. Scope and observable API contract

The API source exposes two `POST` operations:

| Operation | Endpoint | Request | Successful response |
|---|---|---|---|
| Local assistant | `/api/chat` | UTF-8 question text in the raw request body (`Content-Type: text/plain`) | Answer text; when retrieved documents have `source` metadata, the controller appends `Sources: <comma-separated names>` |
| Hosted assistant | `/api/chat_online` | Same | Same |

Use HTTP requests against the running Spring application (for example, RestAssured or an equivalent Java HTTP client). These are API-level tests, not direct controller-method tests. Do not send a JSON object unless a future contract explicitly changes the raw-string body format.

The bundled `spring-boot-reference.pdf` is ingested by a `CommandLineRunner` during startup, split into chunks, and stored in the pgvector table `vector_store`. The service skips ingestion if that table already contains a row whose metadata `source` equals the PDF filename. Both assistants use the same vector-store advisor, configured for up to four retrieved passages. The controller appends source names from retrieved passage metadata; if none of the retrieved passages has a source name, it returns the answer without a `Sources:` suffix.

**No health/readiness endpoint is defined in the inspected API source.** For a successful startup, first confirm the process remains alive and the HTTP port accepts connections, then use a real API request as the functional readiness probe. Do not add assumptions about a `/health` endpoint. For a failed-startup case, capture process exit/startup logs and confirm that the API is not serving successful answers.

## 2. Test environment and data safety

- Run against an isolated, disposable PostgreSQL/pgvector instance and a dedicated database/schema for each test run. Never point these tests at a developer, shared, staging, or production database.
- Keep the isolated database persistent only across the restart scenario that explicitly tests reuse. Start other scenarios with an empty database.
- Configure Ollama with the expected chat and embedding models for local happy paths. Hosted-assistant happy paths require a Gemini key supplied securely through the process environment or a local ignored Spring configuration file; never put the key in a test, command transcript, or report.
- For unavailable-service cases, use only test-owned disposable processes/containers or a controlled test network. Do not interrupt shared services.
- Prefix test-created rows/fixtures with a run UUID where metadata permits. The bundled document itself has a fixed source filename, so database/schema isolation—not a UUID on that source—is required to prevent collisions between runs.
- Before and after a test, query the isolated `vector_store` for counts and IDs by source. Teardown removes only rows created in the test-owned database/schema (including any seeded source-less fixture rows), then drops that database/schema or disposes of its container. Do not issue broad deletes against a shared store.
- On cleanup failure, retain the isolated instance for diagnosis, report the residual IDs, and do not claim cleanup passed. Never clean up data outside the run's isolated database/schema.
- Preserve response status, headers, and bounded/redacted response text; do not log API keys or sensitive environment values.

## 3. Acceptance-scenario traceability and API steps

Every scenario below is independently runnable with its stated starting state. “Pass” means the observable result matches the spec; a timeout or unavailable prerequisite is **blocked/unverified**, not a pass.

### User Story 1 — Make the included reference searchable

#### S1.1 — Fresh startup indexes readable reference (REQ-001)

**Precondition:** Empty isolated pgvector database; bundled PDF is present/readable; PostgreSQL, Ollama embedding, and local chat services are available.

1. Record the initial row count for `metadata->>'source' = 'spring-boot-reference.pdf'` (expect zero).
2. Start the application with the isolated database and test configuration; wait for a live process and listening HTTP port.
3. Query the isolated database and verify one or more chunks for the bundled source exist. Record chunk IDs and count.
4. Send an answerable, content-specific question to `POST /api/chat`; verify a successful HTTP response contains the expected reference fact and the bundled source name.
5. Tear down the isolated database and any test-owned services.

**Pass:** Startup completes; reference chunks are queryable; the API can answer from that indexed content. An open port without indexed data or a successful grounded API response is insufficient.

#### S1.2 — Restart reuses indexed reference without duplicates (REQ-002)

**Precondition:** Dedicated persistent isolated database with a successful initial ingestion; same application configuration and PDF on both starts.

1. Record all bundled-source row IDs, row count, and stable content/metadata fingerprints after the first successful start.
2. Call `/api/chat` with a known answerable question and record the expected successful outcome.
3. Stop the application cleanly, keep the isolated database intact, and start the application again.
4. Re-read source row IDs, count, and fingerprints; compare them with the first-start snapshot.
5. Call `/api/chat` again and verify the reference remains searchable and returns the expected fact/source.
6. Dispose of the isolated database after recording the comparison.

**Pass:** The second start preserves the existing indexed content and adds no duplicate chunks; the same source remains searchable.

#### S1.3 — Unreadable reference or failed indexing is not ready (REQ-003)

**Precondition:** A new isolated database and a test-only invalid/unreadable PDF fixture or a controllably failing indexing dependency. Do not alter the production PDF or production source.

1. Start the application with the invalid fixture, or induce a failure in a test-owned embedding/vector-store dependency during ingestion.
2. Capture startup exit status and relevant application logs; verify startup does not report ingestion as complete.
3. Verify the process fails to become API-ready (no successful answer from either endpoint). If it remains alive, probe `/api/chat` and verify it reports failure rather than an answer.
4. Inspect the isolated vector store for partial rows. Record them; verify they are not treated as a completed/ready reference by the test. Clean only this isolated store.

**Pass:** The failure is observable and no request is represented as a successful answer over an unsuccessfully processed reference. **Important limitation:** the current API has no ingestion-status endpoint; this scenario can verify startup/error and API behavior, but cannot assert a dedicated readiness flag that the API does not expose. Partial batches may have been persisted before an indexing error, so record their exact state rather than assuming rollback.

### User Story 2 — Ask a question using the local assistant

#### S2.1 — Local answer uses relevant indexed content (REQ-004, REQ-005)

**Precondition:** Reference successfully indexed; PostgreSQL/pgvector, Ollama embedding, and Ollama chat are available.

1. Send raw UTF-8 text containing a question with an unambiguous answer in the bundled reference to `POST /api/chat`.
2. Verify a successful HTTP status and a non-empty answer containing the preselected expected fact (case/whitespace tolerant, not a full generated-text equality check).
3. Verify the response includes `Sources: spring-boot-reference.pdf`.
4. Send a second independently answerable question and confirm the endpoint accepts successive requests.
5. Clean up the isolated vector data and test-owned services.

**Pass:** Local endpoint returns a substantive answer grounded in the reference and identifies its source.

#### S2.2 — Local assistant abstains when reference does not answer (REQ-005)

**Precondition:** Reference indexed in an isolated store; local services available; selected question asks for a specific fact that has been verified absent from the PDF.

1. Send the out-of-scope question to `POST /api/chat`.
2. Verify the response explicitly indicates that the answer is unavailable/not found in the reference; do not accept a confident unsupported factual answer as passing.
3. Verify the response does not append a source attribution unless relevant retrieved passages actually carry source metadata.
4. Repeat with the planned unanswered-question benchmark (see §5); record each outcome.
5. Clean up the isolated data.

**Pass:** The assistant abstains for every required unanswered benchmark item; any unsupported answer is a failure, not a wording variation.

#### S2.3 — Local chat or search dependency failure is reported (REQ-009)

**Precondition:** App is running with a test-owned isolated database; one required local dependency can be made unavailable without affecting other environments.

1. With the app serving HTTP, make the local chat model unavailable in the test environment and send an answerable question to `/api/chat`.
2. Verify a failure status (non-2xx) or, if the framework returns another status, a clearly failed response that is not a successful-looking empty answer. Record exact status/body.
3. In a separate fresh run, make search/PostgreSQL unavailable. Test startup and the HTTP operation when the application remains reachable; otherwise record the failed startup and lack of API readiness.
4. For embedding unavailability, induce the failure during fresh startup/indexing and apply S1.3; do not claim a request-level result if the application cannot start.
5. Restore/dispose of only the test-owned dependencies and clean the isolated store.

**Pass:** Each exercised failure is reported as a failure; none is reported as a successful answer or completed ingestion. Record a distinct result for chat, search, and embedding failure modes.

### User Story 3 — Ask a question using the hosted assistant

#### S3.1 — Configured hosted assistant answers from indexed reference (REQ-006)

**Precondition:** Reference indexed; PostgreSQL/pgvector and embedding service available; Gemini service reachable; key provided securely to the test process.

1. Send an answerable question as raw UTF-8 text to `POST /api/chat_online`.
2. Verify successful HTTP status, non-empty response, and the expected reference fact.
3. Verify `Sources: spring-boot-reference.pdf` appears when the returned retrieved document has that metadata.
4. Where running the full acceptance benchmark, repeat with the 20 preselected answerable questions for the hosted assistant.
5. Revoke/clear the test process's key and clean up the isolated database.

**Pass:** The configured hosted option returns a grounded answer and source attribution for the expected benchmark cases. If no key/service access is authorized, mark this scenario blocked/unverified; do not substitute a local response and call it hosted coverage.

#### S3.2 — Unconfigured or unavailable hosted assistant reports failure (REQ-006)

**Precondition:** Use a fresh isolated app process. Run two separate cases: no hosted credential/configuration, and configured credentials with the hosted service made unavailable or returning an authentication/service error in a controlled test environment.

1. Start the app with hosted configuration absent; record whether startup succeeds and whether the HTTP port is available.
2. If the app is serving, POST an answerable question to `/api/chat_online` and verify a clear failure outcome, not an empty successful answer. Also verify `/api/chat` remains usable if the local dependencies are available.
3. If the app fails before binding because the hosted model is unconditionally required, record that as a failure against the specified request-level behavior—not as a passing “clear endpoint failure.”
4. In the configured-but-unavailable case, POST to `/api/chat_online`; verify failure status/body, not a successful-looking empty answer. Check the local endpoint separately to establish that hosted failure did not masquerade as local success.
5. Dispose of test-owned processes/dependencies and the isolated store.

**Pass:** A hosted request made while the app is running has an explicit failure outcome. Startup failure before the request is a documented contract gap/failure for this acceptance scenario, not a pass. The inspected controller injects and constructs both model clients unconditionally, so whether missing hosted configuration prevents all application startup must be established by execution.

### User Story 4 — Check the sources behind an answer

#### S4.1 — Returned source name identifies retrieved document (REQ-007)

**Precondition:** Isolated vector store contains retrievable chunks with `source = 'spring-boot-reference.pdf'`; the chosen question retrieves them.

1. Call `/api/chat` with a question targeted to those chunks; repeat with `/api/chat_online` when hosted configuration is available.
2. Verify the response has a source suffix naming `spring-boot-reference.pdf`.
3. If multiple retrieved passages share the same source, verify the name is not misleadingly duplicated; record actual formatting.
4. Confirm the expected fact is present as well as the source name, so a source-only response cannot pass.
5. Clean up the isolated store.

**Pass:** Each tested assistant reports the source name actually associated with retrieved passages.

#### S4.2 — No source metadata is not attributed (REQ-008)

**Precondition:** Isolated store contains a retrievable, test-owned passage without a `source` metadata key; no bundled-source rows are present or selectable for the controlled question.

1. Insert the source-less passage into the test-owned store and record its ID and run UUID in the test ledger.
2. POST a question that retrieves that passage to `/api/chat`; verify no `Sources:` suffix or invented document name is appended.
3. Repeat through `/api/chat_online` where the hosted configuration is available.
4. Remove only the fixture by its recorded ID (or dispose of the isolated database) and verify it is gone.

**Pass:** The API does not assert or imply a source document name when retrieved passages lack source metadata. Do not mistake an LLM's prose about a source for controller-provided attribution; inspect the explicit response suffix and separately flag any generated unsupported attribution.

## 4. API contract and security-boundary probes

These supplementary probes do not invent acceptance behavior where the spec is silent:

- Confirm `POST` is accepted on both documented paths and a wrong HTTP method is not treated as an answer.
- Probe missing body, empty body, and wrong content type in an isolated run. Record actual status/body; treat unexpected successful substantive answers as defects, but do not assert undocumented validation messages.
- Verify raw question text is carried as submitted; do not assume a JSON envelope or response JSON schema.
- The inspected controller has no authentication/authorization annotations or security configuration in the reviewed API source. Expect these API operations to be unauthenticated in the current implementation; **do not write tests that require 401/403 or invent credentials**. Record this as a security limitation: anyone able to reach the API can invoke local or hosted inference, potentially consume paid hosted quota, and submit arbitrary content. Restrict these tests to an isolated trusted network. Authentication, authorization, rate limiting, and user separation are out of scope and remain product risks.

## 5. Success criteria, repetitions, and reporting

Run acceptance criteria as repeatable API-level checks against isolated state. The spec labels these targets as proposed, not previously measured:

| Spec target | Planned evidence |
|---|---|
| SC-001: 20 fresh application starts | 20 independent empty-database startup/index/search cycles with the readable PDF and available dependencies; all 20 must become searchable. |
| SC-002: 20 restarts | 20 restart cycles over their own persistent isolated stores; compare source row IDs/count/fingerprints before and after each restart; no duplicates in any cycle. |
| SC-003: 20 answerable questions per configured assistant; at least 18 expected answers and source names | Run the same pre-reviewed 20-question benchmark through each assistant that is configured. Report per-question fact and source assertions separately. Do not count an unconfigured hosted assistant as covered. |
| SC-004: 20 unanswered questions; every response abstains | Run the 20 pre-reviewed out-of-reference questions through the configured assistant(s); any unsupported factual answer fails the criterion. |
| SC-005: required-service failures always reported as failures | Exercise controlled chat, embedding, search/database, and hosted-service failure modes. Record HTTP result or startup exit/readiness result for every mode; no successful-looking empty answer or completed-ingestion claim may pass. |

Maintain a scenario ledger with scenario ID, linked REQ/SC, isolated environment/run UUID, exact HTTP method/path/content type (never credentials), status, bounded assertion outcome, database before/after counts, cleanup outcome, and PASS/FAIL/BLOCKED. Never report tests as executed based on this plan.

## 6. Execution constraints and deliverable naming

- Use a framework HTTP client or REST Assured against the live Spring REST API. No browser automation, HTML assertions, UI navigation, or browser clicks.
- The application has no explicit health endpoint. Record startup logs/process/port evidence and use a meaningful API request for functional readiness; a model-dependent readiness probe may itself fail because an upstream service is down.
- Preserve the primary integration behavior with real pgvector and Ollama for local acceptance. Use the real hosted service only with explicitly authorized configuration. Controlled service-failure injection is performed only in disposable test-owned environments.
- Test-only fixtures/configuration may be added by a later test implementation, but this plan does not authorize changes to production source, existing artifacts, or shared data.
- If later producing runnable tests and reports from this plan, use the `_2` suffix for new output filenames (for example, `RagSpringAiApiAcceptanceTests_2.java` and `qa-e2e-report_2.md`). Do not overwrite existing QA plans, tests, reports, or other artifacts.
- Execution is fail-fast on failed startup; collect bounded startup logs and stop downstream scenarios that require a ready app. Do not turn infrastructure failures into passing answers.
