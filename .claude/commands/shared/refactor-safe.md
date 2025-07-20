# Safe Refactoring Command

You will guide a safe, incremental refactoring process. The key principle: maintain working code at all times.

## Refactoring Process

### 1. Preparation Phase
- Ensure all tests pass before starting
- Commit current changes (clean working directory)
- Identify the refactoring goal clearly
- Plan small, reversible steps

### 2. Safety Checks
Before ANY refactoring:
- ✓ Tests exist and pass
- ✓ Code is committed
- ✓ Refactoring scope is clear
- ✓ Each step is small and atomic

### 3. Refactoring Catalog

#### Common Refactorings:
1. **Extract Method**: Pull code into a new method
2. **Rename**: Improve names for clarity
3. **Extract Variable**: Name complex expressions
4. **Inline**: Remove unnecessary indirection
5. **Move Method**: Relocate to more appropriate class
6. **Extract Interface**: Define contracts
7. **Replace Magic Numbers**: Use named constants
8. **Simplify Conditionals**: Make logic clearer

### 4. Step-by-Step Process

For EACH refactoring step:
1. **Identify**: What specific change to make
2. **Test**: Run tests before change
3. **Change**: Make ONE small change
4. **Test**: Run tests after change
5. **Commit**: Save progress with descriptive message

### 5. Refactoring Workflow

```
while (code needs improvement) {
    1. Pick smallest useful refactoring
    2. Apply refactoring
    3. Run tests
    4. If tests pass: commit
    5. If tests fail: revert
}
```

### 6. Red Flags - Stop If:
- Tests start failing
- Changes become too large
- Original functionality changes
- You're not sure what something does

### 7. Types of Refactoring Sessions

**Quick Win** (5-15 min):
- Rename variables/methods
- Extract obvious methods
- Remove dead code

**Focused** (30-60 min):
- Restructure a single class
- Eliminate duplication
- Simplify complex method

**Architectural** (Multiple sessions):
- Extract interfaces
- Introduce design patterns
- Restructure modules

## Getting Started

First, let's check:
1. What code needs refactoring?
2. What's the goal of this refactoring?
3. Do we have tests for this code?

Then we'll plan our approach and proceed step by step.