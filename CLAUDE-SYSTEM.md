# Claude Code System Configuration - Sean's Global Defaults

## Development Standards (Global)

### Code Style
- **C# (.NET)**: Use 4 spaces for indentation
- **TypeScript/JavaScript**: Use 2 spaces for indentation
- **Follow Microsoft C# naming conventions**
- **Async patterns**: Always use async/await for I/O operations
- **SOLID principles**: Apply in all object-oriented code

### Testing Strategy (All Projects)
- Use xUnit as the primary testing framework
- Aim for 80% code coverage
- Follow AAA pattern (Arrange, Act, Assert)
- Test naming: `MethodName_Scenario_ExpectedOutcome`

### Git Workflow (Global)
- Conventional commits (feat:, fix:, docs:, etc.)
- Never commit sensitive data
- Always run tests before committing

### Security Guidelines (Global)
- Never commit API keys or secrets
- Use environment variables for configuration
- Always validate and sanitize input
- Use HTTPS in production

### Performance (Global)
- Profile before optimizing
- Use async/await properly
- Implement caching strategically
- Use pagination for large datasets

## Common Commands

### Build Commands
```bash
# .NET
dotnet build
dotnet test
dotnet watch run

# Node.js
npm install
npm run dev
npm test
```

## Quick Commands (Available Everywhere)
- "Review this code for best practices"
- "Generate unit tests for this class"
- "Optimize this query for performance"
- "Convert this to async/await pattern"
- "Implement proper error handling"

## Remember (Global Rules)
1. **Think before coding**: Use 'think' for complex problems
2. **Test everything**: Never skip tests
3. **Document intent**: Complex logic needs comments
4. **Follow project conventions**: Check existing code first

# Important Reminders
- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files
- NEVER proactively create documentation files unless requested