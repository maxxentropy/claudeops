# Test-Driven Development (TDD) Workflow

You will guide the user through a Test-Driven Development process. Follow the RED-GREEN-REFACTOR cycle strictly.

## TDD Process:

### 1. RED Phase - Write a Failing Test
- Ask the user what feature or behavior they want to implement
- Write the simplest test that captures the desired behavior
- Use the project's testing framework (default to xUnit for .NET)
- Ensure the test fails for the right reason
- The test should be:
  - Focused on one behavior
  - Clear in its intent
  - Independent of other tests

### 2. GREEN Phase - Make the Test Pass
- Write the MINIMUM code necessary to make the test pass
- Don't worry about elegance or optimization yet
- Resist the urge to write more than needed
- Run the test to confirm it passes

### 3. REFACTOR Phase - Improve the Code
- Now that the test passes, improve the code quality
- Look for opportunities to:
  - Remove duplication
  - Improve naming
  - Simplify logic
  - Apply SOLID principles
- Run tests after each change to ensure nothing breaks

### 4. Repeat
- Move to the next test
- Each cycle should be small (5-10 minutes)
- Build functionality incrementally

## Guidelines:
- Never write production code without a failing test
- Tests should be written from the perspective of the code's user
- Keep tests and production code separate
- One assertion per test when possible
- Use descriptive test names that explain the scenario

## Example Test Structure (xUnit):
```csharp
[Fact]
public void MethodName_Scenario_ExpectedBehavior()
{
    // Arrange
    var sut = new SystemUnderTest();
    
    // Act
    var result = sut.MethodName();
    
    // Assert
    Assert.Equal(expected, result);
}
```

Start by asking: "What behavior or feature would you like to implement using TDD?"