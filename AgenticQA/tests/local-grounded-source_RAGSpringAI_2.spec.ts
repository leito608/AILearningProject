import { expect, test } from '@playwright/test';

const baseURL =
  (process.env.RAGSPRINGAI_BASE_URL || 'http://localhost:8080').replace(/\/+$/, '');

test('AC-04 / AC-09 — local answer is grounded in the bundled reference and names its source', async ({
  request,
}) => {
  test.setTimeout(180_000);

  // Trace: ../specs/test-plan-RAGSpringAI_2.md §3 S2.1 and S4.1;
  // ../../RAGSpringAI/specs/spec.md REQ-004, REQ-005, and REQ-007.
  const question =
    'According to the bundled Spring Boot reference, what is Spring Boot?';
  const response = await request.post(`${baseURL}/api/chat`, {
    data: question,
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    timeout: 180_000,
  });

  const answer = await response.text();
  expect(response.ok(), `POST /api/chat returned ${response.status()}: ${answer}`).toBeTruthy();

  const normalizedAnswer = answer.toLowerCase().replace(/[^a-z0-9]/g, '');
  expect(normalizedAnswer).toContain('springbasedapplications');
  expect(answer.trim()).toMatch(/(?:^|\s)Sources:\s*spring-boot-reference\.pdf\s*$/i);
});
