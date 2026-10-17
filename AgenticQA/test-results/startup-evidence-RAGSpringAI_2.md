# RAGSpringAI Startup Evidence — QA Run 2

**Date**: 2026-10-17

**Start command**: `cd RAGSpringAI && ./mvnw spring-boot:run`

**Profile**: Spring Boot `default`; local `application-default.properties` supplied the hosted-model configuration and is Git-ignored.

## First startup

Spring Boot started on port 8080 in 6.181 seconds. PostgreSQL/pgvector connected successfully, and ingestion logged:

```text
'spring-boot-reference.pdf' is already ingested, skipping
```

The root route returned HTTP 404 with Spring Boot's Whitelabel Error Page; the app exposes API routes, not a rendered UI. `GET /api/chat` returned HTTP 405 as expected for a POST-only route.

Using Playwright MCP in the browser, `POST /api/chat` with a plain-text question about Spring Boot returned HTTP 200 and a substantive answer with `Sources: spring-boot-reference.pdf`. The initial `page.request.post` attempt could not access the integrated browser's cookie store (`Storage.getCookies` protocol method unavailable); using same-origin `fetch` through Playwright's page evaluation worked. This was an MCP tool limitation, not an application error.

## Restart / index persistence

Before stopping the first app instance, PostgreSQL reported 400 rows for `spring-boot-reference.pdf` with ID fingerprint `0aff5e2bc01b7ead17e574b3d2d38dc3`. The application was stopped intentionally with `SIGTERM` to execute the restart scenario.

On the second launch, Spring Boot started on port 8080 in 8.202 seconds and again logged that the reference was already ingested and skipped. After restart, the source still had 400 rows and the same ID fingerprint. No vectors were inserted, changed, or removed during this check.
