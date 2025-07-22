# Implementation Summary: Consistent Slash Command Paths

## Executive Summary
This implementation plan addresses the issue of slash commands saving files relative to the current working directory, which causes outputs to be scattered across the filesystem. The solution implements repository-aware path resolution to ensure all command outputs go to consistent locations within the repository root.

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Slash Command  │────▶│  Hook Pipeline   │────▶│  Path Resolver  │
│   (/prd, etc)   │     │  (Detects Root)  │     │  (Resolves Path)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │                           │
                                ▼                           ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │  Repo Detector   │     │ Consistent Path │
                        │  (Finds .git)    │     │ (repo/docs/...) │
                        └──────────────────┘     └─────────────────┘
```

## Implementation Phases

### Phase 1: Repository Root Detection (1-2 hours)
- **Core Component**: `system/utils/repo_detector.py`
- **Features**: Git detection, caching, environment override
- **Key Decision**: Use `.git` directory as primary indicator
- **Edge Cases**: Submodules, symlinks, bare repos

### Phase 2: Path Resolution Service (1 hour)
- **Core Component**: `system/utils/path_resolver.py`
- **Features**: Template variables, path normalization
- **Key Decision**: Use `${REPO_ROOT}` as primary variable
- **Fallback**: Current directory when not in repository

### Phase 3: Hook Infrastructure (1.5 hours)
- **Updates**: `combined_hook.sh`, new context injector
- **Features**: Environment variable injection
- **Key Decision**: Use environment variables for compatibility
- **Context**: `CLAUDE_REPO_ROOT`, `CLAUDE_CWD`

### Phase 4: Command Updates (2 hours)
- **Scope**: All PRD and generation commands
- **Changes**: Replace relative with repo-relative paths
- **Features**: Show absolute paths in output
- **Pattern**: `docs/prds/` → `${REPO_ROOT}/docs/prds/`

### Phase 5: Testing & Documentation (1 hour)
- **Tests**: Unit, integration, performance
- **Docs**: User guide, migration guide, API docs
- **Validation**: Multi-platform, edge cases

## Key Design Decisions

### 1. Repository Detection Strategy
- **Primary**: Look for `.git` directory walking up tree
- **Override**: `CLAUDE_OUTPUT_ROOT` environment variable
- **Fallback**: Current working directory
- **Cache**: TTL-based with path keys

### 2. Path Template Variables
- `${REPO_ROOT}` - Repository root or CWD
- `${CWD}` - Original working directory
- `${HOME}` - User home directory
- `${DATE}` - Current date (YYYY-MM-DD)
- `${TIMESTAMP}` - Unix timestamp

### 3. Backward Compatibility
- Environment detection is automatic
- Existing commands continue to work
- Gradual migration approach
- Clear migration documentation

### 4. Performance Targets
- Cached lookups: < 10ms
- Uncached lookups: < 100ms
- Total hook overhead: < 50ms
- No noticeable impact on command execution

## Example Workflows

### Before Implementation
```bash
cd /Users/sean/project1/src/components
claude /prd "New Feature"
# Creates: /Users/sean/project1/src/components/docs/prds/new-feature.md ❌

cd /Users/sean/project2
claude /prd "Another Feature"  
# Creates: /Users/sean/project2/docs/prds/another-feature.md ❌
```

### After Implementation
```bash
cd /Users/sean/project1/src/components
claude /prd "New Feature"
# Creates: /Users/sean/project1/docs/prds/new-feature.md ✓
# Shows: "✓ PRD saved to: /Users/sean/project1/docs/prds/2024-01-21-new-feature.md"

cd /Users/sean/project2/deep/nested/directory
claude /prd "Another Feature"
# Creates: /Users/sean/project2/docs/prds/another-feature.md ✓
# Shows: "✓ PRD saved to: /Users/sean/project2/docs/prds/2024-01-21-another-feature.md"
```

## Risk Mitigation

1. **Performance Impact**
   - Aggressive caching of repository detection
   - Lazy loading of Python modules
   - Consider pure shell implementation if needed

2. **Edge Cases**
   - Comprehensive test suite for all scenarios
   - Graceful fallbacks for all error conditions
   - Clear error messages with remediation steps

3. **User Disruption**
   - No breaking changes to existing workflows
   - Clear migration documentation
   - Gradual rollout with feature flags if needed

## Success Metrics

1. **Functional Success**
   - All commands use consistent paths
   - Works from any directory in repository
   - Graceful fallback outside repositories
   - Environment override works correctly

2. **Performance Success**
   - No noticeable slowdown in commands
   - Cache hit rate > 95% in typical usage
   - Sub-100ms resolution time

3. **User Success**
   - Zero breaking changes reported
   - Positive feedback on consistency
   - Reduced confusion about file locations
   - Easy migration for existing users

## Next Steps

1. **Immediate Actions**
   - Begin Phase 1 implementation
   - Set up test repository structure
   - Create performance benchmarks

2. **Communication**
   - Announce planned changes to users
   - Gather feedback on design decisions
   - Create beta testing group

3. **Long-term Vision**
   - Consider workspace management features
   - Add project-level configuration
   - Integrate with version control better

## Conclusion

This implementation provides a robust solution to the path consistency problem while maintaining backward compatibility and excellent performance. The phased approach allows for incremental development and testing, reducing risk and ensuring quality at each step.