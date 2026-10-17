import { expect, test } from '@playwright/test';

const baseURL =
  (process.env.RAGSPRINGAI_BASE_URL || 'http://localhost:8080').replace(/\/+$/, '');

test('AC-05 — local assistant explicitly abstains when the reference has no answer', async ({
  request,
}) => {
  // Trace: ../specs/test-plan-RAGSpringAI_2.md §3 S2.2;
  // ../../RAGSpringAI/specs/spec.md REQ-005.
  const question =
    'Using only the bundled Spring Boot reference, what is the home address of its author?';
  const response = await request.post(`${baseURL}/api/chat`, {
    data: question,
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    timeout: 120_000,
  });

  const answer = await response.text();
  expect(response.ok(), `POST /api/chat returned ${response.status()}: ${answer}`).toBeTruthy();
  expect(answer.trim().length).toBeGreaterThan(0);

  const normalizedAnswer = answer.toLowerCase().replace(/[’]/g, "'").replace(/\s+/g, ' ');
  const explicitlyAbstains =
    /\b(?:cannot|can't|unable to|do not|don't)\s+(?:answer|provide|determine|find|identify|verify|know|have)\b/.test(
      normalizedAnswer,
    ) ||
    /\b(?:not available|not found|not in (?:the )?(?:reference|document|provided material)|does not (?:contain|provide|mention|include)|doesn't (?:contain|provide|mention|include)|no (?:information|answer))\b/.test(
      normalizedAnswer,
    );
  expect(
    explicitlyAbstains,
    `Expected an explicit abstention, got: ${answer}`,
  ).toBeTruthy();
});
