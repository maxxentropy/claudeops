# Claude Code System Configuration - Sean's Global Defaults

# CRITICAL COMPLETION CRITERIA
**NEVER claim a task is done unless ALL are verified:**

1. **NEVER TAKE SHORTCUTS**: Every step must be executed fully. If tempted to skip tests, skip verification, use a hacky solution, or say "this should work" without proving it - STOP. Do it right or not at all. No assumptions, no partial implementations, no "we can fix it later"
2. **Full Request Satisfaction**: Every requirement implemented completely
3. **Zero Compilation Errors**: Build command succeeds without errors
4. **Zero Warnings**: No linter/compiler warnings
5. **Meaningful Test Coverage**: Tests verify happy path, edge cases, and error handling. Critical paths must be tested.
6. **CHECKPOINT COMMIT RULE**: The moment ALL above criteria pass, commit immediately. No additional changes before this commit. This is your safety net. Follow standard format: `<type>: <component> <what-and-why> [VERIFIED: build clean, 0 warnings, X% coverage]`

## Verification Process (MANDATORY)
1. Run build: `dotnet build` / `npm run build`
2. Run tests: `dotnet test` / `npm test`
3. Run coverage analysis
4. Run linting: `dotnet format` / `npm run lint`
5. Manually verify each requirement
6. **COMMIT IMMEDIATELY**: Once all checks pass, commit before ANY other changes. This checkpoint is sacred.

# Core Principles
- Do exactly what's asked; nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files
- Think before coding on complex problems
- Test everything - no exceptions
- Document complex logic only
- **Smart git investigation**: For bugs, check last 3 commits (30s). For refactors, check full history (2min). Skip for new features.
- **Write searchable commit messages**: Include context, reasons, and keywords for future investigation

## Development Standards

### Code Style
- **C# (.NET)**: 4 spaces, Microsoft naming conventions
- **TypeScript/JavaScript**: 2 spaces
- **All languages**: SOLID principles, async/await for I/O

### Testing
- **Framework**: xUnit (.NET) as primary
- **Coverage**: 80% minimum
- **Pattern**: AAA (Arrange, Act, Assert)
- **Naming**: `MethodName_Scenario_ExpectedOutcome`

### Git & Security
- **Searchable commits**: `<type>: <component> <what-and-why>`
  - Types: feat:, fix:, refactor:, docs:, test:, perf:, chore:
  - Include: Problem, solution, consequences, references
  - Examples:
    - `fix: UserService auth failing for OAuth - added retry logic`
    - `refactor: OrderService extract payment logic - reduces coupling [VERIFIED: build clean, 0 warnings, 92% coverage]`
    - `feat: Add email notifications - implements issue #123 [VERIFIED: build clean, 0 warnings, 85% coverage]`
- Run tests before committing
- NEVER commit secrets/keys - use environment variables
- Always validate input, use HTTPS in production

### Performance
- Profile before optimizing
- Use async/await properly
- Implement strategic caching
- Paginate large datasets

## Common Commands
```bash
# .NET
dotnet build && dotnet test && dotnet format

# Node.js  
npm install && npm test && npm run lint
```

## Quick Commands
- "Review this code for best practices"
- "Generate unit tests with 80% coverage"
- "Fix all warnings and errors"