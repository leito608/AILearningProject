# QA End-to-End Workflow

Use this workflow to take a user story from requirements through browser exploration, automated Playwright tests, verified results, and a GitHub commit. Complete the stages in order, preserve traceability between artifacts, and do not claim a stage passed without evidence.

## Inputs

Provide:

- **User story:** A Markdown story with acceptance criteria, preferably in Given/When/Then form.
- **Application URL:** The environment to test (local, staging, or another explicitly supplied URL).
- **Scope or constraints:** Target browsers, test data, accounts, excluded flows, and any safety or environment restrictions.

If a required input is missing, inspect the repository for relevant context. Ask for clarification only when a safe, meaningful test cannot be designed without it. Never invent credentials, application behavior, or successful test results.

## End-to-End Workflow Covered

```text
User Story
    ↓
AI Test Plan Generation
    ↓
Exploratory Testing via MCP
    ↓
Automation Script Generation
    ↓
Test Execution & Healing
    ↓
AI Generated Test Report
    ↓
Commit Everything to GitHub
```

## 1. User Story

Read the supplied story and identify:

- User goal, actors, preconditions, and starting state.
- Each acceptance criterion and its observable expected result.
- Required test data, permissions, environment, and browser coverage.
- Ambiguities, dependencies, and risks that may block testing.

Keep the story as the source of truth. Do not silently change requirements to fit the application.

**Output:** The original or clarified story, retained in `user-stories/` when it is part of this repository's test assets.

**Gate:** Every acceptance criterion is testable, or any unresolved blocker is explicitly recorded before proceeding.

## 2. AI Test Plan Generation

Create a plan mapped directly to the story's acceptance criteria. Include:

- A scenario ID, title, and linked acceptance criterion for each scenario.
- Preconditions and independent starting state.
- Numbered user actions and observable expected results.
- Happy paths, validation and error paths, boundaries, and relevant accessibility checks.
- Test data requirements, cleanup needs, browser coverage, and assumptions.
- A clear pass/fail condition for each scenario.

Keep scenarios focused and independently runnable. Prioritize user-visible behavior and avoid asserting implementation details.

**Output:** A Markdown test plan in `specs/`, with story and criterion references.

**Gate:** Every acceptance criterion has at least one scenario; important negative and boundary behavior is included when applicable.

## 3. Exploratory Testing via MCP

Use the available Playwright MCP browser tools to visit the supplied application and manually exercise the planned journeys before automating them.

1. Set up the browser for the target application and environment.
2. Inspect the rendered page and available navigation, controls, and accessible names.
3. Execute each planned scenario using user-like interactions.
4. Compare actual behavior with the story and plan; record observed results, URLs, relevant console/network errors, and reproducible defects.
5. Update the plan only when exploration provides evidence of a requirement or application detail; preserve the original acceptance-criterion traceability.

Do not submit destructive, irreversible, or externally visible actions unless explicitly authorized. Use only approved test accounts and data. Do not expose credentials or sensitive response data in artifacts.

**Output:** Exploration evidence and any plan updates, recorded with the test plan or in the final report.

**Gate:** Each planned flow has been explored, or the reason it could not be explored is recorded. Do not represent an inaccessible or blocked flow as tested.

## 4. Automation Script Generation

Generate Playwright tests from the approved plan and exploration evidence.

- Follow the repository's Playwright configuration, conventions, and test locations.
- Use one test per scenario where practical; use descriptive suite and test names that map back to scenario IDs.
- Prefer accessible, user-facing locators such as roles, labels, and names; avoid brittle positional selectors and arbitrary sleeps.
- Assert meaningful outcomes, not just that an action completed.
- Keep scenarios isolated and repeatable; arrange required setup and cleanup explicitly.
- Reuse suitable fixtures and helpers already in the repository; do not add dependencies without need.
- Add traceability to the source story and plan in the test file or test metadata.

**Output:** Playwright test files in the repository's configured test directory (currently `tests/`).

**Gate:** Every in-scope planned scenario has an automated test, or an explicit reason and manual-test disposition is recorded.

## 5. Test Execution & Healing

Run the generated tests using the repository's configured Playwright projects and environment.

1. Run the focused tests first; run the broader relevant suite after focused tests pass.
2. Save the command, environment, browser/project, and actual pass/fail/skip counts.
3. For failures, inspect the error, trace, page state, console, and network evidence where available.
4. Identify whether the cause is a test defect, application defect, environment issue, or flaky behavior.
5. Make the smallest evidence-based fix. Do not weaken or remove a valid assertion merely to obtain a pass.
6. Rerun the affected test after each fix and rerun the relevant suite after healing.
7. If a failure cannot be fixed safely or reliably, leave it visible and document its cause and status; do not mark it as passing or hide it with a skip.

**Output:** Final test results and any minimal test fixes, with unresolved failures clearly identified.

**Gate:** The final result is reproducible and accurately reported. Any remaining failures, skipped tests, unavailable browsers, or environment limitations are disclosed.

## 6. AI-Generated Test Report

Produce a concise Markdown report (for example, `test-results/qa-e2e-report.md`) containing:

- Story and plan references, application environment, and execution date.
- Scope, browsers/projects, and commands executed.
- Scenario and acceptance-criterion coverage.
- Results with passed, failed, skipped, and blocked counts.
- Defects and unresolved issues, with evidence and reproduction steps where available.
- Healing changes made and the verification rerun performed.
- Limitations, risks, and an overall verdict: **PASS**, **PASS WITH ISSUES**, or **FAIL**.

Base the verdict on the recorded evidence. A report is not a substitute for running the tests.

**Gate:** Counts reconcile with runner output, each acceptance criterion has a stated disposition, and limitations are explicit.

## 7. Commit Everything to GitHub

After the report and required verification are complete:

1. Inspect the current branch, `git status`, and diff. Preserve unrelated user changes.
2. Stage only the story, plan, exploration artifacts, tests, report, and other files created or intentionally changed by this workflow. Do not use a blanket add that could include unrelated or sensitive files.
3. Check the staged diff for secrets, credentials, generated noise, and accidental changes.
4. Commit the complete QA workflow deliverables with a descriptive message that references the story or feature.
5. Push the commit to the appropriate GitHub branch only when the repository remote and available permissions support it. Never place tokens or credentials in files, commands, logs, or the report.
6. Report the commit hash and push status. If a commit or push cannot be completed, explain the blocker and leave the verified work intact.

Do not commit unrelated work or claim a GitHub push succeeded unless it is confirmed.

## Completion Checklist

- [ ] Story requirements and acceptance criteria are understood.
- [ ] Test plan covers and traces every in-scope criterion.
- [ ] MCP exploration evidence and deviations are recorded.
- [ ] Automated tests are generated from the plan and observed application.
- [ ] Tests have been executed; failures and healing are transparently reported.
- [ ] AI-generated report matches actual runner evidence.
- [ ] Only intended workflow files are committed; GitHub push status is confirmed or its blocker is stated.