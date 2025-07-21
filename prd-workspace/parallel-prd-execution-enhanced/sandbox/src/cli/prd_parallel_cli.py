#!/usr/bin/env python3
"""
Command-line interface for parallel PRD execution.

This module provides the main entry point for executing PRD phases
in parallel from the command line.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.parallel_orchestrator import ParallelOrchestrator, ExecutionMode
from parsers.phase_parser import PhaseParser
from models.parallel_execution import PhaseInfo
from analyzers.dependency_analyzer import DependencyAnalyzer
from analyzers.wave_calculator import WaveCalculator
from analyzers.conflict_detector import ConflictDetector


class PRDParallelCLI:
    """Command-line interface for parallel PRD execution."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.workspace_root = Path.home() / ".claude" / "prd-workspace"
        self.parser = self._create_parser()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="Execute PRD phases in parallel with intelligent orchestration",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Execute all phases in parallel
  prd-parallel my-project
  
  # Dry run to see execution plan
  prd-parallel my-project --dry-run
  
  # Resume from saved state
  prd-parallel my-project --resume
  
  # Limit concurrent agents
  prd-parallel my-project --max-agents 3
  
  # Validate dependencies only
  prd-parallel my-project --validate
            """
        )
        
        parser.add_argument(
            "project",
            help="Name of the PRD project to execute"
        )
        
        parser.add_argument(
            "--max-agents",
            type=int,
            default=5,
            help="Maximum number of concurrent agents (default: 5)"
        )
        
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show execution plan without running"
        )
        
        parser.add_argument(
            "--resume",
            action="store_true",
            help="Resume from saved execution state"
        )
        
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate dependencies without executing"
        )
        
        parser.add_argument(
            "--watch",
            action="store_true",
            help="Watch execution progress in real-time"
        )
        
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results in JSON format"
        )
        
        parser.add_argument(
            "--timeout",
            type=int,
            default=3600,
            help="Phase timeout in seconds (default: 3600)"
        )
        
        parser.add_argument(
            "--retry-limit",
            type=int,
            default=2,
            help="Number of retries for failed phases (default: 2)"
        )
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI with given arguments.
        
        Args:
            args: Command line arguments (None uses sys.argv)
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        parsed_args = self.parser.parse_args(args)
        
        try:
            # Load project
            project_path = self.workspace_root / parsed_args.project
            if not project_path.exists():
                print(f"Error: Project '{parsed_args.project}' not found")
                return 1
            
            # Load phases
            phases = self._load_phases(project_path)
            if not phases:
                print("Error: No phases found in project")
                return 1
            
            # Configure orchestrator
            config = {
                "max_agents": parsed_args.max_agents,
                "phase_timeout_seconds": parsed_args.timeout,
                "retry_limit": parsed_args.retry_limit,
            }
            
            orchestrator = ParallelOrchestrator(
                str(project_path / "sandbox"),
                config
            )
            
            # Set up callbacks for progress monitoring
            if parsed_args.watch and not parsed_args.json:
                self._setup_progress_callbacks(orchestrator)
            
            # Determine execution mode
            if parsed_args.validate:
                mode = ExecutionMode.VALIDATE
            elif parsed_args.dry_run:
                mode = ExecutionMode.DRY_RUN
            elif parsed_args.resume:
                mode = ExecutionMode.RESUME
            else:
                mode = ExecutionMode.NORMAL
            
            # Execute
            print(f"\nExecuting PRD: {parsed_args.project}")
            print(f"Mode: {mode.value}")
            print(f"Phases: {len(phases)}")
            print(f"Max agents: {parsed_args.max_agents}")
            print("-" * 50)
            
            result = orchestrator.execute_prd(phases, mode)
            
            # Output results
            if parsed_args.json:
                self._output_json(result)
            else:
                self._output_summary(result)
            
            return 0 if result.success else 1
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted by user")
            return 130
        except Exception as e:
            print(f"\nError: {str(e)}")
            if parsed_args.json:
                print(json.dumps({"error": str(e)}))
            return 1
    
    def _load_phases(self, project_path: Path) -> List[PhaseInfo]:
        """Load phase specifications from project directory."""
        phases = []
        phase_files = sorted(project_path.glob("phase-*.md"))
        
        parser = PhaseParser()
        for phase_file in phase_files:
            try:
                phase = parser.parse_phase_file(str(phase_file))
                phases.append(phase)
            except Exception as e:
                print(f"Warning: Failed to parse {phase_file.name}: {e}")
        
        return phases
    
    def _setup_progress_callbacks(self, orchestrator: ParallelOrchestrator):
        """Set up callbacks for progress monitoring."""
        
        def on_phase_start(phase_id: str, phase_info: PhaseInfo):
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Starting {phase_id}: {phase_info.name}")
        
        def on_phase_complete(phase_id: str, success: bool):
            timestamp = datetime.now().strftime("%H:%M:%S")
            status = "✓ COMPLETE" if success else "✗ FAILED"
            print(f"[{timestamp}] {phase_id}: {status}")
        
        def on_wave_complete(wave_num: int, result):
            print(f"\nWave {wave_num} complete: "
                  f"{result.completed_phases}/{result.total_phases} phases succeeded")
        
        orchestrator.on_phase_start = on_phase_start
        orchestrator.on_phase_complete = on_phase_complete
        orchestrator.on_wave_complete = on_wave_complete
    
    def _output_json(self, result):
        """Output execution result as JSON."""
        output = {
            "success": result.success,
            "mode": result.mode.value,
            "duration_seconds": result.total_duration_seconds,
            "phases": {
                "total": result.total_phases,
                "completed": result.completed_phases,
                "failed": result.failed_phases
            },
            "waves_executed": result.waves_executed,
            "phase_results": result.phase_results,
            "errors": result.errors
        }
        print(json.dumps(output, indent=2))
    
    def _output_summary(self, result):
        """Output human-readable execution summary."""
        print("\n" + "=" * 50)
        print("EXECUTION SUMMARY")
        print("=" * 50)
        
        print(f"\nResult: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"Duration: {result.total_duration_seconds:.1f} seconds")
        print(f"Phases: {result.completed_phases}/{result.total_phases} completed")
        
        if result.failed_phases > 0:
            print(f"Failed phases: {result.failed_phases}")
        
        print(f"Waves executed: {result.waves_executed}")
        
        if result.phase_results:
            print("\nPhase Details:")
            for phase_id, details in result.phase_results.items():
                status_symbol = "✓" if details["status"] == "completed" else "✗"
                print(f"  {status_symbol} {phase_id}: {details['status']} "
                      f"({details['duration']:.1f}s)")
                if details.get("error"):
                    print(f"    Error: {details['error']}")
        
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")
        
        # Calculate time savings for parallel execution
        if result.mode == ExecutionMode.NORMAL and result.success:
            sequential_time = sum(
                details["duration"] 
                for details in result.phase_results.values()
            )
            time_saved = sequential_time - result.total_duration_seconds
            if time_saved > 0:
                efficiency = (time_saved / sequential_time) * 100
                print(f"\nTime saved: {time_saved:.1f}s ({efficiency:.1f}% faster)")


def main():
    """Main entry point."""
    cli = PRDParallelCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()