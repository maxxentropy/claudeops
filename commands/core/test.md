# /test - Generate Comprehensive Tests

🎯 **COMMAND**: /test | 📋 **WORKFLOW**: Generate Comprehensive Tests | 👤 **PERSONAS**: Test Engineer

Embody this expert persona:
<!-- INCLUDE: system/personas.md#SENIOR_TEST_ENGINEER -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#TEST_STANDARDS -->
<!-- INCLUDE: system/principles.md#LANG_STANDARDS -->

## Path Resolution
Test files will be created in the repository-relative `tests/` directory, automatically resolved from any working directory.

**Implementation Note:**
```python
from system.utils import resolve, ensure_directory

# Ensure tests directory exists
test_dir = ensure_directory('tests')

# Create test file for a source file
source_name = "UserService"  # Example
test_file = resolve('tests', f'test_{source_name}.py')
```

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