# RAG PDF Assistant — User Stories

> Governed by: no project constitution was found.

**Feature Branch**: `rag-pdf-user-stories`

**Created**: 2026-10-17

**Status**: Draft
**Input**: Create user stories for project RAG.

## Scope Baseline

- **Discovery method**: Reviewed the RAG project README and its upload interface, ingestion/query workflow, PDF loader, vector-search component, and request/result types.
- **Total items discovered**: 4 user-facing capability areas: PDF ingestion, question answering, source display, and failure feedback.
- **Items in scope**: 4. The stories cover the local, single-user PDF question-answering workflow described by the project.
- **Out of scope**: User accounts, shared or remote workspaces, non-PDF formats, document deletion/management, and administration.

## User Scenarios & Testing

### User Story 1 — Add a PDF to the knowledge collection (Priority: P1)

As a user, I want to upload a PDF so that its contents can be used when I ask questions.

**Why this priority**: Ingestion makes the user's own documents available to the assistant and is the first step in the primary workflow.

**Independent Test**: Upload a readable PDF and verify that the ingestion workflow extracts its text, processes it, and makes its content available to a subsequent search.

**Acceptance Scenarios**:

1. **Given** the ingestion service is available, **When** I select a PDF, **Then** the application accepts one file and starts processing it for inclusion in the knowledge collection.
2. **Given** PDF processing completes successfully, **When** I ask a question covered by that PDF, **Then** content from the uploaded PDF can be retrieved.
3. **Given** a selected file is not a readable PDF, **When** ingestion is attempted, **Then** the application reports that processing failed and does not report the document as successfully ingested.

### User Story 2 — Ask a question about uploaded PDFs (Priority: P1)

As a user, I want to ask a question in plain language so that I can find an answer across the PDFs I have added.

**Why this priority**: Question answering is the primary user value of the project.

**Independent Test**: With a known PDF already in the collection, submit a question whose answer is present and another whose answer is absent; verify a grounded answer for the first and an explicit unknown response for the second.

**Acceptance Scenarios**:

1. **Given** at least one PDF has been processed, **When** I submit a non-empty question, **Then** the assistant returns an answer based on relevant retrieved document content.
2. **Given** retrieved content does not answer my question, **When** I submit it, **Then** the assistant clearly says it does not know rather than presenting an unsupported answer.
3. **Given** I choose a retrieval count within the supported range, **When** I submit my question, **Then** the answer is generated using no more than that number of retrieved text passages.
4. **Given** I submit an empty or whitespace-only question, **When** I attempt to ask it, **Then** no question is sent and I am prompted to enter a question.

### User Story 3 — See which documents support an answer (Priority: P2)

As a user, I want to see the source PDFs associated with an answer so that I can check where the information came from.

**Why this priority**: Source visibility helps users assess the relevance and trustworthiness of generated answers.

**Independent Test**: Ask a question answerable from a known PDF and verify that the answer view lists the source PDF; ask an unanswerable question and verify that no unsupported source is implied.

**Acceptance Scenarios**:

1. **Given** retrieved passages come from one or more PDFs, **When** the assistant returns an answer, **Then** the interface displays the associated source document names.
2. **Given** no source passage is retrieved, **When** the assistant returns an unknown response, **Then** the interface does not display a source as evidence for that response.

### User Story 4 — Understand and recover from processing failures (Priority: P2)

As a user, I want to know when upload, search, or answer generation fails so that I can correct the problem or try again.

**Why this priority**: The workflow depends on multiple services; clear failure feedback prevents a failed operation from appearing successful.

**Independent Test**: Make an ingestion or question-answering dependency unavailable and verify that the user sees an error state and can retry after the dependency is restored.

**Acceptance Scenarios**:

1. **Given** a required service is unavailable during ingestion, **When** I upload a PDF, **Then** the application reports that ingestion could not be completed and does not claim the PDF is ready for questions.
2. **Given** a required service fails while answering a question, **When** I submit it, **Then** the application displays a clear failure message and allows me to submit the question again.
3. **Given** an operation exceeds its allowed wait time, **When** the wait ends, **Then** the application reports that the result was not confirmed instead of displaying an empty answer as a successful result.

### Edge Cases

- A PDF contains no extractable text or is damaged: report an ingestion failure; do not mark it ready for questions.
- A PDF is selected again after already being uploaded: explain whether the existing document is being reused or processed again; do not imply a new copy exists unless it was added.
- No PDFs have been processed, or no relevant passages are found: return an explicit no-answer response without inventing document evidence.
- The selected retrieval count is outside the supported range: prevent submission or explain the permitted range.
- Embedding, retrieval, or answer generation is unavailable or times out: show a failure state that distinguishes an unconfirmed operation from a successful answer.
- The returned answer has no associated sources: do not present source attribution as if it existed.

## Requirements

### Functional Requirements

- **REQ-001**: The application MUST accept a single PDF file for ingestion and reject files that are not PDFs.
- **REQ-002**: The application MUST extract and process readable PDF text so that it can be searched in later questions.
- **REQ-003**: The application MUST report ingestion failure for unreadable or empty PDFs and MUST NOT represent them as successfully processed.
- **REQ-004**: The application MUST allow a user to submit a non-empty natural-language question about the processed PDF collection.
- **REQ-005**: The application MUST use retrieved document content to generate answers and MUST clearly indicate when that content does not contain an answer.
- **REQ-006**: The application MUST let the user select a retrieval count from 1 through 20, defaulting to 5, and MUST use no more than the selected count of passages.
- **REQ-007**: The application MUST display the names of source PDFs associated with retrieved passages and MUST NOT imply unsupported sources.
- **REQ-008**: The application MUST show a clear failure or unconfirmed status when ingestion or question answering cannot complete, including service failures and timeouts.
- **REQ-009**: The application MUST prevent an empty or whitespace-only question from being submitted.

### Key Entities

- **PDF source**: A user-provided PDF identified by its document name and the content processed from it.
- **Text passage**: A searchable segment extracted from a PDF and associated with its source document.
- **Question**: The user's natural-language request and selected retrieval count.
- **Answer**: The assistant's response, associated retrieved passages, and source document names when available.
- **Ingestion result**: The outcome of processing a PDF, including whether processing completed and how many passages were added.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In a benchmark of 20 readable PDFs, at least 19 are successfully processed and made searchable within 2 minutes each.
- **SC-002**: In a benchmark of 20 questions with answers present in the source PDFs, at least 18 responses include the expected answer and at least one relevant source.
- **SC-003**: For 20 questions whose answers are absent from the processed PDFs, every response clearly indicates that the answer is not known from the available content.
- **SC-004**: In usability testing, at least 9 out of 10 users can upload a PDF, ask a question, and identify the source document without assistance.

## Assumptions

- The product is a local, single-user tool; user accounts, permissions, and cross-user data isolation are not part of this scope.
- PDF is the only supported upload format, and one file is selected per upload action.
- All processed PDFs are available to subsequent questions in the same local knowledge collection.
- A displayed source name is sufficient attribution for this iteration; page-level citations and quoted passage previews are not specified.
- The success-criteria benchmark sizes and thresholds are proposed targets, not measured results from the current application.
- No project constitution, clarification artifact, or architecture/research artifact was found; scope was based on the project README and source files.
