# RAGSpringAI — User Stories

> Governed by: no project constitution was found.

**Feature Branch**: `ragspringai-user-stories`

**Created**: 2026-10-17

**Status**: Draft  
**Input**: Create user stories for RAGSpringAI.

## Scope Baseline

- **Discovery method**: Reviewed the RAGSpringAI project description, application configuration, document-ingestion service, chat controller, bundled PDF, and existing test.
- **Total items discovered**: 3 user-facing capability areas: prepare the bundled reference for search, answer questions with either supported chat option, and identify retrieved source documents.
- **Items in scope**: 3 capability areas evidenced by the current project.
- **Out of scope**: User-managed PDF uploads, document collections or deletion, a graphical user interface, user accounts, conversation history, and administration.

## User Scenarios & Testing

### User Story 1 — Make the included reference searchable (Priority: P1)

As a learner using RAGSpringAI, I want the included Spring Boot reference to be prepared for search when the application starts so that I can ask questions about it without manually importing it.

**Why this priority**: Preparing the reference is a prerequisite for the application's main purpose: answering document-based questions.

**Independent Test**: Start the application with its required services available and verify that content from the included reference becomes available to a subsequent question. Restart it and verify the same source is not ingested again as a duplicate.

**Acceptance Scenarios**:

1. **Given** the included reference has not yet been processed and required services are available, **When** the application starts, **Then** its readable content is made available for search.
2. **Given** the included reference has already been processed, **When** the application starts again, **Then** the existing indexed content is reused and the reference is not ingested again as a duplicate.
3. **Given** the reference cannot be read or indexing cannot complete, **When** the application starts, **Then** the failure is surfaced and the reference is not reported as ready for questions.

### User Story 2 — Ask a question using the local assistant (Priority: P1)

As a learner, I want to ask a natural-language question about the included reference using the local assistant so that I can get an answer grounded in that material.

**Why this priority**: Question answering is the primary value of the project, and the local assistant provides that core journey without requiring the hosted option.

**Independent Test**: With the reference indexed, submit a question whose answer is present in it and verify the response is based on relevant retrieved content. Submit a question whose answer is absent and verify the response does not claim unsupported knowledge.

**Acceptance Scenarios**:

1. **Given** the reference is searchable, **When** I submit a question through the local assistant, **Then** I receive an answer informed by relevant content from the reference.
2. **Given** the searchable content does not provide an answer, **When** I submit the question, **Then** the assistant indicates that the answer is not available from the reference rather than presenting an unsupported answer.
3. **Given** the local assistant or search service is unavailable, **When** I submit a question, **Then** the request is reported as failed and is not presented as a successful answer.

### User Story 3 — Ask a question using the hosted assistant (Priority: P2)

As a learner, I want to ask a natural-language question using the hosted assistant so that I can use the alternative answer-generation option when it is configured and available.

**Why this priority**: The alternative assistant provides another way to generate answers, while the local assistant already supports the core question-answering journey.

**Independent Test**: With the reference indexed and the hosted assistant configured, submit an answerable question through that option and verify that the response uses retrieved reference content. Verify a clear failure when the hosted service is unavailable or not configured.

**Acceptance Scenarios**:

1. **Given** the reference is searchable and the hosted assistant is configured, **When** I submit a question through that assistant, **Then** I receive an answer informed by relevant content from the reference.
2. **Given** the hosted assistant is not configured or is unavailable, **When** I submit a question through it, **Then** I receive a clear failure outcome rather than a successful-looking empty answer.

### User Story 4 — Check the sources behind an answer (Priority: P2)

As a learner, I want to see the source documents associated with retrieved content so that I can check what material informed an answer.

**Why this priority**: Source names help users assess whether an answer is grounded in the intended reference.

**Independent Test**: Ask an answerable question and verify that the response identifies the retrieved reference source. Ask a question with no retrieved source and verify that the response does not imply a source was found.

**Acceptance Scenarios**:

1. **Given** retrieved passages have source-document metadata, **When** an answer is returned, **Then** the response identifies the associated source document name.
2. **Given** no source document is associated with retrieved passages, **When** an answer is returned, **Then** the response does not claim or imply source attribution.

### Edge Cases

- The bundled reference is missing, unreadable, or contains no extractable text: surface an ingestion failure and do not represent it as searchable.
- Ingestion stops partway through: do not report successful completion unless the reference is available for search.
- The reference has already been indexed: reuse it instead of silently creating duplicate indexed content on every restart.
- No relevant passages are found for a question: do not fabricate an answer or source attribution.
- The local or hosted assistant, embedding service, or vector search service is unavailable: report failure rather than returning a successful-looking empty response.
- A retrieved passage has no source name: include only source names that are actually available.

## Requirements

### Functional Requirements

- **REQ-001**: The application MUST make the included reference searchable before treating document-based question answering as ready.
- **REQ-002**: The application MUST avoid re-ingesting the included reference when it has already been successfully indexed.
- **REQ-003**: The application MUST surface reference-reading or indexing failures and MUST NOT report an unsuccessfully processed reference as ready.
- **REQ-004**: The application MUST allow a user to submit a natural-language question to the local assistant about searchable reference content.
- **REQ-005**: The application MUST use relevant retrieved reference content to inform answers and MUST indicate when the available content does not answer the question.
- **REQ-006**: The application MUST allow a user to submit a question to the hosted assistant when that option is configured and MUST clearly report configuration or service failures.
- **REQ-007**: The application MUST identify source document names associated with retrieved content when those names are available.
- **REQ-008**: The application MUST NOT imply source attribution when retrieved content has no associated source document.
- **REQ-009**: The application MUST report failures from required chat, embedding, or search services as failures rather than successful-looking answers.

### Key Entities

- **Reference document**: The bundled document whose content is processed and made searchable.
- **Text passage**: A searchable portion of the reference document associated with source metadata.
- **Question**: A user's natural-language request submitted to one of the supported assistants.
- **Answer**: A response to a question, informed by retrieved passages and associated source names when available.
- **Ingestion result**: The outcome of preparing the reference for search, including whether it was successfully indexed or already available.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In 20 application-start tests with a readable, unindexed reference and available dependencies, the reference is searchable after startup in all 20 tests.
- **SC-002**: In 20 restart tests after successful indexing, no duplicate reference content is added in any test.
- **SC-003**: In a benchmark of 20 questions answerable from the reference, at least 18 responses from each configured assistant include the expected answer and identify the source document.
- **SC-004**: For 20 questions whose answers are absent from the reference, every response indicates that the available content does not answer the question.
- **SC-005**: In tests where a required service is unavailable, 100% of affected requests or startup attempts are reported as failures and none are presented as successful answers or completed ingestion.

## Assumptions

- The product is a local, single-user learning application.
- The bundled Spring Boot reference PDF is the sole document source in this iteration.
- The reference is prepared automatically during application startup; users do not upload or manage documents.
- The local and hosted assistants are alternative ways to generate answers over the same searchable content.
- The hosted assistant is available only when its required configuration is present.
- Source document names are sufficient attribution for this iteration; page-level citations and passage previews are not specified.
- Success-criteria thresholds are proposed acceptance targets, not measured results.
- No project constitution, clarification artifact, or architecture/research artifact was found.
