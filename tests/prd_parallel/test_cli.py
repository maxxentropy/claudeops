"""
Tests for command-line interfaces.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cli.prd_parallel_cli import PRDParallelCLI
from cli.prd_analyze_cli import PRDAnalyzeCLI
from models.parallel_execution import PhaseInfo


class TestPRDParallelCLI(unittest.TestCase):
    """Test cases for parallel execution CLI."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir) / ".claude" / "prd-workspace"
        self.project_dir = self.workspace / "test-project"
        self.project_dir.mkdir(parents=True)
        
        # Create test phase files
        self._create_test_phases()
        
        # Patch home directory
        self.home_patcher = patch('pathlib.Path.home')
        mock_home = self.home_patcher.start()
        mock_home.return_value = Path(self.temp_dir)
        
        self.cli = PRDParallelCLI()
    
    def tearDown(self):
        """Clean up test environment."""
        self.home_patcher.stop()
        shutil.rmtree(self.temp_dir)
    
    def _create_test_phases(self):
        """Create test phase files."""
        phases = [
            {
                "id": "phase-1-setup",
                "content": """# Phase 1: Setup
                
## Objective
Set up foundation

## Dependencies
None

## Outputs
- /src/config.py
- /src/models.py

## Estimated Time
2.0 hours
"""
            },
            {
                "id": "phase-2-api",
                "content": """# Phase 2: API

## Objective
Build API layer

## Dependencies
- phase-1-setup

## Outputs
- /src/api/endpoints.py

## Estimated Time
3.0 hours
"""
            }
        ]
        
        for phase in phases:
            phase_file = self.project_dir / f"{phase['id']}.md"
            phase_file.write_text(phase['content'])
    
    def test_basic_execution(self):
        """Test basic parallel execution."""
        with patch('cli.prd_parallel_cli.ParallelOrchestrator') as mock_orchestrator:
            # Mock the orchestrator
            instance = mock_orchestrator.return_value
            instance.execute_prd.return_value = MagicMock(
                success=True,
                mode=MagicMock(value='normal'),
                total_duration_seconds=120.5,
                total_phases=2,
                completed_phases=2,
                failed_phases=0,
                waves_executed=2,
                phase_results={},
                errors=[]
            )
            
            # Run CLI
            result = self.cli.run(['test-project'])
            
            # Verify
            self.assertEqual(result, 0)
            mock_orchestrator.assert_called_once()
            instance.execute_prd.assert_called_once()
    
    def test_dry_run(self):
        """Test dry run mode."""
        with patch('cli.prd_parallel_cli.ParallelOrchestrator') as mock_orchestrator:
            instance = mock_orchestrator.return_value
            instance.execute_prd.return_value = MagicMock(
                success=True,
                mode=MagicMock(value='dry_run'),
                total_duration_seconds=0,
                total_phases=2,
                completed_phases=0,
                failed_phases=0,
                waves_executed=0,
                phase_results={},
                errors=[]
            )
            
            # Run CLI with dry-run
            result = self.cli.run(['test-project', '--dry-run'])
            
            # Verify
            self.assertEqual(result, 0)
            # Check that dry run mode was used
            args, kwargs = instance.execute_prd.call_args
            self.assertEqual(args[1].value, 'dry_run')
    
    def test_json_output(self):
        """Test JSON output format."""
        with patch('cli.prd_parallel_cli.ParallelOrchestrator') as mock_orchestrator:
            instance = mock_orchestrator.return_value
            instance.execute_prd.return_value = MagicMock(
                success=True,
                mode=MagicMock(value='normal'),
                total_duration_seconds=120.5,
                total_phases=2,
                completed_phases=2,
                failed_phases=0,
                waves_executed=2,
                phase_results={"phase-1": {"status": "completed", "duration": 60}},
                errors=[]
            )
            
            # Capture output
            with patch('builtins.print') as mock_print:
                result = self.cli.run(['test-project', '--json'])
                
                # Verify JSON was printed
                self.assertEqual(result, 0)
                # Get the printed JSON
                json_output = mock_print.call_args[0][0]
                data = json.loads(json_output)
                
                self.assertTrue(data['success'])
                self.assertEqual(data['phases']['total'], 2)
                self.assertEqual(data['phases']['completed'], 2)
    
    def test_project_not_found(self):
        """Test handling of missing project."""
        result = self.cli.run(['non-existent-project'])
        self.assertEqual(result, 1)
    
    def test_max_agents_option(self):
        """Test max agents configuration."""
        with patch('cli.prd_parallel_cli.ParallelOrchestrator') as mock_orchestrator:
            instance = mock_orchestrator.return_value
            instance.execute_prd.return_value = MagicMock(
                success=True,
                mode=MagicMock(value='normal'),
                total_duration_seconds=120,
                total_phases=2,
                completed_phases=2,
                failed_phases=0,
                waves_executed=1,
                phase_results={},
                errors=[]
            )
            
            # Run with custom max agents
            result = self.cli.run(['test-project', '--max-agents', '3'])
            
            # Verify configuration was passed
            self.assertEqual(result, 0)
            args, kwargs = mock_orchestrator.call_args
            self.assertEqual(kwargs['config']['max_agents'], 3)


class TestPRDAnalyzeCLI(unittest.TestCase):
    """Test cases for analysis CLI."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir) / ".claude" / "prd-workspace"
        self.project_dir = self.workspace / "test-project"
        self.project_dir.mkdir(parents=True)
        
        # Create test phase files
        self._create_test_phases()
        
        # Patch home directory
        self.home_patcher = patch('pathlib.Path.home')
        mock_home = self.home_patcher.start()
        mock_home.return_value = Path(self.temp_dir)
        
        self.cli = PRDAnalyzeCLI()
    
    def tearDown(self):
        """Clean up test environment."""
        self.home_patcher.stop()
        shutil.rmtree(self.temp_dir)
    
    def _create_test_phases(self):
        """Create test phase files."""
        phases = [
            {
                "id": "phase-1-setup",
                "content": """# Phase 1: Setup
                
## Objective
Set up foundation

## Dependencies
None

## Outputs
- /src/config.py

## Estimated Time
2.0 hours
"""
            },
            {
                "id": "phase-2-api",
                "content": """# Phase 2: API

## Objective
Build API layer

## Dependencies
- phase-1-setup

## Outputs
- /src/api/endpoints.py

## Estimated Time
3.0 hours
"""
            },
            {
                "id": "phase-3-frontend",
                "content": """# Phase 3: Frontend

## Objective
Build frontend

## Dependencies
- phase-1-setup

## Outputs
- /frontend/app.js

## Estimated Time
4.0 hours
"""
            }
        ]
        
        for phase in phases:
            phase_file = self.project_dir / f"{phase['id']}.md"
            phase_file.write_text(phase['content'])
    
    def test_basic_analysis(self):
        """Test basic dependency analysis."""
        with patch('builtins.print') as mock_print:
            result = self.cli.run(['test-project'])
            
            # Verify success
            self.assertEqual(result, 0)
            
            # Check that analysis was printed
            output = '\n'.join(str(call[0][0]) if call[0] else '' 
                             for call in mock_print.call_args_list)
            self.assertIn('PRD Analysis Summary', output)
            self.assertIn('Phases: 3', output)
            self.assertIn('Execution Waves:', output)
    
    def test_json_output(self):
        """Test JSON output format."""
        with patch('builtins.print') as mock_print:
            result = self.cli.run(['test-project', '--json'])
            
            # Verify success
            self.assertEqual(result, 0)
            
            # Get JSON output
            json_output = mock_print.call_args[0][0]
            data = json.loads(json_output)
            
            # Verify structure
            self.assertIn('phases', data)
            self.assertIn('waves', data)
            self.assertIn('metrics', data)
            self.assertIn('conflicts', data)
            self.assertEqual(len(data['phases']), 3)
    
    def test_report_generation(self):
        """Test markdown report generation."""
        with patch('builtins.print') as mock_print:
            result = self.cli.run(['test-project', '--report'])
            
            # Verify success
            self.assertEqual(result, 0)
            
            # Check report content
            output = '\n'.join(str(call[0][0]) if call[0] else '' 
                             for call in mock_print.call_args_list)
            self.assertIn('# PRD Dependency Analysis Report', output)
            self.assertIn('## Executive Summary', output)
            self.assertIn('## Phase Dependencies', output)
            self.assertIn('## Execution Waves', output)
    
    def test_graph_generation(self):
        """Test visual graph generation."""
        result = self.cli.run(['test-project', '--graph'])
        
        # Verify success
        self.assertEqual(result, 0)
        
        # Check that graph file was created
        graph_file = self.project_dir / "dependency-graph.html"
        self.assertTrue(graph_file.exists())
        
        # Verify HTML content
        content = graph_file.read_text()
        self.assertIn('PRD Dependency Graph', content)
        self.assertIn('vis.Network', content)
    
    def test_conflict_check(self):
        """Test specific conflict checking."""
        with patch('builtins.print') as mock_print:
            result = self.cli.run(['test-project', '--check', 'conflicts'])
            
            # Verify success
            self.assertEqual(result, 0)
            
            # Check output
            output = '\n'.join(str(call[0][0]) if call[0] else '' 
                             for call in mock_print.call_args_list)
            self.assertIn('CONFLICTS CHECK', output)
    
    def test_critical_path_check(self):
        """Test critical path analysis."""
        with patch('builtins.print') as mock_print:
            result = self.cli.run(['test-project', '--check', 'critical-path'])
            
            # Verify success
            self.assertEqual(result, 0)
            
            # Check output
            output = '\n'.join(str(call[0][0]) if call[0] else '' 
                             for call in mock_print.call_args_list)
            self.assertIn('CRITICAL-PATH CHECK', output)
            self.assertIn('Critical path length:', output)


class TestShellIntegration(unittest.TestCase):
    """Test shell integration functionality."""
    
    def test_shell_script_exists(self):
        """Test that shell integration script exists."""
        script_path = Path(__file__).parent.parent / "cli" / "shell_integration.sh"
        self.assertTrue(script_path.exists())
    
    def test_progress_monitor_exists(self):
        """Test that progress monitor script exists."""
        script_path = Path(__file__).parent.parent / "cli" / "progress_monitor.py"
        self.assertTrue(script_path.exists())


if __name__ == '__main__':
    unittest.main()