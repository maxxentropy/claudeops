# Git History Investigation Command

You are about to investigate the git history of a file or codebase to understand:
- Why code was written this way
- What problems it was solving
- What approaches were already tried
- Who made changes and when

## Investigation Steps

1. **Start with file history**:
   ```bash
   git log --oneline <filename>
   git log -p -10 <filename>
   ```

2. **Search for related changes**:
   ```bash
   git log --grep="<search-term>" --all
   git log -S "<code-snippet>" -p
   ```

3. **Understand specific lines**:
   ```bash
   git blame <filename>
   git show <commit-hash>
   ```

4. **Check recent context**:
   ```bash
   git log --since="2 weeks ago" --graph
   git shortlog -sn --since="1 month ago"
   ```

## What to Look For

1. **Patterns in commit messages**:
   - Previous bug fixes
   - Refactoring attempts
   - Performance improvements
   - Security patches

2. **Code evolution**:
   - How the implementation changed over time
   - Why certain approaches were abandoned
   - Dependencies that were added/removed

3. **Related issues**:
   - Issue numbers in commits
   - Links to PRs or discussions
   - TODO/FIXME comments in history

## Report Your Findings

After investigation, provide:
1. Summary of relevant history
2. Previous approaches that didn't work
3. Current implementation reasoning
4. Recommendations based on history

Start by asking what file or component the user wants to investigate.