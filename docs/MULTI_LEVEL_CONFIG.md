# Multi-Level Claude Configuration

Claude Code supports a hierarchy of configurations, allowing you to have both system-wide defaults and project-specific overrides.

## Configuration Hierarchy

1. **System Level** (`~/.claude/CLAUDE.md`)
   - Your global defaults and preferences
   - General coding standards
   - Common commands and patterns
   - Applies to all projects

2. **Project Level** (`./CLAUDE.md` in project root)
   - Project-specific instructions
   - Overrides/extends system configuration
   - Tech stack specific patterns
   - Project conventions

## How It Works

When you run `cc` (or `claude`) in a directory:
1. Claude first loads the system-level configuration from `~/.claude/CLAUDE.md`
2. If a `CLAUDE.md` file exists in the current directory, it loads that too
3. Project-level instructions take precedence over system-level

## Setting Up

### System Level Setup
```bash
# Run the sync script to set up system config
cd ~/claudeops
bash sync.sh
```

This creates `~/.claude/CLAUDE.md` from your `CLAUDE-SYSTEM.md` file.

### Project Level Setup
```powershell
# Navigate to your project
cd C:\path\to\your\project

# Initialize project with Claude support
cc-init-project

# Edit the generated CLAUDE.md
notepad CLAUDE.md
```

## Example Use Cases

### System Level (CLAUDE-SYSTEM.md)
- General C# coding standards
- xUnit testing preferences
- Security guidelines
- Common build commands

### Project Level (Project's CLAUDE.md)
- This is a MAUI app using Prism
- Use DryIoc for dependency injection
- Follow this specific folder structure
- Run these specific test commands

## Benefits

1. **Consistency**: System config ensures consistent standards across all projects
2. **Flexibility**: Project configs handle project-specific needs
3. **Portability**: Project CLAUDE.md can be committed to git
4. **Team Collaboration**: Share project conventions with your team

## PowerShell Commands

- `cc` - Project-aware Claude launcher
- `cc-init-project` - Create a new project CLAUDE.md
- `ccsync` - Update system configuration

## Best Practices

1. Keep system config general and reusable
2. Put project-specific details in project CLAUDE.md
3. Commit project CLAUDE.md to version control
4. Update both configs as standards evolve

## Example Project CLAUDE.md

```markdown
# MyApp Claude Configuration

## Project Overview
Mobile app for tracking expenses using MAUI with Prism

## Tech Stack
- **Language**: C# .NET 8
- **Framework**: .NET MAUI with Prism.DryIoc.Maui
- **Database**: SQLite with Entity Framework Core
- **Testing**: xUnit with Moq

## Project Structure
project-root/
├── MyApp/                    # Main MAUI project
├── MyApp.Core/              # Shared business logic
├── MyApp.Tests/             # Unit tests
└── MyApp.UITests/           # UI tests

## Build Commands
dotnet build
dotnet test
dotnet build -t:Run -f net8.0-android
```