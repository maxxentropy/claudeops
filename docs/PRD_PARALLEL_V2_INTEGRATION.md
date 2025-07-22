# PRD Parallel V2 Integration Guide

This document describes the enhanced integration process for the `prd_parallel` project using the v2 import fixing capabilities.

## Overview

The `/prd-integrate-v2` command has been enhanced to support the `prd_parallel` project with automatic Python import transformations. This ensures that all Python modules work correctly after integration without manual import fixes.

## Key Features

### 1. Automatic Import Transformation

The v2 integration automatically transforms imports to use the correct package prefix:

```python
# Before (in sandbox)
from models.parallel_execution import PhaseInfo
from analyzers.wave_calculator import WaveCalculator

# After (integrated)
from prd_parallel.models.parallel_execution import PhaseInfo
from prd_parallel.analyzers.wave_calculator import WaveCalculator
```

### 2. Python Module Name Sanitization

Directories with hyphens are automatically converted to underscores for Python compatibility:

```
lib/prd-parallel/ → lib/prd_parallel/
tests/prd-parallel/ → tests/prd_parallel/
```

### 3. Test File Import Fixing

Test files have their `sys.path` manipulations removed and imports updated:

```python
# Before (in test file)
import sys
sys.path.insert(0, os.path.dirname(__file__))
from models.execution_state import ExecutionState

# After (integrated)
from prd_parallel.models.execution_state import ExecutionState
```

### 4. Automatic __init__.py Creation

The integration ensures all directories have proper `__init__.py` files to make them valid Python packages.

## Usage

### Basic Integration

```bash
# Run the v2 integration for prd_parallel
python ~/.claude/scripts/integrate_prd_parallel_v2.py

# Preview changes without applying (dry run)
python ~/.claude/scripts/integrate_prd_parallel_v2.py --dry-run
```

### Integration Output

The integration creates a detailed report showing:
- Files created/updated/skipped
- Import transformations applied
- Validation issues (if any)
- Backup location for rollback

Example output:
```
Enhanced PRD Integration Report (v2)
============================================================
Project: parallel-prd-execution-enhanced
Package: prd_parallel
Date: 2025-07-22 10:30:45
Backup ID: 2025-07-22-103045

Integration Summary
------------------------------
Status: SUCCESS
Files created: 45
Files updated: 0
Files skipped: 5
Import transformations: 23
Errors: 0

Import Transformations Applied:
------------------------------
✓ parallel_execution.py: Transformed imports to use prd_parallel prefix
✓ wave_calculator.py: Transformed imports to use prd_parallel prefix
✓ dependency_analyzer.py: Transformed imports to use prd_parallel prefix
...
```

## Integration Workflow

1. **Pre-flight Checks**
   - Validates workspace structure
   - Checks for Python files needing transformation
   - Creates backup directory

2. **File Processing**
   - Copies files from sandbox to target locations
   - Transforms Python imports on-the-fly
   - Sanitizes directory names for Python compatibility

3. **Post-Processing**
   - Creates missing `__init__.py` files
   - Validates all imports will resolve correctly
   - Generates comprehensive report

4. **Testing**
   ```bash
   # Run tests to verify integration
   cd ~/.claude/tests/prd_parallel
   python -m pytest
   
   # Test CLI commands
   python -m prd_parallel.cli.prd_parallel_cli --help
   ```

## Rollback Support

If issues arise, you can rollback the integration:

```bash
# Use the backup ID from the integration report
/prd-rollback parallel-prd-execution-enhanced --backup-id 2025-07-22-103045
```

## File Structure After Integration

```
~/.claude/
├── lib/
│   └── prd_parallel/           # Python-compliant package name
│       ├── __init__.py
│       ├── analyzers/
│       ├── cli/
│       ├── config/
│       ├── core/
│       ├── models/
│       ├── monitoring/
│       ├── orchestrator/
│       └── parsers/
├── tests/
│   └── prd_parallel/          # Matching test structure
│       ├── __init__.py
│       ├── test_analyzers.py
│       ├── test_cli.py
│       └── ...
└── commands/
    └── workflow/
        ├── prd-parallel.md    # Command documentation
        └── prd-integrate-v2.md
```

## Troubleshooting

### Import Errors After Integration

If you encounter import errors:

1. Check the validation section of the integration report
2. Ensure PYTHONPATH includes the lib directory:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:~/.claude/lib"
   ```

3. Verify all `__init__.py` files were created:
   ```bash
   find ~/.claude/lib/prd_parallel -name "__init__.py" | wc -l
   ```

### Module Not Found Errors

If Python can't find the `prd_parallel` module:

1. Check you're in the correct directory
2. Verify the package was installed correctly:
   ```python
   import sys
   print(sys.path)
   import prd_parallel
   ```

## Next Steps

After successful integration:

1. **Test the Integration**
   ```bash
   cd ~/.claude
   python -m pytest tests/prd_parallel/
   ```

2. **Use the Parallel PRD Commands**
   ```bash
   # Execute PRD phases in parallel
   /prd-parallel my-project
   
   # Analyze dependencies
   /prd-analyze my-project
   ```

3. **Commit the Changes**
   ```bash
   git add lib/prd_parallel tests/prd_parallel
   git commit -m "feat: integrate parallel PRD execution with v2 import fixes"
   ```

## Related Documentation

- [PRD Parallel Execution Guide](./prd_parallel/PARALLEL_EXECUTION_GUIDE.md)
- [PRD Parallel API Reference](./prd_parallel/API_REFERENCE.md)
- [PRD Integration Fix Documentation](./PRD_INTEGRATION_FIX_TEST_REPORT.md)