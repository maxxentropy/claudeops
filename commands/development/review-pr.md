# Pull Request Review Command

🎯 **COMMAND**: /review-pr | 📋 **WORKFLOW**: Workflow | 👤 **PERSONAS**: Default

You will perform a comprehensive code review of the current changes. Follow this systematic approach:

## Review Checklist

### 1. Code Quality
- **Readability**: Is the code easy to understand?
- **Naming**: Are variables, methods, and classes named clearly?
- **Complexity**: Can complex logic be simplified?
- **DRY**: Is there unnecessary duplication?
- **SOLID**: Does the code follow SOLID principles?

### 2. Functionality
- **Correctness**: Does the code do what it's supposed to?
- **Edge Cases**: Are edge cases handled properly?
- **Error Handling**: Are errors caught and handled appropriately?
- **Performance**: Are there any obvious performance issues?

### 3. Security
- **Input Validation**: Is user input validated and sanitized?
- **Authentication**: Are authentication checks in place?
- **Secrets**: Are there any hardcoded secrets or credentials?
- **SQL Injection**: Are database queries parameterized?
- **XSS**: Is output properly escaped?

### 4. Testing
- **Test Coverage**: Are new features/changes tested?
- **Test Quality**: Do tests actually test the behavior?
- **Test Names**: Are test names descriptive?
- **Edge Cases**: Are edge cases tested?

### 5. Architecture
- **Design Patterns**: Are appropriate patterns used?
- **Dependencies**: Are new dependencies justified?
- **Modularity**: Is the code properly modularized?
- **Coupling**: Is coupling minimized?

### 6. Documentation
- **Code Comments**: Is complex logic explained?
- **API Docs**: Are public APIs documented?
- **README**: Is README updated if needed?
- **Changelog**: Are breaking changes noted?

## Review Process

1. First run `git diff` to see all changes
2. Analyze each file systematically
3. Check for patterns across files
4. Run tests if available
5. Consider the bigger picture

## Output Format

Provide feedback in this structure:

### ✅ Strengths
- What's done well

### 🔍 Issues Found
- **Critical**: Must fix before merge
- **Major**: Should fix before merge  
- **Minor**: Consider fixing
- **Nitpick**: Optional improvements

### 💡 Suggestions
- Improvement ideas
- Alternative approaches
- Future considerations

### 📊 Summary
- Overall assessment
- Merge recommendation (Approve/Request Changes)

Start by examining the current changes with `git diff` or `git diff --cached`.