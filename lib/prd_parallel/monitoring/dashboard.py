"""
Real-time progress dashboard for parallel PRD execution.

This module provides a visual dashboard for monitoring the progress of
parallel PRD execution, including wave progress, agent status, and resource locks.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.align import Align

from ..models.execution_state import ExecutionState, PhaseState, AgentState
from ..models.parallel_execution import Wave, ParallelExecution


class StatusColor(Enum):
    """Colors for different execution states."""
    PENDING = "bright_white"
    IN_PROGRESS = "bright_yellow"
    COMPLETED = "bright_green"
    FAILED = "bright_red"
    BLOCKED = "bright_magenta"


@dataclass
class DashboardMetrics:
    """Metrics displayed on the dashboard."""
    total_phases: int
    completed_phases: int
    in_progress_phases: int
    failed_phases: int
    total_agents: int
    active_agents: int
    estimated_time_remaining: float
    time_saved: float
    parallel_efficiency: float


class ProgressDashboard:
    """Real-time monitoring dashboard for parallel PRD execution."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the dashboard.
        
        Args:
            console: Rich console instance (creates new if not provided)
        """
        self.console = console or Console()
        self.start_time = datetime.now()
        self.metrics = None
        
    def display_execution_overview(self, execution: ParallelExecution) -> Panel:
        """Display high-level execution overview.
        
        Args:
            execution: The parallel execution being monitored
            
        Returns:
            Rich Panel with execution overview
        """
        # Calculate metrics
        metrics = self._calculate_metrics(execution)
        
        # Create overview text
        overview_text = Text()
        overview_text.append(f"Feature: ", style="bold")
        overview_text.append(f"{execution.feature_name}\n", style="bright_cyan")
        overview_text.append(f"Status: ", style="bold")
        overview_text.append(
            f"{execution.status.value}\n", 
            style=StatusColor[execution.status.name].value
        )
        
        # Progress bar
        progress = metrics.completed_phases / metrics.total_phases * 100
        overview_text.append(f"Progress: ", style="bold")
        overview_text.append(f"{progress:.1f}% ", style="bright_green")
        overview_text.append(f"({metrics.completed_phases}/{metrics.total_phases} phases)\n")
        
        # Time information
        overview_text.append(f"Time Elapsed: ", style="bold")
        elapsed = datetime.now() - self.start_time
        overview_text.append(f"{self._format_duration(elapsed.total_seconds())}\n")
        
        overview_text.append(f"Est. Remaining: ", style="bold")
        overview_text.append(f"{self._format_duration(metrics.estimated_time_remaining)}\n")
        
        overview_text.append(f"Time Saved: ", style="bold")
        overview_text.append(
            f"{self._format_duration(metrics.time_saved)} ",
            style="bright_green"
        )
        overview_text.append(f"({metrics.parallel_efficiency:.0f}% efficiency)\n")
        
        return Panel(
            overview_text,
            title="Parallel PRD Execution",
            title_align="left",
            border_style="bright_blue"
        )
    
    def render_wave_progress(self, wave: Wave, wave_number: int, total_waves: int) -> Panel:
        """Render progress for a specific wave.
        
        Args:
            wave: The wave to display
            wave_number: Current wave number
            total_waves: Total number of waves
            
        Returns:
            Rich Panel with wave progress
        """
        # Create wave header
        header = Text()
        header.append(f"Wave {wave_number}/{total_waves}: ", style="bold")
        header.append(f"{wave.name}\n", style="bright_cyan")
        
        # Create phase grid
        phase_panels = []
        for phase_id in wave.phase_ids:
            phase_panel = self._create_phase_panel(phase_id, wave)
            phase_panels.append(phase_panel)
        
        # Arrange phases in a grid
        if len(phase_panels) == 1:
            content = phase_panels[0]
        else:
            # Create a simple grid layout
            content = Text()
            for i, panel in enumerate(phase_panels):
                content.append(str(panel))
                if i < len(phase_panels) - 1:
                    content.append("\n")
        
        return Panel(
            content,
            title=f"Current Wave ({wave_number}/{total_waves})",
            title_align="left",
            border_style="bright_yellow"
        )
    
    def show_agent_status(self, agents: List[AgentState]) -> Table:
        """Display agent status table.
        
        Args:
            agents: List of agent states
            
        Returns:
            Rich Table with agent status
        """
        table = Table(title="Agent Status", show_header=True)
        table.add_column("Agent ID", style="bright_cyan", width=12)
        table.add_column("Phase", style="bright_white", width=20)
        table.add_column("Status", width=15)
        table.add_column("Progress", width=20)
        table.add_column("Duration", style="bright_white", width=15)
        
        for agent in agents:
            status_color = StatusColor[agent.status.name].value
            progress_bar = self._create_mini_progress_bar(agent.progress)
            
            duration = "N/A"
            if agent.started_at:
                elapsed = datetime.now() - agent.started_at
                duration = self._format_duration(elapsed.total_seconds())
            
            table.add_row(
                agent.agent_id,
                agent.phase_id or "Idle",
                Text(agent.status.value, style=status_color),
                progress_bar,
                duration
            )
        
        return table
    
    def display_resource_locks(self, locks: Dict[str, str]) -> Panel:
        """Display current resource locks.
        
        Args:
            locks: Dictionary of resource path to phase ID
            
        Returns:
            Rich Panel with lock information
        """
        if not locks:
            content = Text("No active resource locks", style="dim")
        else:
            content = Text()
            for resource, phase_id in sorted(locks.items()):
                content.append("🔒 ", style="bright_yellow")
                content.append(f"{resource}", style="bright_white")
                content.append(" → ", style="dim")
                content.append(f"{phase_id}\n", style="bright_cyan")
        
        return Panel(
            content,
            title="Resource Locks",
            title_align="left",
            border_style="bright_magenta"
        )
    
    def update_dashboard(self, state: ExecutionState) -> Layout:
        """Update the complete dashboard with current state.
        
        Args:
            state: Current execution state
            
        Returns:
            Rich Layout with complete dashboard
        """
        layout = Layout()
        
        # Main layout structure
        layout.split_column(
            Layout(name="header", size=10),
            Layout(name="body"),
            Layout(name="footer", size=8)
        )
        
        # Split body into left and right
        layout["body"].split_row(
            Layout(name="main", ratio=2),
            Layout(name="sidebar", ratio=1)
        )
        
        # Populate sections
        execution = state.execution
        layout["header"].update(self.display_execution_overview(execution))
        
        # Find current wave
        current_wave = None
        wave_number = 0
        for i, wave in enumerate(execution.waves):
            if any(execution.phases[pid].status.value in ["PENDING", "IN_PROGRESS"] 
                   for pid in wave.phase_ids if pid in execution.phases):
                current_wave = wave
                wave_number = i + 1
                break
        
        if current_wave:
            layout["main"].update(
                self.render_wave_progress(current_wave, wave_number, len(execution.waves))
            )
        else:
            layout["main"].update(
                Panel("All waves completed!", style="bright_green")
            )
        
        # Agent status
        layout["sidebar"].update(self.show_agent_status(list(state.agents.values())))
        
        # Resource locks
        layout["footer"].update(self.display_resource_locks(state.resource_locks))
        
        return layout
    
    def _calculate_metrics(self, execution: ParallelExecution) -> DashboardMetrics:
        """Calculate dashboard metrics from execution state."""
        total_phases = len(execution.phases)
        completed_phases = sum(1 for p in execution.phases.values() 
                              if p.status.value == "COMPLETED")
        in_progress_phases = sum(1 for p in execution.phases.values() 
                                if p.status.value == "IN_PROGRESS")
        failed_phases = sum(1 for p in execution.phases.values() 
                           if p.status.value == "FAILED")
        
        # Calculate time estimates
        total_estimated_time = sum(p.estimated_hours for p in execution.phases.values())
        completed_time = sum(p.estimated_hours for p in execution.phases.values() 
                            if p.status.value == "COMPLETED")
        remaining_time = total_estimated_time - completed_time
        
        # Calculate parallel efficiency
        sequential_time = total_estimated_time
        parallel_time = sum(w.estimated_duration for w in execution.waves)
        time_saved = sequential_time - parallel_time
        efficiency = (time_saved / sequential_time * 100) if sequential_time > 0 else 0
        
        return DashboardMetrics(
            total_phases=total_phases,
            completed_phases=completed_phases,
            in_progress_phases=in_progress_phases,
            failed_phases=failed_phases,
            total_agents=4,  # From config
            active_agents=in_progress_phases,
            estimated_time_remaining=remaining_time * 3600,  # Convert to seconds
            time_saved=time_saved * 3600,
            parallel_efficiency=efficiency
        )
    
    def _create_phase_panel(self, phase_id: str, wave: Wave) -> Text:
        """Create a mini panel for a phase."""
        # This would normally get the phase from execution state
        # For now, create a simple representation
        text = Text()
        text.append(f"📦 {phase_id}\n", style="bright_cyan")
        text.append("Status: ", style="dim")
        text.append("IN_PROGRESS\n", style="bright_yellow")
        text.append("Progress: ", style="dim")
        text.append("████████░░ 80%\n", style="bright_green")
        return text
    
    def _create_mini_progress_bar(self, progress: float) -> Text:
        """Create a mini progress bar."""
        filled = int(progress / 10)
        empty = 10 - filled
        bar = Text()
        bar.append("█" * filled, style="bright_green")
        bar.append("░" * empty, style="dim")
        bar.append(f" {progress}%", style="bright_white")
        return bar
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


def display_completion_summary(execution: ParallelExecution, start_time: datetime) -> Panel:
    """Display final completion summary.
    
    Args:
        execution: Completed execution
        start_time: When execution started
        
    Returns:
        Rich Panel with completion summary
    """
    elapsed = datetime.now() - start_time
    
    # Calculate statistics
    total_phases = len(execution.phases)
    successful_phases = sum(1 for p in execution.phases.values() 
                           if p.status.value == "COMPLETED")
    failed_phases = sum(1 for p in execution.phases.values() 
                       if p.status.value == "FAILED")
    
    # Time calculations
    sequential_time = sum(p.estimated_hours for p in execution.phases.values())
    actual_time = elapsed.total_seconds() / 3600
    time_saved = sequential_time - actual_time
    efficiency = (time_saved / sequential_time * 100) if sequential_time > 0 else 0
    
    # Create summary
    summary = Text()
    summary.append("✅ Execution Complete!\n\n", style="bright_green bold")
    
    summary.append("Results:\n", style="bold")
    summary.append(f"  • Total Phases: {total_phases}\n")
    summary.append(f"  • Successful: {successful_phases}", style="bright_green")
    if failed_phases > 0:
        summary.append(f"  • Failed: {failed_phases}", style="bright_red")
    summary.append("\n\n")
    
    summary.append("Performance:\n", style="bold")
    summary.append(f"  • Sequential Time: {sequential_time:.1f} hours\n")
    summary.append(f"  • Actual Time: {actual_time:.1f} hours\n")
    summary.append(f"  • Time Saved: {time_saved:.1f} hours ", style="bright_green")
    summary.append(f"({efficiency:.0f}% improvement)\n")
    
    return Panel(
        Align.center(summary),
        title="Execution Summary",
        border_style="bright_green",
        padding=(1, 2)
    )