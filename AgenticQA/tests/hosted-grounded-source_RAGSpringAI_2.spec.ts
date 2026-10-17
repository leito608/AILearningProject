import { expect, test } from '@playwright/test';

const baseURL =
  (process.env.RAGSPRINGAI_BASE_URL || 'http://localhost:8080').replace(/\/+$/, '');

test('AC-07 / AC-09 — hosted answer is grounded in the bundled reference and names its source', async ({
  request,
}) => {
  test.setTimeout(150_000);

  // Trace: ../specs/test-plan-RAGSpringAI_2.md §3 S3.1 and S4.1;
  // ../../RAGSpringAI/specs/spec.md REQ-006 and REQ-007.
  const question =
    'According to the Spring Boot reference, what does Spring Boot help users create?';
  const response = await request.post(`${baseURL}/api/chat_online`, {
    data: question,
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    timeout: 120_000,
  });

  const answer = await response.text();
  expect(
    response.ok(),
    `POST /api/chat_online returned ${response.status()}: ${answer}`,
  ).toBeTruthy();

  const normalizedAnswer = answer.toLowerCase().replace(/[^a-z0-9]/g, '');
  expect(normalizedAnswer).toContain('javaapplications');
  expect(answer.trim()).toMatch(/(?:^|\s)Sources:\s*spring-boot-reference\.pdf\s*$/i);
});
