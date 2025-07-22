#!/usr/bin/env python3
"""Master test runner for all path resolution tests."""

import sys
import subprocess
from pathlib import Path


def run_test_file(test_file):
    """Run a single test file and return results."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file.name}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, str(test_file)],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def main():
    """Run all path resolution tests."""
    test_dir = Path(__file__).parent
    
    # List of test files to run
    test_files = [
        test_dir / 'test_path_resolution.py',
        test_dir / 'test_path_resolution_commands.py',
        test_dir / 'test_path_resolution_phase3.py',
        test_dir / 'test_path_resolution_edge_cases.py',
        test_dir / 'test_slash_commands_integration.py',
    ]
    
    print("🧪 Running Complete Path Resolution Test Suite")
    print("=" * 60)
    
    results = []
    for test_file in test_files:
        if test_file.exists():
            success = run_test_file(test_file)
            results.append((test_file.name, success))
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results.append((test_file.name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<40} {status}")
    
    print(f"\nTotal: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total_tests - passed_tests} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())