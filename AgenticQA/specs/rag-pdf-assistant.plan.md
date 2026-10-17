# RAG PDF Assistant E2E Test Plan

- **Source story**: [RAG user stories](../../RAG/specs/spec.md)
- **Target**: `http://127.0.0.1:8501/` (local Streamlit UI)
- **Browser coverage**: Playwright Chromium, Firefox, and WebKit; focused execution begins with Chromium.
- **Generated**: 2026-10-17

## Environment and exploration

- Qdrant, FastAPI, Inngest, and the Streamlit UI were started locally; their readiness endpoints returned HTTP 200.
- Docker was available and the existing `qdrantRagDb` container was running on port 6333.
- Browser MCP exploration found the upload and question forms, the retrieval-count control defaulting to 5, and the Ask button.
- Submitting an empty question did not produce a result or error.
- A first browser-MCP interaction before the local services were restarted showed `NoSessionContext:` after a question submission. A subsequent real Playwright upload-and-query flow succeeded with the services running, so this initial observation is treated as inconclusive browser-tool evidence rather than a confirmed application defect.
- A controlled outage was not exercised; user-facing failure handling under an unavailable dependency remains unverified.
- Gemini and Groq keys are configured, but their values were not inspected. The synthetic end-to-end flow used the configured embedding and answer-generation services and may incur provider charges.
- A single synthetic PDF ingestion and grounded-answer flow was exercised against the local services. Test data used a unique filename and was removed from Qdrant and local upload storage after the run.
- The RAG application has no authentication requirement; authentication-failure testing is not applicable.

## Test scenarios

### RAG-01 — Upload PDF and make its content searchable

- **Trace**: User Story 1, Acceptance Scenarios 1–2; REQ-001, REQ-002
- **Preconditions**: Application and ingestion/vector services available; a small synthetic PDF containing a unique fact.
**Steps**:
1. Open the RAG UI in a fresh browser context.
2. Select the synthetic PDF.
3. Wait for ingestion completion.
4. Ask about its unique fact.
- **Expected**: The file is accepted and processed, and a subsequent question can retrieve its content.
**Disposition**: PASS — A synthetic PDF was uploaded, indexed, and its unique fact was retrieved. Test vectors and the uploaded file were cleaned up.

### RAG-02 — Reject non-PDF and unreadable PDF files

- **Trace**: User Story 1, Acceptance Scenario 3; REQ-001, REQ-003
- **Preconditions**: Application and ingestion services available; synthetic non-PDF and malformed-PDF fixtures.
**Steps**:
1. Attempt to select a non-PDF file.
2. Select a malformed or empty PDF.
3. Observe the upload status.
- **Expected**: Non-PDF files are rejected; unreadable or empty PDFs report failure and are not marked processed.
**Disposition**: NOT RUN — This run used a valid synthetic PDF only; malformed and non-PDF upload outcomes remain unverified.

### RAG-03 — Answer a question from retrieved content

- **Trace**: User Story 2, Acceptance Scenario 1; REQ-004, REQ-005
- **Preconditions**: A known-answer PDF has been successfully ingested; retrieval and model services available.
**Steps**:
1. Ask a question whose answer is explicitly stated in the PDF.
2. Inspect the returned answer.
- **Expected**: The answer reflects the document evidence.
**Disposition**: PASS — The answerable question returned the unique fact from the synthetic PDF through the UI.

### RAG-04 — Decline an unanswerable question

- **Trace**: User Story 2, Acceptance Scenario 2; REQ-005
- **Preconditions**: A PDF is ingested and available; retrieval and model services available.
**Steps**:
1. Ask a question whose answer is absent from the collection.
2. Inspect the answer and source list.
- **Expected**: The assistant explicitly says it does not know and does not imply unsupported evidence.
**Disposition**: NOT RUN — An unanswerable question was not submitted; unknown-answer behavior remains unverified.

### RAG-05 — Prevent empty and whitespace-only questions

- **Trace**: User Story 2, Acceptance Scenario 4; REQ-009
- **Preconditions**: RAG UI loaded with no question entered.
**Steps**:
1. Submit the form with an empty question.
2. Enter whitespace only and submit again.
- **Expected**: Neither value is sent; no answer or success state appears, and the user remains able to enter a valid question.
**Disposition**: PASS — Manual exploration and automated empty/whitespace checks confirmed no answer or error is produced.

### RAG-06 — Enforce retrieval-count bounds and default

- **Trace**: User Story 2, Acceptance Scenario 3; REQ-006
- **Preconditions**: RAG UI loaded.
**Steps**:
1. Inspect the retrieval-count control's value and allowed minimum and maximum.
2. Try values at the lower and upper bounds and values outside them.
- **Expected**: The default is 5; allowed values are 1–20 inclusive.
**Disposition**: PASS — Automated checks confirmed default 5 and accepted values 1 and 20; no query is sent by this scenario.

### RAG-07 — Attribute answers to retrieved PDF sources only

- **Trace**: User Story 3, Acceptance Scenarios 1–2; REQ-007
- **Preconditions**: At least one answerable PDF is ingested and the query service is available.
**Steps**:
1. Ask an answerable question and inspect the source names.
2. Ask an unanswerable question and inspect whether unsupported source names appear.
- **Expected**: Sources match retrieved evidence; no source is presented when none was retrieved.
**Disposition**: PASS for answerable-source attribution — The automated flow confirmed the uploaded filename was shown with the retrieved answer. No-answer source behavior remains unverified.

### RAG-08 — Show actionable failures when a dependency is unavailable

- **Trace**: User Story 4, Acceptance Scenarios 1–3; REQ-008
- **Preconditions**: RAG UI loaded while Inngest is unavailable.
**Steps**:
1. Submit a non-empty question.
2. Observe the failure alert and whether the user can retry.
- **Expected**: The UI explains that the operation failed or was not confirmed, avoids success-shaped output, and provides a retry path.
**Disposition**: UNVERIFIED — A controlled service outage was not created. The earlier `NoSessionContext:` output was not reproduced in the successful real Playwright flow and is not treated as a confirmed app result.

### RAG-09 — Re-upload the same PDF

- **Trace**: User Story 1 edge case.
- **Preconditions**: A PDF was successfully ingested in the current session.
**Steps**:
1. Select the same PDF again.
2. Observe whether the UI describes reuse or reprocessing accurately.
- **Expected**: The UI does not imply a new independent copy was created unless it was.
**Disposition**: NOT RUN — Duplicate upload behavior was not exercised.

## Run policy and acceptance

- Use independent Playwright browser contexts and user-facing roles/labels for UI checks.
- Use only a synthetic PDF fixture; do not upload existing personal or business documents. Calls to the configured embedding and answer-generation services may incur provider charges.
- Keep backend-dependent scenarios visibly unverified when they have not been exercised; do not convert them into mocks.
- A PASS requires every in-scope acceptance criterion to be verified. Otherwise, report a qualified verdict and list the unresolved scenarios and requirements for sign-off.
