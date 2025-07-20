# Claude Command Reference

All slash commands are organized by category for easy discovery and use.

## Command Categories

### 🛡️ Core Commands (`/core`)
Essential commands for everyday development:
- `/commit` - Safe commit workflow with full verification
- `/fix` - Systematic debugging with minimal changes
- `/test` - Generate comprehensive tests (80% coverage)
- `/build` - Platform-specific build verification
- `/safe` - Universal safety wrapper for any task
- `/config` - Safe configuration changes with API checks

### 📋 Workflow Commands (`/workflow`)
Complex multi-step processes:
- `/prd` - Create comprehensive Product Requirements Document
- `/prdq` - Quick PRD for immediate implementation
- `/prd-decompose` - Break PRD into executable phases
- `/prd-implement` - Execute PRD phases with context

### 🔧 Development Commands (`/development`)
Programming-specific workflows:
- `/refactor-safe` - Incremental refactoring with verification
- `/review-pr` - Systematic pull request review
- `/tdd` - Test-driven development workflow
- `/pattern` - Implement standard code patterns
- `/git-investigate` - Analyze code history and evolution
- `/fix-and-test` - Legacy fix command with test generation

### 🏗️ Generation Commands (`/generation`)
Code and content generation:
- `/api-crud` - Generate complete REST APIs with tests
- `/mobile-scaffold` - Create MAUI apps with Prism framework
- `/create-docs` - Auto-generate comprehensive documentation
- `/context-prime` - Deep codebase understanding

## Command Structure

Each command follows this pattern:
1. **Personas** - Expert mindsets to embody
2. **Principles** - Core rules to follow (via INCLUDE tags)
3. **Workflow** - Step-by-step process
4. **Verification** - Mandatory checks before completion

## Usage

```bash
# Basic usage
claude /commit

# With parameters
claude /fix "login timeout issue"

# Wrapped in safety
claude /safe "refactor authentication module"
```

## Creating New Commands

See `/system/templates/newcmd.md` for the template and guidelines.

## Command Evolution

Commands in this directory use two styles:
- **Modern** (core/): Use personas and principles via INCLUDE tags
- **Legacy** (some in other directories): Self-contained instructions

We're gradually migrating all commands to the modern style for better maintainability.