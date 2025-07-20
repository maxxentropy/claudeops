# /test - Generate Comprehensive Tests

Embody this expert persona:
<!-- INCLUDE: system/personas.md#SENIOR_TEST_ENGINEER -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#TEST_STANDARDS -->
<!-- INCLUDE: system/principles.md#LANG_STANDARDS -->

Generate comprehensive tests for the specified target:

1. **Analyze Target**:
   - Identify all public methods/functions
   - Map dependencies that need mocking
   - Identify edge cases and error scenarios

2. **Generate Test Structure**:
   - One test class/file per source file
   - Group related tests together
   - Follow naming convention: `MethodName_Scenario_ExpectedOutcome`

3. **Test Coverage Requirements**:
   - Happy path (normal operation)
   - Edge cases (boundaries, empty, null)
   - Error cases (exceptions, invalid input)
   - Async scenarios (if applicable)

4. **Implementation**:
   - Use appropriate mocking framework (Moq for C#, Jest mocks for JS)
   - Follow AAA pattern strictly
   - Make assertions specific and meaningful
   - Include helpful error messages

5. **Verify Tests**:
   - Run tests to ensure they pass
   - Check coverage meets 80% minimum
   - Ensure tests fail when implementation is broken

Example usage: `/test UserService` or `/test calculateTotal function`