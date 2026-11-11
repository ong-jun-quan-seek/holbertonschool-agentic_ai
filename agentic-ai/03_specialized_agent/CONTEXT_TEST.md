# 2. The Crash Test (Attention Saturation)

## The response obtained before clearing the context

Per TESTING_GUIDELINES.md, every it() or test() title must be in English and follow:

should_[EXPECTED_BEHAVIOR]_when_[CONDITION]

Example: should_return_zero_when_cart_is_empty

Related requirement in the same doc: use AAA in each test with mandatory comments // Arrange, // Act, and // Assert

## The response obtained after the reset

Per COMPANY STANDARD: UNIT TESTS (SKILL QA) in TESTING_GUIDELINES.md, every it() or test() name must follow this pattern (in English):

should_[EXPECTED_BEHAVIOR]_when_[CONDITION]

Example from the doc:

should_return_zero_when_cart_is_empty
So: expected behavior after should_, then when_, then the condition that drives that behavior. Names are snake_case segments separated by underscores.

The same file also requires AAA in the test body with // Arrange, // Act, and // Assert comments if you’re writing new tests—not part of naming, but part of the company test standard.

## Difference observed between two situations.

1. The response before clearing is short and concise without much elaboration and formatting.  
2. The response before clearing only gave example of the pattern for every it() and test() and doesn't explain it further. 
3. The response before clearing doesn't explain the AAA part as well, just a brief statement. 