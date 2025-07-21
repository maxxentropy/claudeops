#!/usr/bin/env python3
"""
Comprehensive Integration Fix Strategy for PRD Workflow
Implements automatic Python module naming and import transformation
"""

import re
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def sanitize_python_path(path: str) -> str:
    """
    Convert hyphens to underscores for Python compatibility.
    
    Args:
        path: File or directory path that may contain hyphens
        
    Returns:
        Path with hyphens converted to underscores in directory names
    """
    if path.endswith('.py') or '/' in path:
        parts = path.split('/')
        parts = [p.replace('-', '_') if not p.endswith('.py') else p 
                 for p in parts]
        return '/'.join(parts)
    return path.replace('-', '_')


def transform_imports(file_content: str, package_name: str) -> str:
    """
    Transform relative imports to absolute imports with package prefix.
    
    Args:
        file_content: Python file content with relative imports
        package_name: Target package name (e.g., 'prd_parallel')
        
    Returns:
        File content with transformed imports
    """
    # Pattern 1: from models.x import y -> from package.models.x import y
    file_content = re.sub(
        r'from (models|analyzers|core|config|parsers|orchestrator|monitoring|cli|benchmarks)\.', 
        f'from {package_name}.\\1.',
        file_content
    )
    
    # Pattern 2: import models.x -> import package.models.x
    file_content = re.sub(
        r'import (models|analyzers|core|config|parsers|orchestrator|monitoring|cli|benchmarks)\.', 
        f'import {package_name}.\\1.',
        file_content
    )
    
    # Pattern 3: from .module import x -> from package.current_module import x
    # This requires context about current module location
    
    return file_content


def detect_import_issues(file_path: str, content: str) -> List[str]:
    """
    Detect potential import issues in a Python file.
    
    Returns:
        List of import lines that may need transformation
    """
    issues = []
    lines = content.split('\n')
    
    import_patterns = [
        r'^from\s+(models|analyzers|core|config|parsers|orchestrator|monitoring|cli)\.',
        r'^import\s+(models|analyzers|core|config|parsers|orchestrator|monitoring|cli)\.',
        r'^from\s+\.\.',  # Relative imports
    ]
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        for pattern in import_patterns:
            if re.match(pattern, line):
                issues.append(f"Line {i}: {line}")
                break
                
    return issues


def create_init_files(package_dir: Path) -> List[Path]:
    """
    Create __init__.py files in all directories to make them proper Python packages.
    
    Returns:
        List of created __init__.py files
    """
    created = []
    
    for dirpath, dirnames, filenames in os.walk(package_dir):
        dirpath = Path(dirpath)
        init_file = dirpath / '__init__.py'
        
        # Skip hidden directories and __pycache__
        if any(part.startswith('.') or part == '__pycache__' for part in dirpath.parts):
            continue
            
        # Create __init__.py if it doesn't exist
        # Include directories that contain Python files OR subdirectories
        if not init_file.exists() and (dirnames or any(f.endswith('.py') for f in filenames)):
            init_file.write_text('"""Package initialization."""\n')
            created.append(init_file)
            
    return created


def validate_python_imports(package_dir: Path, package_name: str) -> Dict[str, List[str]]:
    """
    Validate that all imports in the package will work correctly.
    
    Returns:
        Dictionary mapping file paths to list of import issues
    """
    issues = {}
    
    for py_file in package_dir.rglob('*.py'):
        content = py_file.read_text()
        file_issues = []
        
        # Check for imports that won't resolve
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip().startswith(('import ', 'from ')):
                # Simple validation - check if import starts with package name
                if package_name not in line and not line.strip().startswith(('import os', 
                    'import sys', 'from typing', 'from pathlib', 'from datetime',
                    'from collections', 'from enum', 'from dataclasses', 'import re',
                    'import json', 'import unittest', 'import threading', 'import time')):
                    # Check if it's a relative import that needs transformation
                    if re.match(r'from (models|analyzers|core|config|parsers|orchestrator|monitoring|cli)\.', line.strip()):
                        file_issues.append(f"Line {i}: {line.strip()} -> Needs package prefix")
                        
        if file_issues:
            issues[str(py_file.relative_to(package_dir.parent))] = file_issues
            
    return issues


def generate_enhanced_mapping(project_name: str, package_name: Optional[str] = None) -> Dict:
    """
    Generate enhanced mapping.json structure with Python integration rules.
    
    Args:
        project_name: Name of the PRD project
        package_name: Python package name (auto-generated if not provided)
        
    Returns:
        Enhanced mapping configuration
    """
    if not package_name:
        # Auto-generate package name from project name
        package_name = project_name.replace('-', '_').lower()
        
    return {
        "repository": "auto-detect",
        "python_package_name": package_name,
        "mappings": {
            "src/": f"lib/{package_name}/",
            "tests/": f"tests/{package_name}/",
            "commands/": "commands/workflow/",
            "docs/": f"docs/{package_name}/"
        },
        "integration_rules": {
            "sanitize_python_names": True,
            "transform_imports": True,
            "create_init_files": True,
            "validate_imports": True,
            "backup_originals": True
        },
        "import_transformations": {
            "relative_to_absolute": True,
            "add_package_prefix": True,
            "preserve_stdlib_imports": True,
            "custom_rules": []
        }
    }


def apply_integration_fixes(
    source_dir: Path,
    target_dir: Path,
    mapping_config: Dict
) -> Tuple[int, List[str]]:
    """
    Apply all integration fixes during file copying.
    
    Returns:
        Tuple of (files_processed, issues_found)
    """
    files_processed = 0
    issues = []
    
    package_name = mapping_config.get('python_package_name', 'package')
    rules = mapping_config.get('integration_rules', {})
    
    for source_file in source_dir.rglob('*'):
        if source_file.is_file():
            # Calculate target path
            rel_path = source_file.relative_to(source_dir)
            
            # Apply path sanitization
            if rules.get('sanitize_python_names', True):
                target_rel_path = Path(sanitize_python_path(str(rel_path)))
            else:
                target_rel_path = rel_path
                
            target_file = target_dir / target_rel_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Process file content
            if source_file.suffix == '.py' and rules.get('transform_imports', True):
                content = source_file.read_text()
                
                # Detect issues before transformation
                import_issues = detect_import_issues(str(source_file), content)
                if import_issues:
                    issues.extend([f"{source_file}: {issue}" for issue in import_issues])
                
                # Transform imports
                content = transform_imports(content, package_name)
                target_file.write_text(content)
            else:
                # Copy non-Python files as-is
                target_file.write_bytes(source_file.read_bytes())
                
            files_processed += 1
    
    # Create __init__.py files
    if rules.get('create_init_files', True):
        created_inits = create_init_files(target_dir)
        files_processed += len(created_inits)
        
    return files_processed, issues


def create_integration_preview(
    source_dir: Path,
    mapping_config: Dict
) -> str:
    """
    Generate a preview of what the integration will do.
    
    Returns:
        Formatted preview string
    """
    preview_lines = ["Integration Preview", "=" * 50, ""]
    
    package_name = mapping_config.get('python_package_name', 'package')
    rules = mapping_config.get('integration_rules', {})
    
    # Check for Python files
    py_files = list(source_dir.rglob('*.py'))
    preview_lines.append(f"Python files found: {len(py_files)}")
    
    # Check for naming issues
    naming_issues = []
    for f in source_dir.rglob('*'):
        if '-' in f.name and f.is_dir():
            naming_issues.append(f"  {f.name} → {f.name.replace('-', '_')}")
            
    if naming_issues and rules.get('sanitize_python_names', True):
        preview_lines.extend([
            "\nPython Module Name Corrections:",
            *naming_issues
        ])
    
    # Check for import transformations needed
    import_transforms = 0
    for py_file in py_files:
        content = py_file.read_text()
        if detect_import_issues(str(py_file), content):
            import_transforms += 1
            
    if import_transforms and rules.get('transform_imports', True):
        preview_lines.extend([
            f"\nImport Transformations: {import_transforms} files",
            f"  Package prefix: {package_name}"
        ])
    
    # Show target structure
    preview_lines.extend([
        "\nTarget Structure:",
        f"  lib/{package_name}/",
        f"  tests/{package_name}/"
    ])
    
    return '\n'.join(preview_lines)


# Example usage and testing
if __name__ == "__main__":
    # Test path sanitization
    print("Path Sanitization Tests:")
    print(f"  lib/prd-parallel/ → {sanitize_python_path('lib/prd-parallel/')}")
    print(f"  tests/prd-parallel/test.py → {sanitize_python_path('tests/prd-parallel/test.py')}")
    
    # Test import transformation
    print("\nImport Transformation Test:")
    sample_code = """
from models.parallel_execution import PhaseInfo
import analyzers.wave_calculator
from core.resource_manager import Lock
    """
    transformed = transform_imports(sample_code.strip(), "prd_parallel")
    print(transformed)
    
    # Generate sample mapping
    print("\nSample Enhanced Mapping:")
    mapping = generate_enhanced_mapping("parallel-prd-execution")
    print(json.dumps(mapping, indent=2))