#!/usr/bin/env python3
"""
Progress monitor for active PRD executions.

Displays real-time progress of parallel PRD execution.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def load_execution_state(project_name: str) -> Dict[str, Any]:
    """Load execution state from project."""
    state_file = Path.home() / ".claude" / "prd-workspace" / project_name / "sandbox" / ".execution_state.json"
    
    if not state_file.exists():
        return None
    
    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except:
        return None

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.0f}m {seconds%60:.0f}s"
    else:
        hours = seconds / 3600
        mins = (seconds % 3600) / 60
        return f"{hours:.0f}h {mins:.0f}m"

def display_progress(project_name: str):
    """Display execution progress."""
    state = load_execution_state(project_name)
    
    if not state:
        print(f"No active execution found for project: {project_name}")
        return
    
    # Calculate statistics
    total_phases = len(state.get("phase_states", {}))
    completed = sum(1 for p in state["phase_states"].values() 
                   if p["status"] == "completed")
    failed = sum(1 for p in state["phase_states"].values() 
                if p["status"] == "failed")
    in_progress = sum(1 for p in state["phase_states"].values() 
                     if p["status"] == "in_progress")
    
    # Calculate progress percentage
    progress = (completed / total_phases * 100) if total_phases > 0 else 0
    
    # Calculate elapsed time
    if state.get("start_time"):
        start = datetime.fromisoformat(state["start_time"])
        elapsed = (datetime.now() - start).total_seconds()
    else:
        elapsed = 0
    
    # Display header
    print(f"PRD Parallel Execution Monitor - {project_name}")
    print("=" * 60)
    print(f"Progress: {progress:.1f}% ({completed}/{total_phases} phases)")
    print(f"Status: {in_progress} running, {completed} complete, {failed} failed")
    print(f"Elapsed: {format_duration(elapsed)}")
    print()
    
    # Find current wave
    current_wave = None
    if "waves" in state:
        for wave in state["waves"]:
            if wave["status"] == "in_progress":
                current_wave = wave["wave_number"]
                break
    
    if current_wave:
        print(f"Current Wave: {current_wave}")
    
    # Display phase status
    print("\nPhase Status:")
    print("-" * 60)
    
    for phase_id, phase_state in sorted(state["phase_states"].items()):
        status = phase_state["status"]
        
        # Status symbols
        symbols = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌"
        }
        
        symbol = symbols.get(status, "?")
        
        # Duration
        if phase_state.get("start_time") and phase_state.get("end_time"):
            start = datetime.fromisoformat(phase_state["start_time"])
            end = datetime.fromisoformat(phase_state["end_time"])
            duration = (end - start).total_seconds()
            duration_str = format_duration(duration)
        elif phase_state.get("start_time") and status == "in_progress":
            start = datetime.fromisoformat(phase_state["start_time"])
            duration = (datetime.now() - start).total_seconds()
            duration_str = f"{format_duration(duration)} (running)"
        else:
            duration_str = "-"
        
        # Error message
        error = phase_state.get("error_message", "")
        if error:
            error = f" - {error[:50]}..."
        
        print(f"{symbol} {phase_id:<30} {status:<12} {duration_str:<15}{error}")
    
    # Check for stop signal
    stop_file = Path.home() / ".claude" / "prd-workspace" / project_name / "sandbox" / ".stop_requested"
    if stop_file.exists():
        print("\n⚠️  STOP REQUESTED - Waiting for current phases to complete...")

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: progress_monitor.py <project-name>")
        sys.exit(1)
    
    project_name = sys.argv[1]
    display_progress(project_name)

if __name__ == "__main__":
    main()