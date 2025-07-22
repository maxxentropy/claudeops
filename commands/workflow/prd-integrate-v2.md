# /prd-integrate-v2 - Enhanced PRD Integration with Import Fixing

🎯 **COMMAND**: /prd-integrate-v2 | 📋 **WORKFLOW**: integrate-v2 - Enhanced PRD Integration with Import Fixing | 👤 **PERSONAS**: Software Architect + Devops Architect

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: system/personas.md#DEVOPS_ARCHITECT -->

Enhanced version of PRD integration that handles Python imports correctly.

## Key Enhancements

1. **Python Module Name Validation**
   - Detect target directories with hyphens
   - Automatically convert to underscores for Python compatibility
   - Warn user about naming changes

2. **Import Path Transformation**
   - Detect Python files during integration
   - Transform relative imports to absolute imports
   - Add package prefix based on target location

3. **Sandbox Structure Recommendations**
   - Suggest sandbox structure that mirrors production
   - Validate import compatibility before integration

## Enhanced Workflow

1. **Pre-Integration Analysis**:
   ```
   Analyzing integration compatibility...
   ⚠️ Target directory 'lib/prd-parallel' contains hyphen
   ✓ Will create as 'lib/prd_parallel' for Python compatibility
   
   Import transformations needed:
   - models.parallel_execution → prd_parallel.models.parallel_execution
   - analyzers.wave_calculator → prd_parallel.analyzers.wave_calculator
   - 15 files will have imports updated
   ```

2. **Smart File Processing**:
   ```python
   def process_python_file(content, source_path, target_path):
       """Transform imports during integration."""
       # Detect package name from target path
       package_name = extract_package_name(target_path)
       
       # Transform relative imports
       content = transform_imports(content, package_name)
       
       return content
   ```

3. **Integration Mapping Enhancement**:
   ```json
   {
     "repository": "~/.claude",
     "mappings": {
       "src/": "lib/prd_parallel/"  // Use underscores
     },
     "import_rules": {
       "package_prefix": "prd_parallel",
       "transform_relative": true
     }
   }
   ```

## Import Transformation Rules

1. **Relative to Absolute**:
   ```python
   # Before (in sandbox)
   from models.parallel_execution import PhaseInfo
   
   # After (integrated)
   from prd_parallel.models.parallel_execution import PhaseInfo
   ```

2. **Internal Imports**:
   ```python
   # Before
   from ..core.resource_manager import Lock
   
   # After
   from prd_parallel.core.resource_manager import Lock
   ```

3. **Test Imports**:
   ```python
   # Before (in test file)
   sys.path.insert(0, os.path.dirname(__file__))
   from models.x import Y
   
   # After
   from prd_parallel.models.x import Y
   ```

## Validation Steps

1. **Python Compatibility Check**:
   - Validate all target paths are Python-importable
   - No hyphens in module paths
   - Proper __init__.py files created

2. **Import Verification**:
   - Parse all Python files for import statements
   - Verify transformed imports will resolve
   - Check for circular dependencies

3. **Test Environment Setup**:
   - Ensure test files can import integrated modules
   - Update test runners with correct paths
   - Validate PYTHONPATH settings

## Example Integration Report

```
Integration Preview: parallel-prd-execution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Python Module Corrections:
  lib/prd-parallel → lib/prd_parallel ✓

Import Transformations (31 files):
  ✓ models.* → prd_parallel.models.*
  ✓ analyzers.* → prd_parallel.analyzers.*
  ✓ core.* → prd_parallel.core.*

Package Structure:
  lib/prd_parallel/
    __init__.py (will create)
    models/
      __init__.py ✓
      parallel_execution.py ✓
    analyzers/
      __init__.py ✓
      wave_calculator.py ✓

Ready to integrate with automatic fixes
```

## PRD Parallel Integration Support

For the `prd_parallel` project specifically, use the enhanced integration script:

```bash
# Run the v2 integration for prd_parallel
python ~/.claude/scripts/integrate_prd_parallel_v2.py

# Preview changes without applying
python ~/.claude/scripts/integrate_prd_parallel_v2.py --dry-run

# Integrate a different PRD project
python ~/.claude/scripts/integrate_prd_parallel_v2.py [project-name]
```

The enhanced script provides:
- Automatic import transformation for all prd_parallel modules
- Test file import fixing (removes sys.path manipulations)
- Comprehensive validation of transformed imports
- Detailed transformation report

## Safety Features

1. **Dry Run Mode**: Preview all transformations
2. **Rollback Support**: Original imports preserved in backup
3. **Validation Suite**: Run import tests before finalizing
4. **Manual Override**: Option to skip transformations

This enhanced integration ensures Python packages work immediately after integration without manual fixes.