# 🛡️ COMPANY STANDARD: UNIT TESTS (SKILL QA)

As a QA Agent, you must strictly apply this skill whenever generating tests.

## 1. Naming Convention
Each `it()` or `test()` block MUST follow this naming convention (in English):
`should_[EXPECTED_BEHAVIOR]_when_[CONDITION]`
Example: `should_return_zero_when_cart_is_empty`

## 2. The Arrange-Act-Assert (AAA) Pattern
The body of the test must be visually divided into 3 blocks using line breaks, with the following mandatory explanatory comments:
- `// Arrange`: Preparation of mocked variables and setup.
- `// Act`: A single call to the function being tested.
- `// Assert`: Verification of the result using `expect()`.