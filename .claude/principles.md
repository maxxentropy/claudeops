# Reusable Principles for Slash Commands

This file contains tagged sections that slash commands reference.
DO NOT execute this file directly - it's used by other commands.

<!-- CORE_PRINCIPLES -->
## Core Development Principles
1. **NEVER TAKE SHORTCUTS**: Do it right or not at all. No assumptions, no "this should work"
2. **Do exactly what's asked**: Nothing more, nothing less
3. **Test everything**: No exceptions, even for "simple" changes
4. **Prefer editing over creating**: Never create files unless absolutely necessary

<!-- VERIFICATION_STEPS -->
## Verification Process
1. Run build: `dotnet build` / `npm run build`
2. Run tests: `dotnet test` / `npm test`
3. Check coverage (80% minimum)
4. Run linting: `dotnet format --verify-no-changes` / `npm run lint`
5. Manually verify each requirement works
6. If ANY step fails: STOP and fix before proceeding

<!-- COMMIT_FORMAT -->
## Commit Message Format
- Format: `<type>: <component> <what-and-why> [VERIFIED: build clean, 0 warnings, tests pass]`
- Types: feat, fix, refactor, docs, test, perf, chore
- Include context and consequences
- Be searchable for future investigation

<!-- LANG_STANDARDS -->
## Language Standards
- **C# (.NET)**: 4 spaces, Microsoft naming (PascalCase public, camelCase private, I-prefix interfaces)
- **TypeScript/JavaScript**: 2 spaces, camelCase
- **All languages**: async/await for I/O, SOLID principles, clean code

<!-- SECURITY_RULES -->
## Security Requirements
- **NEVER** commit secrets, keys, or tokens
- Use environment variables for sensitive config
- Always validate and sanitize input
- Use HTTPS in production
- Check for exposed credentials before ANY commit

<!-- TEST_STANDARDS -->
## Testing Standards
- Framework: xUnit (.NET), Jest/Vitest (JS)
- Coverage: 80% minimum
- Pattern: AAA (Arrange, Act, Assert)
- Naming: `MethodName_Scenario_ExpectedOutcome`
- Test edge cases and error paths

<!-- API_CHECK -->
## API Version Verification
1. Check docs: https://docs.anthropic.com/en/docs/claude-code/[topic]
2. Compare with last known version
3. If changed: Update tracking and rules BEFORE proceeding
4. Test with minimal example first

<!-- BUILD_PLATFORMS -->
## Platform Build Commands
**.NET**: `dotnet build && dotnet test && dotnet format`
**Node.js**: `npm install && npm test && npm run lint`
**Android**: `dotnet build -t:Run -f net8.0-android`
**iOS**: `dotnet build -t:Run -f net8.0-ios`
**Windows**: `dotnet build -t:Run -f net8.0-windows10.0.19041.0`

<!-- ERROR_PATTERN -->
## Error Handling Pattern
```csharp
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

<!-- MAUI_PRISM -->
## MAUI with Prism Standards
- NO MAUI Shell - use Prism navigation
- ViewModels inherit from BindableBase
- Implement INavigationAware
- Use DryIoc for DI
- Naming: ViewNamePage, ViewNamePageViewModel
- Platform code in Platforms/ folders