# Runtime Validation Report

**Generated**: 2026-10-17T12:09:34+07:00

**Target**: RAG PDF Assistant at `http://127.0.0.1:8501/`

**Story**: [RAG user stories](../../RAG/specs/spec.md)

**Plan**: [RAG PDF Assistant E2E test plan](../specs/rag-pdf-assistant.plan.md)

## Summary

| Step | Status | Exit Code | Details |
|------|--------|-----------|---------|
| Startup | PASS | n/a | Qdrant, FastAPI, Inngest, and Streamlit readiness endpoints returned HTTP 200. |
| Browser UI E2E | PASS | 0 | 6 checks passed across Chromium, Firefox, and WebKit (2 per browser). |
| Full RAG suite in Chromium | PASS | 0 | 3 checks passed, including synthetic PDF upload, persisted retrieval, answer, and source attribution. |
| Initial focused run | HEALED | 1 | 2 passed and 1 failed due to an ambiguous test locator; the test was corrected and rerun successfully. |

**Overall**: PASS WITH ISSUES

## Scope and Environment

- Scope: RAG-01 through RAG-09 in the test plan; user-facing upload, question, retrieval-count, source, and failure behaviors.
- Node.js: `v24.21.0`.
- Playwright: `1.64.1`; Chromium, Firefox, and WebKit were available. `playwright install chromium` completed successfully.
- Docker: available. The existing `qdrantRagDb` container responded on port 6333.
- Services: FastAPI on 8000, Streamlit on 8501, Inngest on 8288, and Qdrant on 6333 each returned HTTP 200 on their readiness probes.
- The RAG app has no authentication flow; authentication-failure testing is not applicable.
- RAG had no existing automated test assets. Existing `AgenticQA` tests for a separate Playwright documentation story were not changed.
- The synthetic end-to-end flow used the configured embedding and answer-generation services. Only synthetic text was sent; provider usage may incur charges. Secret values were not read or recorded.

## Test Commands and Results

1. Initial focused run: `cd AgenticQA && npx playwright test tests/rag --project=chromium --reporter=list`
   - Exit code: **1** — 2 passed, 1 failed.
   - Failure cause: the source assertion matched both the upload status and the source list item.
2. Healing rerun: `cd AgenticQA && npx playwright test tests/rag/rag-pdf-ingestion-answer.spec.ts --project=chromium --reporter=list --grep "uploads a synthetic PDF, retrieves its fact, and displays its source"`
   - Exit code: **0** — 1 passed.
   - Healing change: narrowed the assertion to the matching list item; application code was not modified.
3. Browser UI suite: `cd AgenticQA && npx playwright test tests/rag --grep-invert 'RAG-01/03/07' --reporter=list`
   - Exit code: **0** — 6 passed, 0 failed, 0 skipped across Chromium, Firefox, and WebKit.
4. Final Chromium suite: `cd AgenticQA && npx playwright test tests/rag --project=chromium --reporter=list`
   - Exit code: **0** — 3 passed, 0 failed, 0 skipped.

The Chromium end-to-end flow generated a small synthetic PDF with a unique fact, uploaded it through the UI, verified a matching point was persisted in Qdrant, asked the question in the UI, and verified both the returned fact and source filename. The test deletes only points matching its unique source name and removes its own uploaded file. A post-run check found zero remaining `rag-qa-*` vectors and no matching upload files.

## Acceptance-Criterion Coverage

| Scenario | Coverage | Result |
|----------|----------|--------|
| RAG-01 — Upload and index a readable PDF | Chromium end-to-end upload and Qdrant read-back | PASS |
| RAG-02 — Reject non-PDF or malformed PDFs | Not exercised | NOT RUN |
| RAG-03 — Answer from retrieved content | Chromium end-to-end answer contains the synthetic fact | PASS |
| RAG-04 — Decline an unanswerable question | Not exercised | NOT RUN |
| RAG-05 — Block empty and whitespace questions | Automated in Chromium, Firefox, and WebKit | PASS |
| RAG-06 — Retrieval-count default and bounds | Automated in Chromium, Firefox, and WebKit | PASS |
| RAG-07 — Show the source for an answer | Source list item verified for the answerable synthetic question; no-answer attribution not exercised | PARTIAL |
| RAG-08 — Actionable service-failure feedback | No controlled dependency outage was introduced | UNVERIFIED |
| RAG-09 — Duplicate PDF upload behavior | Not exercised | NOT RUN |

## Exploration and Healing

- A scenario-planning agent prepared the scenario matrix, and a separate test-healing agent fixed and reran the ambiguous source locator. Browser MCP tools were used for exploratory navigation; GitHub MCP confirmed that only `main` existed before the QA branch was created.
- Browser MCP exploration confirmed the upload control, question textbox, retrieval-count control (default 5), and Ask button.
- Empty-question submission produced no answer or error. Automated empty and whitespace-only checks passed.
- One early browser-MCP interaction before the local services were restarted showed `NoSessionContext:`. The later real Playwright upload-and-query flow succeeded with services running, so that observation is treated as inconclusive browser-tool evidence, not a confirmed application defect.
- No application code was changed. The one test failure was caused by the test locator and was healed with a narrowly scoped selector update.

## Issues Found

| # | Severity | Description | Evidence / Disposition |
|---|----------|-------------|------------------------|
| 1 | Medium | `anyio.Path.exists()` is called without `await` during PDF path handling; this emitted a `coroutine 'Path.exists' was never awaited` warning during ingestion and can prevent the intended relative-path fallback and missing-file check from executing. | [RAG/main.py](../../RAG/main.py#L35-L43). Reported only; production source was not changed under the QA workflow constraints. |

## Limitations and Sign-off

- Non-PDF/malformed-PDF handling, unanswerable questions, no-answer source suppression, controlled outage feedback, and duplicate-upload behavior remain unverified.
- There was no separate framework-native integration-test suite; Qdrant persistence was verified as part of the Playwright end-to-end scenario.
- No authentication-related cases apply to the current local application.
- The full happy path passed, but the unverified scenarios and the async path-check warning require follow-up before an unconditional PASS.

## Verdict

```text
environment:
  docker: AVAILABLE — `docker info` succeeded; qdrantRagDb responded on port 6333
  node: AVAILABLE — v24.21.0
  playwright: AVAILABLE — Playwright 1.64.1; Chromium, Firefox, WebKit available
  infra-tier: PRIMARY(Docker-based) — Qdrant ran in the existing Docker container
  browser-tier: PRIMARY(Playwright) — UI checks exercised all configured browser projects
startup: PASS — FastAPI, Streamlit, Inngest, and Qdrant readiness probes returned HTTP 200
integration: UNVERIFIED — exit_code: n/a; no separate framework-native integration command; Qdrant persistence was asserted in E2E
e2e: PARTIAL — exit_code: 0 final runs; 3 Chromium tests passed and 6 cross-browser UI checks passed; RAG-02, RAG-04, RAG-08, RAG-09 remain unverified
overall: NEEDS_SIGNOFF — primary upload/query/source flow passed; unverified scenarios and the async path-check warning remain
```
