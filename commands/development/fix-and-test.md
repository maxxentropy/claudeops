# Fix and Test Command

Intelligently debug issues and ensure comprehensive test coverage using xUnit.

## Workflow:

1. **Analyze the Error**
   - Read error messages and stack traces carefully
   - Identify the root cause, not just symptoms
   - Check for related issues in surrounding code

2. **Search for Context**
   - Look for similar implementations in the codebase
   - Check for existing patterns that solve similar problems
   - Review documentation and comments

3. **Implement the Fix**
   - Apply the minimal change needed
   - Ensure the fix doesn't break existing functionality
   - Add proper error handling if missing
   - Include defensive programming where appropriate

4. **Generate/Update Tests (xUnit)**
   - Create unit tests using xUnit framework
   - Use Theory for parameterized tests
   - Test edge cases and error conditions
   - Ensure existing tests still pass
   - Add integration tests if needed

5. **Verify the Solution**
   - Run all related tests with `dotnet test`
   - Check for performance implications
   - Ensure no memory leaks or resource issues
   - Validate against requirements

6. **Document if Needed**
   - Add comments for complex logic
   - Update method documentation
   - Note any assumptions or limitations

## Common Patterns to Check:

### For .NET/C#:
- Null reference exceptions → Add null checks
- Async deadlocks → Use ConfigureAwait properly
- Collection modified → Use concurrent collections
- Resource leaks → Implement IDisposable

### For Mobile (MAUI/Prism):
- Navigation issues → Check INavigationAware implementation
- Binding failures → Verify property names and INotifyPropertyChanged
- Platform crashes → Add platform-specific exception handling
- Memory leaks → Weak references for event handlers

### For APIs:
- 500 errors → Add try-catch and proper error responses
- Validation failures → Implement proper model validation
- Auth issues → Check token handling and claims
- Performance → Add caching and optimize queries

## xUnit Test Generation Rules:

### Test Structure:
```csharp
public class ServiceNameTests
{
    private readonly ILogger<ServiceName> _logger;
    private readonly Mock<IDependency> _mockDependency;
    private readonly ServiceName _sut; // System Under Test
    
    public ServiceNameTests()
    {
        _logger = new NullLogger<ServiceName>();
        _mockDependency = new Mock<IDependency>();
        _sut = new ServiceName(_logger, _mockDependency.Object);
    }
    
    [Fact]
    public async Task MethodName_StateUnderTest_ExpectedBehavior()
    {
        // Arrange
        
        // Act
        
        // Assert
    }
    
    [Theory]
    [InlineData("value1", true)]
    [InlineData("value2", false)]
    public void MethodName_VariousInputs_ExpectedResults(string input, bool expected)
    {
        // Test implementation
    }
}
```

### xUnit Best Practices:
- Use `[Fact]` for single test cases
- Use `[Theory]` with `[InlineData]` for parameterized tests
- Use constructor for test setup (not [SetUp])
- Implement IDisposable for cleanup (not [TearDown])
- Use IClassFixture<T> for shared context
- Use ICollectionFixture<T> for shared context across classes

### Assertion Patterns:
```csharp
// Basic assertions
Assert.Equal(expected, actual);
Assert.NotNull(result);
Assert.True(condition);
Assert.Throws<ArgumentException>(() => method());
Assert.ThrowsAsync<InvalidOperationException>(async () => await methodAsync());

// Collection assertions
Assert.Empty(collection);
Assert.Contains(item, collection);
Assert.All(collection, item => Assert.True(item.IsValid));

// String assertions
Assert.StartsWith("prefix", actual);
Assert.Contains("substring", actual);
Assert.Matches("pattern", actual);
```

### Mock Setup (using Moq):
```csharp
// Setup mock behavior
_mockService.Setup(x => x.GetAsync(It.IsAny<int>()))
    .ReturnsAsync(new Result { Success = true });

// Verify interactions
_mockService.Verify(x => x.SaveAsync(It.IsAny<Entity>()), Times.Once);
```

### Test Organization:
- One test class per class being tested
- Group related tests using nested classes
- Use meaningful test names: `MethodName_Scenario_ExpectedOutcome`
- Keep tests independent and isolated
- Test both success and failure paths
- Use test data builders for complex objects