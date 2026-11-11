# 0. Forge the "QA Engineer Strict" Agent (output)

Here’s a concise summary from MEMORY.md (and how it fits with the workspace rules):

Project: Agentic E-Commerce
Stack: Node.js, vanilla JavaScript, Jest for tests — no TypeScript in this microservice.

Architecture note: The app generally uses cents, but cart_calculator.js is legacy and returns euros with two decimal places. That mismatch is known technical debt.

Your role (QA): I act as a Senior QA Engineer. I must not change anything under /src while building tests. Work is tests only.

Priority: Add a solid unit test suite for the cart calculator before any migration or refactor of that logic.

Test standards (TESTING_GUIDELINES.md): Names like should_[EXPECTED_BEHAVIOR]_when_[CONDITION], and each test uses Arrange / Act / Assert with those comment labels.

In short: Jest tests for the legacy cart calculator, without touching source, with strict naming and AAA structure, as a gate before migration.