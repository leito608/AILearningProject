# RAGSpringAI User Story

**Source of truth**: [RAGSpringAI specification](../../RAGSpringAI/specs/spec.md)

**Test plan**: [RAGSpringAI API test plan](../specs/test-plan-RAGSpringAI.md)

## Scope

A single learner asks questions about the bundled Spring Boot reference. The application prepares the reference for search, answers through a local assistant or an optionally configured hosted assistant, and identifies source documents associated with retrieved content. User-managed uploads, accounts, conversation history, and a graphical user interface are out of scope.

## Stories and Acceptance Criteria

### US-RAGSPR-01 — Make the included reference searchable (P1)

As a learner using RAGSpringAI, I want the included Spring Boot reference to be prepared for search when the application starts so that I can ask questions about it without manually importing it.

- **AC-01**: Given the reference has not been processed and required services are available, when the application starts, then its readable content is made searchable.
- **AC-02**: Given the reference has already been processed, when the application starts again, then existing indexed content is reused without duplicate ingestion.
- **AC-03**: Given reading or indexing cannot complete, when the application starts, then failure is surfaced and the reference is not reported as ready.

### US-RAGSPR-02 — Ask a question using the local assistant (P1)

As a learner, I want to ask a natural-language question about the included reference using the local assistant so that I can get an answer grounded in that material.

- **AC-04**: Given the reference is searchable, when I submit a question through the local assistant, then I receive an answer informed by relevant reference content.
- **AC-05**: Given the available content does not answer my question, when I submit it, then the assistant indicates that the answer is not available rather than presenting an unsupported answer.
- **AC-06**: Given the local assistant or search service is unavailable, when I submit a question, then the request is reported as failed rather than as a successful answer.

### US-RAGSPR-03 — Ask a question using the hosted assistant (P2)

As a learner, I want to ask a natural-language question using the hosted assistant so that I can use the alternative answer-generation option when it is configured and available.

- **AC-07**: Given the reference is searchable and the hosted assistant is configured, when I submit a question through it, then I receive an answer informed by relevant reference content.
- **AC-08**: Given the hosted assistant is unconfigured or unavailable, when I submit a question through it, then I receive a clear failure outcome rather than a successful-looking empty answer.

### US-RAGSPR-04 — Check the sources behind an answer (P2)

As a learner, I want to see the source documents associated with retrieved content so that I can check what material informed an answer.

- **AC-09**: Given retrieved passages have source-document metadata, when an answer is returned, then it identifies the associated source document name.
- **AC-10**: Given no source document is associated with retrieved passages, when an answer is returned, then it does not claim or imply source attribution.
