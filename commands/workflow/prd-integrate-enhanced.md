# /prd-integrate-enhanced - Smart PRD Integration with Python Fix

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: system/personas.md#DEVOPS_ARCHITECT -->

Enhanced PRD integration that automatically handles Python module naming and import transformations.

## Purpose

Intelligently integrates PRD sandbox implementations with automatic fixes for:
- Python module naming (hyphens → underscores)
- Import path transformations (relative → absolute)
- Package structure validation
- Test environment setup

## Key Features

1. **Automatic Python Compatibility**
   - Detects and fixes hyphenated directory names
   - Creates proper Python package structure
   - Adds `__init__.py` files automatically

2. **Smart Import Transformation**
   - Converts relative imports to absolute
   - Adds package prefixes where needed
   - Preserves standard library imports

3. **Validation & Preview**
   - Shows all transformations before applying
   - Validates imports will resolve correctly
   - Detects potential issues early

## Enhanced Workflow

1. **Smart Analysis Phase**:
   ```python
   # Load the integration fix module
   from lib.prd_integration_fix import (
       sanitize_python_path,
       transform_imports,
       create_integration_preview,
       apply_integration_fixes
   )
   
   # Generate preview
   preview = create_integration_preview(sandbox_dir, mapping_config)
   print(preview)
   ```

2. **Integration Execution**:
   ```
   Integrating: parallel-prd-execution
   
   Python Compatibility Fixes:
   ✓ lib/prd-parallel → lib/prd_parallel
   ✓ tests/prd-parallel → tests/prd_parallel
   
   Import Transformations (31 files):
   ✓ from models.x → from prd_parallel.models.x
   ✓ from analyzers.y → from prd_parallel.analyzers.y
   ✓ import core.z → import prd_parallel.core.z
   
   Package Structure:
   ✓ Created 12 __init__.py files
   ✓ All imports validated
   ✓ No circular dependencies detected
   ```

3. **Enhanced Mapping Structure**:
   ```json
   {
     "repository": "~/.claude",
     "python_package_name": "prd_parallel",
     "mappings": {
       "src/": "lib/prd_parallel/",
       "tests/": "tests/prd_parallel/"
     },
     "integration_rules": {
       "sanitize_python_names": true,
       "transform_imports": true,
       "create_init_files": true,
       "validate_imports": true
     }
   }
   ```

## Import Transformation Examples

### Before (Sandbox)
```python
# In sandbox/src/analyzers/wave_calculator.py
from models.parallel_execution import PhaseInfo
from core.resource_manager import Lock
import analyzers.conflict_detector

class WaveCalculator:
    def __init__(self):
        self.phases = []
```

### After (Integrated)
```python
# In lib/prd_parallel/analyzers/wave_calculator.py
from prd_parallel.models.parallel_execution import PhaseInfo
from prd_parallel.core.resource_manager import Lock
import prd_parallel.analyzers.conflict_detector

class WaveCalculator:
    def __init__(self):
        self.phases = []
```

## Validation Steps

1. **Pre-Integration Validation**:
   - Check all Python files for import statements
   - Verify no naming conflicts
   - Ensure test files will work post-integration

2. **Transform & Validate**:
   - Apply transformations to copy of files
   - Run import validation
   - Check circular dependencies

3. **Post-Integration Test**:
   ```bash
   # Automatically run after integration
   cd tests/{package_name}
   python3 -m pytest --import-mode=importlib
   ```

## Usage

```bash
# Standard integration with automatic fixes
/prd-integrate-enhanced [project-name]

# Preview without applying
/prd-integrate-enhanced [project-name] --preview

# Skip certain transformations
/prd-integrate-enhanced [project-name] --skip-import-transform

# Custom package name
/prd-integrate-enhanced [project-name] --package-name my_package
```

## Safety Features

1. **Comprehensive Backup**: All transformations reversible
2. **Validation First**: Won't proceed if imports won't work
3. **Test Verification**: Runs basic import test post-integration
4. **Detailed Logging**: Every transformation recorded

## Integration Report

After integration, generates detailed report:

```
Integration Report: parallel-prd-execution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Files Processed: 37
Transformations Applied:
  - Path sanitization: 2 directories
  - Import updates: 31 files
  - Init files created: 12

Import Changes:
  - Relative → Absolute: 89 imports
  - Package prefix added: 89 imports
  - Unchanged (stdlib): 145 imports

Validation Results:
  ✓ All imports resolve correctly
  ✓ No circular dependencies
  ✓ Package structure valid
  ✓ Tests can import modules

Time: 2.3 seconds
Status: SUCCESS

Test Command:
  cd /Users/you/.claude && python3 -m pytest tests/prd_parallel/
```

## Implementation Note

This enhanced version uses the `prd_integration_fix.py` module to ensure:
- Zero manual intervention required
- Works correctly for any Python project
- Maintains compatibility with existing PRD workflow
- Provides clear visibility into all changes

The integration now "just works" without any post-integration fixes needed!