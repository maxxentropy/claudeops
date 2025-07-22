#!/usr/bin/env python3
"""
Enhanced Integration script for parallel-prd-execution with v2 import fixing
Combines parallel PRD execution capabilities with automatic Python import transformation
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add the system utilities to the path
sys.path.insert(0, os.path.expanduser('~/.claude'))
from system.utils.path_resolver import PathResolver
from lib.prd_integration_fix import (
    sanitize_python_path,
    transform_imports,
    detect_import_issues,
    create_init_files,
    validate_python_imports,
    create_integration_preview
)


class PRDParallelIntegratorV2:
    """Enhanced integrator for PRD parallel execution with import fixing."""
    
    def __init__(self, project_name: str = "parallel-prd-execution-enhanced"):
        self.project_name = project_name
        self.package_name = "prd_parallel"
        self.path_resolver = PathResolver()
        
        # Get workspace path - handle case where we're already in .claude
        workspace_base = self.path_resolver.get_workspace_path(project_name)
        if not workspace_base.exists():
            # Try relative to current directory if we're in .claude
            alt_path = Path.cwd() / "prd-workspace" / project_name
            if alt_path.exists():
                workspace_base = alt_path
        self.workspace_path = workspace_base
        
        self.repo_root = self.path_resolver.get_repo_root() or Path.cwd()
        self.timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        
    def load_mapping_config(self) -> Dict:
        """Load and enhance the integration mapping configuration."""
        mapping_file = self.workspace_path / "integration" / "mapping.json"
        if not mapping_file.exists():
            raise FileNotFoundError(f"No integration mapping found at {mapping_file}")
        
        with open(mapping_file) as f:
            mapping_config = json.load(f)
        
        # Enhance with v2 integration rules
        mapping_config.update({
            "python_package_name": self.package_name,
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
                "preserve_stdlib_imports": True
            }
        })
        
        return mapping_config
    
    def create_backup(self) -> Path:
        """Create a backup of existing files."""
        backup_path = self.workspace_path / "backups" / self.timestamp
        backup_path.mkdir(parents=True, exist_ok=True)
        return backup_path
    
    def process_python_file(self, content: str, source_path: Path, target_path: Path) -> str:
        """Transform Python file content during integration."""
        # Detect import issues
        issues = detect_import_issues(str(source_path), content)
        
        # Transform imports to use package prefix
        content = transform_imports(content, self.package_name)
        
        # Additional transformations for test files
        if 'test' in source_path.name or source_path.parts[-2] == 'tests':
            # Remove sys.path manipulations from test files
            lines = content.split('\n')
            filtered_lines = []
            skip_next = False
            
            for line in lines:
                if skip_next:
                    skip_next = False
                    continue
                    
                if 'sys.path.insert' in line or 'sys.path.append' in line:
                    skip_next = True
                    continue
                    
                # Transform test imports
                if line.strip().startswith('from ') and '..' in line:
                    # Convert relative imports in tests
                    line = line.replace('from ..', f'from {self.package_name}')
                    
                filtered_lines.append(line)
            
            content = '\n'.join(filtered_lines)
        
        return content
    
    def integrate_files(self, mapping_config: Dict, backup_path: Path) -> Dict[str, List[str]]:
        """Integrate files with v2 enhancements."""
        results = {
            "created": [],
            "updated": [],
            "skipped": [],
            "errors": [],
            "transformations": []
        }
        
        sandbox_path = self.workspace_path / "sandbox"
        mappings = mapping_config.get("mappings", {})
        ignore_patterns = mapping_config.get("ignore", [])
        
        for mapping_source, mapping_target in mappings.items():
            source_dir = sandbox_path / mapping_source
            
            if not source_dir.exists():
                continue
            
            # Apply Python naming conventions to target path
            if mapping_config["integration_rules"]["sanitize_python_names"]:
                mapping_target = sanitize_python_path(mapping_target)
            
            for source_file in source_dir.rglob("*"):
                if not source_file.is_file():
                    continue
                
                # Check ignore patterns
                should_ignore = any(source_file.match(pattern) for pattern in ignore_patterns)
                if should_ignore:
                    results["skipped"].append(str(source_file.relative_to(sandbox_path)))
                    continue
                
                # Calculate target path with sanitization
                relative_to_source = source_file.relative_to(source_dir)
                if mapping_config["integration_rules"]["sanitize_python_names"]:
                    sanitized_path = sanitize_python_path(str(relative_to_source))
                    relative_to_source = Path(sanitized_path)
                
                target_path = self.repo_root / mapping_target / relative_to_source
                
                try:
                    # Create parent directories
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Read source content
                    if source_file.suffix == '.py':
                        content = source_file.read_text()
                        original_content = content
                        
                        # Process Python file
                        if mapping_config["integration_rules"]["transform_imports"]:
                            content = self.process_python_file(content, source_file, target_path)
                            
                            if content != original_content:
                                results["transformations"].append(
                                    f"{source_file.name}: Transformed imports to use {self.package_name} prefix"
                                )
                    else:
                        content = source_file.read_bytes()
                    
                    # Handle existing files
                    if target_path.exists():
                        # Compare content
                        if source_file.suffix == '.py':
                            existing_content = target_path.read_text()
                            if content == existing_content:
                                continue
                        else:
                            existing_content = target_path.read_bytes()
                            if content == existing_content:
                                continue
                        
                        # Backup existing file
                        backup_file = backup_path / target_path.relative_to(self.repo_root)
                        backup_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(target_path, backup_file)
                        
                        # Write updated content
                        if isinstance(content, str):
                            target_path.write_text(content)
                        else:
                            target_path.write_bytes(content)
                        results["updated"].append(str(target_path.relative_to(self.repo_root)))
                    else:
                        # Write new file
                        if isinstance(content, str):
                            target_path.write_text(content)
                        else:
                            target_path.write_bytes(content)
                        results["created"].append(str(target_path.relative_to(self.repo_root)))
                        
                except Exception as e:
                    results["errors"].append(f"{source_file}: {str(e)}")
        
        # Create __init__.py files
        if mapping_config["integration_rules"]["create_init_files"]:
            package_dir = self.repo_root / "lib" / self.package_name
            if package_dir.exists():
                created_inits = create_init_files(package_dir)
                for init_file in created_inits:
                    results["created"].append(str(init_file.relative_to(self.repo_root)))
                    results["transformations"].append(
                        f"Created {init_file.name} in {init_file.parent.name}"
                    )
        
        return results
    
    def validate_integration(self, mapping_config: Dict) -> Dict[str, List[str]]:
        """Validate the integration for import issues."""
        validation_results = {}
        
        if mapping_config["integration_rules"]["validate_imports"]:
            package_dir = self.repo_root / "lib" / self.package_name
            if package_dir.exists():
                validation_results = validate_python_imports(package_dir, self.package_name)
        
        return validation_results
    
    def generate_report(self, results: Dict, validation: Dict, backup_path: Path) -> str:
        """Generate a comprehensive integration report."""
        report_lines = [
            "Enhanced PRD Integration Report (v2)",
            "=" * 60,
            f"Project: {self.project_name}",
            f"Package: {self.package_name}",
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Backup ID: {self.timestamp}",
            "",
            "Integration Summary",
            "-" * 30,
            f"Status: {'SUCCESS' if not results['errors'] else 'PARTIAL'}",
            f"Files created: {len(results['created'])}",
            f"Files updated: {len(results['updated'])}",
            f"Files skipped: {len(results['skipped'])}",
            f"Import transformations: {len(results['transformations'])}",
            f"Errors: {len(results['errors'])}",
            ""
        ]
        
        # Add transformation details
        if results['transformations']:
            report_lines.extend([
                "Import Transformations Applied:",
                "-" * 30
            ])
            for transformation in results['transformations']:
                report_lines.append(f"✓ {transformation}")
            report_lines.append("")
        
        # Add file details
        for category, items in [
            ("Files Created", results['created']),
            ("Files Updated", results['updated']),
            ("Files Skipped", results['skipped']),
            ("Errors", results['errors'])
        ]:
            if items:
                report_lines.extend([
                    f"{category}:",
                    "-" * 30
                ])
                for item in sorted(items):
                    prefix = "✓" if category != "Errors" else "✗"
                    report_lines.append(f"{prefix} {item}")
                report_lines.append("")
        
        # Add validation results
        if validation:
            report_lines.extend([
                "Import Validation Issues:",
                "-" * 30
            ])
            for file_path, issues in validation.items():
                report_lines.append(f"\n{file_path}:")
                for issue in issues:
                    report_lines.append(f"  ⚠ {issue}")
            report_lines.append("")
        
        # Add next steps
        report_lines.extend([
            "Next Steps:",
            "-" * 30,
            "1. Review changes with: git status",
            "2. Test the integration:",
            f"   cd tests/prd_parallel && python -m pytest",
            "3. Test CLI commands:",
            f"   python -m prd_parallel.cli.prd_parallel_cli --help",
            "4. Commit when ready:",
            f"   git add lib/{self.package_name} tests/{self.package_name}",
            f'   git commit -m "feat: integrate parallel PRD execution with v2 import fixes"',
            "",
            "Rollback Information:",
            "-" * 30,
            f"To rollback this integration, use:",
            f"/prd-rollback {self.project_name} --backup-id {self.timestamp}",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def run(self, dry_run: bool = False) -> int:
        """Execute the v2 integration process."""
        print(f"Enhanced PRD Integration v2: {self.project_name}")
        print("=" * 60)
        
        try:
            # Load enhanced mapping configuration
            mapping_config = self.load_mapping_config()
            
            # Show preview
            sandbox_path = self.workspace_path / "sandbox"
            preview = create_integration_preview(sandbox_path / "src", mapping_config)
            print("\n" + preview + "\n")
            
            if dry_run:
                print("DRY RUN - No files will be modified")
                return 0
            
            # Create backup
            backup_path = self.create_backup()
            print(f"Created backup at: {backup_path}")
            
            # Integrate files with transformations
            print("\nIntegrating files with import transformations...")
            results = self.integrate_files(mapping_config, backup_path)
            
            # Validate imports
            print("\nValidating Python imports...")
            validation = self.validate_integration(mapping_config)
            
            # Generate and save report
            report = self.generate_report(results, validation, backup_path)
            report_path = self.workspace_path / f"integration-report-v2-{self.timestamp}.txt"
            report_path.write_text(report)
            
            # Print report
            print("\n" + report)
            
            # Format output paths
            output_paths = {
                "Workspace": self.workspace_path,
                "Integration report": report_path,
                "Package location": self.repo_root / "lib" / self.package_name
            }
            if backup_path.exists() and any(backup_path.iterdir()):
                output_paths["Backup created"] = backup_path
            
            print(self.path_resolver.format_output_message(output_paths))
            
            return 0 if not results['errors'] else 1
            
        except Exception as e:
            print(f"\nError during integration: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Main entry point for the v2 integration script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced PRD Integration with v2 import fixing"
    )
    parser.add_argument(
        "project",
        nargs="?",
        default="parallel-prd-execution-enhanced",
        help="PRD project name (default: parallel-prd-execution-enhanced)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview integration without making changes"
    )
    
    args = parser.parse_args()
    
    integrator = PRDParallelIntegratorV2(args.project)
    return integrator.run(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())