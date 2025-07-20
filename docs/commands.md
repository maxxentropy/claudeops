# Slash Commands Reference

All commands use tagged principles from `principles.md` to ensure consistency.

## Core Development Commands

### `/safe [task description]`
General-purpose wrapper that applies ALL safety protocols to any task.
Use this when you want maximum verification and safety checks.
Example: `/safe implement user authentication`

### `/commit`
Execute full verification workflow before committing with proper format.
Includes: build, test, lint, security checks, proper commit message.

### `/fix [issue description]`
Systematic debugging with investigation, minimal changes, and full verification.
Example: `/fix build error in UserService`

### `/config [type]`
Configuration changes with mandatory API version checking.
Types: settings, hooks, mcp
Example: `/config hooks for test automation`

## Specialized Commands

### `/test [target]`
Generate comprehensive unit tests with 80% coverage minimum.
Example: `/test UserService` or `/test calculateTotal function`

### `/build [platform]`
Platform-specific build commands with pre/post checks.
Platforms: dotnet, node, android, ios, windows
Example: `/build android`

### `/pattern [type]`
Implement standard code patterns correctly.
Types: error-handling, repository, service, logging, validation, api-response
Example: `/pattern repository for User entity`

## Planning Commands

### `/prdq [feature description]`
Quick requirements doc for immediate work between you and Claude.
Output: 1-page actionable requirements.
Example: `/prdq implement Azure MCP server tools`

### `/prd [feature description]`
Formal PRD for team planning and stakeholder review.
Output: Comprehensive multi-section document.
Example: `/prd multi-factor authentication system`

### `/prd-decompose [prd name or content]`
Break down a PRD into manageable phases with dependency tracking.
Output: Phased implementation plan with context preservation.
Example: `/prd-decompose continuous-improvement-prd.md`

### `/prd-implement [project] [phase]`
Execute a specific PRD phase with full context from previous phases.
Loads all artifacts and ensures continuity across implementation.
Example: `/prd-implement continuous-improvement phase-3`

## Meta Commands

### `/newcmd [command purpose]`
Create a new slash command that embeds workflows to solve discipline problems.
Reads the slash command rationale and ensures new commands follow best practices.
Example: `/newcmd create API client with automatic validation`

## Command Guidelines

1. **No Duplication**: Each command has a specific purpose
2. **Composable**: Can be used in sequence (e.g., `/prdq` then `/safe`)
3. **Tagged Principles**: All commands reference `principles.md` for consistency
4. **Explicit Workflows**: Commands contain complete steps, not just reminders

## Most Common Workflows

1. **Feature Development**: `/prdq` → `/safe implement`
2. **Bug Fixing**: `/fix` 
3. **Adding Tests**: `/test` → `/commit`
4. **Configuration**: `/config` type

Note: All commands automatically include relevant principles like "NEVER TAKE SHORTCUTS" and language standards from the central principles file.