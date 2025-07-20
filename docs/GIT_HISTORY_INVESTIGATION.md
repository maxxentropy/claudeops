# Git History Investigation Process

## Why Check Git History Before Fixing?

When fixing bugs or modifying existing code, the git history contains crucial context:
- **Why** the code was written this way
- **What problems** it was solving
- **What approaches** were already tried
- **Who** made changes and can provide context
- **When** changes were made (helps identify related issues)

## The Investigation Process

### 1. Initial File History Check
```bash
# See all commits that touched a specific file
git log --oneline <filename>

# Example:
git log --oneline src/Services/UserService.cs
```

### 2. Detailed Change Investigation
```bash
# See actual code changes with commit messages
git log -p <filename>

# Limit to recent changes
git log -p -5 <filename>

# Search for specific changes
git log -p -S "searchterm" <filename>
```

### 3. Understanding Specific Changes
```bash
# Examine a specific commit
git show <commit-hash>

# See who changed what and when
git blame <filename>

# Find commits by message content
git log --grep="bugfix" --grep="user service" --all-match
```

### 4. Context Gathering Commands
```bash
# See changes in date range
git log --since="2024-01-01" --until="2024-02-01" -p <filename>

# Find when a bug was introduced
git bisect start
git bisect bad  # Current version is bad
git bisect good <commit>  # Known good commit

# See branch history
git log --graph --oneline --all
```

## Writing Searchable Commit Messages

### Structure
```
<type>: <subject>

<body>

<footer>
```

### Examples of Good Searchable Commits

```
fix: UserService authentication failing for OAuth users

- Root cause: Token expiration not handled in refresh flow
- Added retry logic with exponential backoff
- Previous approach (simple retry) caused rate limiting

Fixes #1234
Related to #1230 (OAuth implementation)
```

```
refactor: Extract email validation to shared utility

- Moved from UserService and AdminService to EmailValidator
- Consolidated 3 different regex patterns into one
- Performance: 50ms -> 5ms for bulk validation

Breaking: EmailHelper.Validate() signature changed
Migration: Replace EmailHelper.Validate(email) with EmailValidator.IsValid(email)
```

### Key Elements for Searchability

1. **Type Prefix** (fix:, feat:, refactor:, docs:, test:)
2. **Component/Area** (UserService, API, Database)
3. **Problem Statement** (what was broken)
4. **Solution Approach** (what was done)
5. **Consequences** (breaking changes, performance impact)
6. **References** (issue numbers, related commits)

### Search-Friendly Patterns

```bash
# Find all authentication-related fixes
git log --grep="^fix:.*auth"

# Find performance improvements
git log --grep="performance\|optimization\|faster"

# Find breaking changes
git log --grep="BREAKING\|Breaking:"

# Find changes by specific developer
git log --author="Sean" --grep="UserService"
```

## Practical Workflow

### Before Making Changes:
1. **Identify the file(s)** you need to modify
2. **Run**: `git log -p -10 <filename>`
3. **Look for**:
   - Recent changes that might conflict
   - Previous attempts to fix similar issues
   - TODOs or FIXMEs in commit messages
   - Related issue numbers

### While Making Changes:
1. **Reference findings** in your approach
2. **Avoid repeating** failed approaches
3. **Build upon** existing patterns

### When Committing:
1. **Include context** from your investigation
2. **Reference** related commits: "Builds on a1b2c3d"
3. **Explain why** not just what
4. **Add keywords** future developers might search

## Example Investigation Session

```bash
# 1. I need to fix a login timeout issue
$ git log --oneline --grep="login\|timeout" -10

# 2. Found related commit: a1b2c3d "fix: Increase login timeout to 30s"
$ git show a1b2c3d

# 3. Check what else changed in the auth flow
$ git log -p src/Auth/ --since="3 months ago"

# 4. See who's been working on this
$ git shortlog -sn --grep="auth" --since="6 months ago"

# 5. Understand the current state
$ git blame src/Auth/LoginController.cs | grep -i timeout
```

## Tips for Effective History Usage

1. **Use aliases** for common commands:
   ```bash
   git config --global alias.history 'log -p --follow'
   git config --global alias.search 'log --all --grep'
   ```

2. **Combine with grep** for powerful searching:
   ```bash
   git log -p | grep -B5 -A5 "timeout"
   ```

3. **Use GUI tools** when appropriate:
   - `gitk <filename>` - Visual history
   - `git gui blame <filename>` - Interactive blame

4. **Document your investigation** in PR descriptions:
   ```markdown
   ## Investigation
   - Checked history: Found 3 previous attempts (a1b2c3d, d4e5f6g, h7i8j9k)
   - Previous approach X failed because Y
   - This PR tries approach Z instead
   ```

## Benefits of This Approach

1. **Avoid repeating mistakes**
2. **Understand the full context**
3. **Build better solutions**
4. **Create better documentation**
5. **Faster onboarding** for new team members
6. **Easier debugging** in the future

Remember: The git history is your team's collective memory. Use it wisely and contribute to it thoughtfully.