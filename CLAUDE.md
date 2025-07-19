# Claude Code Configuration - Sean's Development Environment

## Development Standards

### Code Style
- **C# (.NET)**: Use 4 spaces for indentation
- **TypeScript/JavaScript**: Use 2 spaces for indentation
- **Follow Microsoft C# naming conventions**:
  - PascalCase for public members, types, and namespaces
  - camelCase for private fields and local variables
  - Prefix interfaces with 'I'
- **Async patterns**: Always use async/await for I/O operations
- **SOLID principles**: Apply in all object-oriented code

### Mobile Development (MAUI with Prism)
- Use Prism framework for MVVM and modular architecture
- NO MAUI Shell - use Prism navigation exclusively
- Implement dependency injection using DryIoc (Prism.DryIoc.Maui)
- Create Prism modules for feature separation
- ViewModels inherit from BindableBase and implement INavigationAware
- Use EventAggregator for module communication
- Platform-specific code in Platforms/ folders
- Follow Prism naming conventions (ViewNamePage, ViewNamePageViewModel)

### Backend Services
- RESTful API design with proper HTTP verbs
- Use DTOs for API contracts
- Implement repository pattern with interfaces
- Service layer for business logic
- Always include Swagger documentation
- Use FluentValidation for input validation

### Web Services
- Follow OpenAPI 3.0 specification
- Implement proper error handling with ProblemDetails
- Use middleware for cross-cutting concerns
- Enable CORS appropriately for development
- Implement rate limiting and caching where appropriate

## Build Commands

### .NET Projects
```bash
# Build
dotnet build

# Test
dotnet test --logger "console;verbosity=detailed"

# Run with hot reload
dotnet watch run
```

### Mobile Projects
```bash
# Android
dotnet build -t:Run -f net8.0-android

# iOS (Mac only)
dotnet build -t:Run -f net8.0-ios

# Windows
dotnet build -t:Run -f net8.0-windows10.0.19041.0
```

### Node.js Projects
```bash
# Install dependencies
npm install

# Development
npm run dev

# Build
npm run build

# Test
npm test
```

## Git Workflow

### Branch Naming
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes
- `refactor/*` - Code refactoring
- `chore/*` - Maintenance tasks

### Commit Style (Conventional Commits)
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or corrections
- `chore:` Maintenance tasks

### Pre-commit Checklist
1. Run all tests: `dotnet test` or `npm test`
2. Check code formatting
3. Ensure no sensitive data in commits
4. Update documentation if needed

## IDE Integration

### Visual Studio
- Use .editorconfig for consistent formatting
- Enable CodeLens for Git blame info
- Configure external tools:
  - Open Terminal Here
  - Claude Code Quick Launch
- Key bindings:
  - Ctrl+K, Ctrl+D: Format document
  - F12: Go to definition
  - Shift+F12: Find all references

### Rider
- Import code style from .editorconfig
- Enable 'Reformat Code on Save'
- Configure external tools for Claude Code
- Use Local History for safety
- Key bindings:
  - Ctrl+Alt+L: Reformat code
  - Ctrl+Shift+F: Find in path
  - Alt+Enter: Show intention actions

## Project-Specific Patterns

### Error Handling
```csharp
// Always use this pattern for service methods
public async Task<Result<T>> ExecuteAsync()
{
    try 
    {
        // Implementation
        return Result<T>.Success(data);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Error in {Method}", nameof(ExecuteAsync));
        return Result<T>.Failure(ex.Message);
    }
}
```

### API Endpoints
```csharp
// Standard CRUD pattern
[ApiController]
[Route("api/[controller]")]
public class EntitiesController : ControllerBase
{
    // GET: api/entities
    // GET: api/entities/{id}
    // POST: api/entities
    // PUT: api/entities/{id}
    // DELETE: api/entities/{id}
}
```

### Mobile ViewModels (Prism)
```csharp
// Always inherit from ViewModelBase (which inherits from BindableBase)
public class ItemPageViewModel : ViewModelBase, INavigationAware
{
    private string _title;
    public string Title
    {
        get => _title;
        set => SetProperty(ref _title, value);
    }
    
    public DelegateCommand LoadDataCommand { get; }
    
    public ItemPageViewModel(INavigationService navigationService, IApiService apiService) 
        : base(navigationService)
    {
        LoadDataCommand = new DelegateCommand(async () => await LoadDataAsync());
    }
    
    public void OnNavigatedTo(INavigationContext context)
    {
        // Handle navigation parameters
        if (context.Parameters.TryGetValue<int>("itemId", out var itemId))
        {
            // Load item
        }
    }
    
    public void OnNavigatedFrom(INavigationContext context) { }
}
```

## Performance Considerations

### General
- Profile before optimizing
- Use async/await properly (ConfigureAwait when appropriate)
- Implement caching strategically
- Use pagination for large datasets

### Mobile Specific
- Minimize UI thread work
- Use virtualized lists (CollectionView)
- Optimize images (resize, cache)
- Implement proper lifecycle management

### Backend Specific
- Use IMemoryCache for hot data
- Implement response compression
- Use bulk operations for database
- Consider using Dapper for read-heavy operations

## Security Guidelines

### Never Commit
- API keys or secrets
- Connection strings with passwords
- Personal access tokens
- Certificates or private keys

### Always Use
- Environment variables for configuration
- Azure Key Vault or similar for production
- HTTPS in production
- Input validation and sanitization

## Testing Strategy

### Unit Tests (xUnit)
- Use xUnit as the primary testing framework
- Aim for 80% code coverage
- Test public methods thoroughly
- Use Moq for mocking dependencies
- Use FluentAssertions for readable assertions
- Follow AAA pattern (Arrange, Act, Assert)

### xUnit Conventions
- Use `[Fact]` for single test cases
- Use `[Theory]` with `[InlineData]` for parameterized tests
- Constructor for setup, IDisposable for teardown
- Test naming: `MethodName_Scenario_ExpectedOutcome`

### Integration Tests
- Test API endpoints with WebApplicationFactory
- Use in-memory database or SQLite for tests
- Test critical user journeys
- Verify error handling
- Use IClassFixture for shared test context

## Monitoring and Logging

### Use Structured Logging
```csharp
_logger.LogInformation("Processing {OrderId} for {UserId}", orderId, userId);
```

### Log Levels
- **Trace**: Detailed diagnostic info
- **Debug**: Debugging information
- **Information**: General flow
- **Warning**: Abnormal but handled
- **Error**: Errors that need attention
- **Critical**: System failures

## Quick Commands

When I'm stuck or need quick help:
- "Review this code for best practices"
- "Generate unit tests for this class"
- "Optimize this query for performance"
- "Convert this to async/await pattern"
- "Implement proper error handling"

## Remember

1. **Think before coding**: Use 'think' for complex problems
2. **Clear context often**: Use /clear to reset when switching tasks
3. **Batch similar work**: Queue multiple related tasks
4. **Test everything**: Never skip tests, even for "simple" changes
5. **Document intent**: Code should be self-documenting, but complex logic needs comments