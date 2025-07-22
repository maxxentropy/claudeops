#!/usr/bin/env python3
"""
Integration script for parallel-prd-execution-enhanced
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add the system utilities to the path
sys.path.insert(0, os.path.expanduser('~/.claude'))
from system.utils import path_resolver

def main():
    project_name = "parallel-prd-execution-enhanced"
    
    print(f"Integrating project: {project_name}")
    print("=" * 60)
    
    # Get workspace path
    workspace_path = path_resolver.get_workspace_path(project_name)
    if not workspace_path.exists():
        print(f"Error: No workspace found for project: {project_name}")
        return 1
    
    # Load integration mapping
    mapping_file = workspace_path / "integration" / "mapping.json"
    if not mapping_file.exists():
        print(f"Error: No integration mapping found at {mapping_file}")
        return 1
    
    with open(mapping_file) as f:
        mapping_config = json.load(f)
    
    # Get repository root
    repo_root = path_resolver.get_repo_root()
    if not repo_root:
        print("Warning: Not in a git repository, using current directory")
        repo_root = Path.cwd()
    
    # Create backup directory
    timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    backup_path = workspace_path / "backups" / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Track integration results
    created_files = []
    updated_files = []
    skipped_files = []
    errors = []
    
    # Get sandbox path
    sandbox_path = workspace_path / "sandbox"
    
    # Process files
    mappings = mapping_config.get("mappings", {})
    ignore_patterns = mapping_config.get("ignore", [])
    
    for mapping_source, mapping_target in mappings.items():
        source_dir = sandbox_path / mapping_source
        
        if not source_dir.exists():
            continue
            
        # Find all files in the source directory
        for source_file in source_dir.rglob("*"):
            if not source_file.is_file():
                continue
            
            # Check if file should be ignored
            should_ignore = False
            for pattern in ignore_patterns:
                if source_file.match(pattern):
                    should_ignore = True
                    break
            
            if should_ignore:
                skipped_files.append(str(source_file.relative_to(sandbox_path)))
                continue
            
            # Calculate target path
            relative_to_source = source_file.relative_to(source_dir)
            target_path = repo_root / mapping_target / relative_to_source
            
            try:
                # Create parent directories
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if target exists
                if target_path.exists():
                    # Compare files
                    with open(source_file, 'rb') as sf, open(target_path, 'rb') as tf:
                        if sf.read() == tf.read():
                            # Files are identical, skip
                            continue
                    
                    # Backup existing file
                    backup_file = backup_path / target_path.relative_to(repo_root)
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target_path, backup_file)
                    
                    # Copy new version
                    shutil.copy2(source_file, target_path)
                    updated_files.append(str(target_path.relative_to(repo_root)))
                else:
                    # Copy new file
                    shutil.copy2(source_file, target_path)
                    created_files.append(str(target_path.relative_to(repo_root)))
                    
            except Exception as e:
                errors.append(f"{source_file}: {str(e)}")
    
    # Create benchmarks directory if needed
    benchmarks_dir = repo_root / "lib" / "prd_parallel" / "benchmarks"
    if not benchmarks_dir.exists():
        benchmarks_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {benchmarks_dir.relative_to(repo_root)}")
    
    # Generate integration report
    report_lines = [
        "Integration Report",
        "=" * 60,
        f"Project: {project_name}",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Backup ID: {timestamp}",
        "",
        "Integration Summary",
        "-" * 30,
        f"Status: {'SUCCESS' if not errors else 'PARTIAL'}",
        f"Files created: {len(created_files)}",
        f"Files updated: {len(updated_files)}",
        f"Files skipped: {len(skipped_files)}",
        f"Errors: {len(errors)}",
        ""
    ]
    
    if created_files:
        report_lines.extend([
            "Files Created:",
            "-" * 30
        ])
        for f in sorted(created_files):
            report_lines.append(f"✓ {f}")
        report_lines.append("")
    
    if updated_files:
        report_lines.extend([
            "Files Updated:",
            "-" * 30
        ])
        for f in sorted(updated_files):
            report_lines.append(f"✓ {f}")
        report_lines.append("")
    
    if skipped_files:
        report_lines.extend([
            "Files Skipped (ignored):",
            "-" * 30
        ])
        for f in sorted(skipped_files):
            report_lines.append(f"- {f}")
        report_lines.append("")
    
    if errors:
        report_lines.extend([
            "Errors:",
            "-" * 30
        ])
        for e in errors:
            report_lines.append(f"✗ {e}")
        report_lines.append("")
    
    report_lines.extend([
        "Next Steps:",
        "-" * 30,
        "1. Review changes with: git status",
        "2. Test the integration:",
        "   cd tests/prd_parallel && python run_tests.py",
        "3. Commit when ready:",
        "   git add lib/prd_parallel tests/prd_parallel",
        '   git commit -m "Update parallel PRD execution system"',
        "",
        "Rollback Information:",
        "-" * 30,
        f"To rollback this integration, use:",
        f"/prd-rollback {project_name} --backup-id {timestamp}",
        ""
    ])
    
    # Save report
    report_path = workspace_path / f"integration-report-{timestamp}.txt"
    report_path.write_text("\n".join(report_lines))
    
    # Print report
    print("\n".join(report_lines))
    
    # Format output paths
    output_paths = {
        "Workspace": workspace_path,
        "Integration report": report_path
    }
    if backup_path.exists() and any(backup_path.iterdir()):
        output_paths["Backup created"] = backup_path
    
    print(path_resolver.format_output_message(output_paths))
    
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())