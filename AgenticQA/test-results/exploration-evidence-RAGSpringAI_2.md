# RAGSpringAI Exploratory Evidence — QA Run 2

**Date**: 2026-10-17

**Target**: `http://localhost:8080`

**Story**: [user-story-RAGSpringAI_2.md](../user-stories/user-story-RAGSpringAI_2.md)

**Plan**: [test-plan-RAGSpringAI_2.md](../specs/test-plan-RAGSpringAI_2.md)

## API surface and observations

The application is a REST API, not a rendered web application.

| Probe | Observed outcome | Interpretation |
|---|---|---|
| Open `GET /` in the integrated Playwright browser | Spring Boot Whitelabel Error Page, HTTP 404 | No root page or browser UI is defined. |
| `GET /api/chat` | HTTP 405 | Endpoint is present and requires POST. |
| Playwright MCP same-origin `fetch` to `POST /api/chat` with `text/plain` question “Based only on the Spring Boot reference document, what is Spring Boot?” | HTTP 200; non-empty answer and `Sources: spring-boot-reference.pdf` | Local chat endpoint, retrieval, answer generation, and source-name attribution worked for this observed request. The response referred to Chapter 3.1 and Chapter 1.4 of the context. |
| Integrated MCP `page.request.post` for the same local API | Browser-protocol error: `Storage.getCookies` method unavailable | The integrated browser's API request helper could not initialize; same-origin fetch through Playwright page evaluation was used instead. |

No browser UI interactions or accessibility checks apply. The Playwright MCP exploration was limited to confirming the API-only surface and one user-like local question; automated API acceptance tests are reported separately.
