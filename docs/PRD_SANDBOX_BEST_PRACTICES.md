# PRD Sandbox Best Practices

## Overview

This guide outlines best practices for structuring PRD implementations in the sandbox to ensure seamless integration.

## Recommended Sandbox Structure

### 1. Use Production-Ready Package Names

```
sandbox/
├── package_name/           # Use underscores, not hyphens
│   ├── __init__.py        # Include from the start
│   ├── models/
│   │   ├── __init__.py
│   │   └── core.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   └── engine.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_analyzers.py
├── setup.py               # Optional: for complex projects
└── requirements.txt       # Track dependencies
```

### 2. Use Absolute Imports from the Start

**✅ Correct (Absolute imports with package name):**
```python
# In sandbox/my_package/analyzers/engine.py
from my_package.models.core import BaseModel
from my_package.utils.helpers import format_data
```

**❌ Incorrect (Relative imports):**
```python
# These will break after integration
from models.core import BaseModel
from ..utils.helpers import format_data
```

### 3. Create Proper Python Packages

Always include `__init__.py` files in every directory that contains Python modules:

```python
# sandbox/my_package/__init__.py
"""My Package - Main module."""

__version__ = "0.1.0"

# Optional: expose key classes/functions
from my_package.models.core import BaseModel
from my_package.analyzers.engine import Analyzer

__all__ = ['BaseModel', 'Analyzer']
```

### 4. Test Imports Match Production

Structure your tests to use the same import style as production:

```python
# sandbox/tests/test_models.py
import sys
import os

# Add parent directory to path if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Use full package imports
from my_package.models.core import BaseModel
from my_package.utils.helpers import validate_input

class TestModels(unittest.TestCase):
    def test_base_model(self):
        model = BaseModel()
        self.assertIsNotNone(model)
```

### 5. Configure mapping.json Correctly

Include Python-specific configuration:

```json
{
  "repository": "~/.claude",
  "python_package_name": "my_package",
  "mappings": {
    "my_package/": "lib/my_package/",
    "tests/": "tests/my_package/",
    "docs/": "docs/my_package/"
  },
  "integration_rules": {
    "sanitize_python_names": true,
    "transform_imports": false,  // Not needed if using absolute imports
    "create_init_files": true,
    "validate_imports": true
  }
}
```

## Phase-Specific Guidelines

### Phase 1: Foundation
- Create the package structure immediately
- Use the final package name from the start
- Include `__init__.py` files
- Set up proper imports

### Phase 2+: Implementation
- Always use absolute imports with package name
- Test imports in isolation
- Validate module structure regularly

### Before Integration
- Run import validation tests
- Check for any relative imports
- Ensure all `__init__.py` files exist
- Verify package name has no hyphens

## Common Pitfalls to Avoid

1. **Don't use hyphens in package names**
   - Bad: `my-awesome-package`
   - Good: `my_awesome_package`

2. **Don't use relative imports**
   - Bad: `from ..models import User`
   - Good: `from my_package.models import User`

3. **Don't forget __init__.py files**
   - Every directory with Python files needs one
   - Can be empty, but must exist

4. **Don't mix import styles**
   - Pick absolute imports and stick with them
   - Be consistent across all modules

## Testing Before Integration

Create a simple test script to validate imports:

```python
# sandbox/test_imports.py
#!/usr/bin/env python3
"""Test that all imports work correctly."""

import sys
import os

# Add sandbox to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Test all major imports
    from my_package.models.core import BaseModel
    from my_package.analyzers.engine import Analyzer
    from my_package.utils.helpers import format_data
    
    print("✅ All imports successful!")
    
    # Basic functionality test
    model = BaseModel()
    analyzer = Analyzer()
    
    print("✅ Basic instantiation works!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
```

## Benefits of Following These Practices

1. **Zero integration issues** - Everything works immediately after `ccintegrate`
2. **No manual fixes needed** - Imports are already correct
3. **Easier testing** - Same import structure in sandbox and production
4. **Better collaboration** - Team members can work independently
5. **Cleaner code** - Consistent structure throughout

## Summary

By following these practices from the beginning of your PRD implementation:
- Your code will integrate seamlessly
- No import errors after integration  
- No manual renaming needed
- Tests will work immediately
- You can focus on functionality, not infrastructure

Remember: **Start with the end in mind** - structure your sandbox as if it's already integrated!