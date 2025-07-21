"""
Rich terminal interface for monitoring parallel PRD execution.

This module provides an interactive terminal UI with real-time updates,
keyboard shortcuts, and multi-pane layout for comprehensive monitoring.
"""

import asyncio
import threading
from typing import Optional, Dict, List, Callable, Any
from datetime import datetime
import time
from queue import Queue
import sys

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.columns import Columns
from rich.prompt import Prompt, Confirm
from pynput import keyboard

from .dashboard import ProgressDashboard, display_completion_summary
from ..models.execution_state import ExecutionState, ExecutionStatus
from ..orchestrator.parallel_orchestrator import ParallelOrchestrator


class ParallelExecutionUI:
    """Interactive terminal UI for parallel PRD execution monitoring."""
    
    def __init__(self, orchestrator: ParallelOrchestrator):
        """Initialize the terminal UI.
        
        Args:
            orchestrator: The orchestrator to monitor
        """
        self.orchestrator = orchestrator
        self.console = Console()
        self.dashboard = ProgressDashboard(self.console)
        self.live = None
        self.is_running = False
        self.is_paused = False
        self.update_interval = 2.0  # seconds
        self.log_queue = Queue(maxsize=100)
        self.start_time = None
        self.keyboard_listener = None
        
        # UI state
        self.show_logs = True
        self.show_details = False
        self.selected_agent = None
        
    def start_monitoring(self) -> None:
        """Start the monitoring UI in a separate thread."""
        if self.is_running:
            return
            
        self.is_running = True
        self.start_time = datetime.now()
        
        # Start keyboard listener
        self._setup_keyboard_shortcuts()
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=self._run_monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
    def stop_monitoring(self) -> None:
        """Stop the monitoring UI."""
        self.is_running = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.live:
            self.live.stop()
            
    def update_agent_panel(self, agents: List[Dict[str, Any]]) -> Panel:
        """Update the agent status panel.
        
        Args:
            agents: List of agent information
            
        Returns:
            Rich Panel with agent details
        """
        table = Table(show_header=True, header_style="bold bright_cyan")
        table.add_column("Agent", style="bright_white", width=10)
        table.add_column("Phase", style="bright_yellow", width=25)
        table.add_column("Status", width=12)
        table.add_column("Progress", width=15)
        table.add_column("CPU", style="bright_green", width=8)
        table.add_column("Memory", style="bright_blue", width=10)
        
        for agent in agents:
            status_style = self._get_status_style(agent['status'])
            progress_bar = self._create_progress_bar(agent.get('progress', 0))
            
            table.add_row(
                agent['id'],
                agent.get('phase', 'Idle')[:25],
                Text(agent['status'], style=status_style),
                progress_bar,
                f"{agent.get('cpu', 0):.1f}%",
                f"{agent.get('memory', 0):.1f}MB"
            )
            
        return Panel(
            table,
            title="Agent Status",
            title_align="left",
            border_style="bright_cyan"
        )
        
    def update_wave_panel(self, waves: List[Dict[str, Any]]) -> Panel:
        """Update the wave progress panel.
        
        Args:
            waves: List of wave information
            
        Returns:
            Rich Panel with wave progress
        """
        content = Text()
        
        for i, wave in enumerate(waves):
            # Wave header
            wave_status = wave['status']
            status_icon = self._get_status_icon(wave_status)
            status_style = self._get_status_style(wave_status)
            
            content.append(f"{status_icon} Wave {i+1}: ", style="bold")
            content.append(f"{wave['name']}\n", style=status_style)
            
            # Phase details
            for phase in wave.get('phases', []):
                phase_status = phase['status']
                phase_icon = self._get_status_icon(phase_status)
                phase_style = self._get_status_style(phase_status)
                
                content.append(f"    {phase_icon} ", style=phase_style)
                content.append(f"{phase['id']}: ", style="bright_white")
                content.append(f"{phase['status']}", style=phase_style)
                
                if phase['status'] == 'IN_PROGRESS':
                    content.append(f" ({phase.get('progress', 0)}%)", style="dim")
                    
                content.append("\n")
                
            content.append("\n")
            
        return Panel(
            content,
            title="Wave Progress",
            title_align="left",
            border_style="bright_yellow"
        )
        
    def display_error(self, error: str) -> None:
        """Display an error message.
        
        Args:
            error: Error message to display
        """
        self.log_queue.put({
            'timestamp': datetime.now(),
            'level': 'ERROR',
            'message': error
        })
        
    def show_completion_summary(self) -> None:
        """Display the final completion summary."""
        if not self.orchestrator or not self.start_time:
            return
            
        # Get final execution state
        state = self.orchestrator.state_manager.get_state()
        execution = state.execution
        
        # Stop live display
        if self.live:
            self.live.stop()
            
        # Display summary
        summary = display_completion_summary(execution, self.start_time)
        self.console.print(summary)
        
    def _run_monitor_loop(self) -> None:
        """Main monitoring loop."""
        with Live(
            self._create_layout(),
            console=self.console,
            refresh_per_second=1,
            screen=True
        ) as live:
            self.live = live
            
            while self.is_running:
                if not self.is_paused:
                    try:
                        # Update the display
                        live.update(self._create_layout())
                    except Exception as e:
                        self.display_error(f"UI update error: {str(e)}")
                        
                time.sleep(1.0 / self.update_interval)
                
        # Show completion summary when done
        if self.orchestrator:
            state = self.orchestrator.state_manager.get_state()
            if state.execution.status == ExecutionStatus.COMPLETED:
                self.show_completion_summary()
                
    def _create_layout(self) -> Layout:
        """Create the main UI layout."""
        layout = Layout()
        
        # Get current state
        state = self.orchestrator.state_manager.get_state()
        
        # Main structure
        layout.split_column(
            Layout(name="header", size=12),
            Layout(name="main", ratio=2),
            Layout(name="footer", size=10)
        )
        
        # Split main into panels
        layout["main"].split_row(
            Layout(name="waves", ratio=1),
            Layout(name="agents", ratio=1)
        )
        
        # Header - execution overview
        layout["header"].update(
            self.dashboard.display_execution_overview(state.execution)
        )
        
        # Waves panel
        waves_data = self._get_waves_data(state)
        layout["waves"].update(self.update_wave_panel(waves_data))
        
        # Agents panel
        agents_data = self._get_agents_data(state)
        layout["agents"].update(self.update_agent_panel(agents_data))
        
        # Footer - logs or resource locks
        if self.show_logs:
            layout["footer"].update(self._create_log_panel())
        else:
            layout["footer"].update(
                self.dashboard.display_resource_locks(state.resource_locks)
            )
            
        # Add keyboard shortcuts help
        layout = self._add_help_overlay(layout)
        
        return layout
        
    def _create_log_panel(self) -> Panel:
        """Create the log panel."""
        logs = []
        
        # Get recent logs from queue
        while not self.log_queue.empty() and len(logs) < 8:
            try:
                log = self.log_queue.get_nowait()
                logs.append(log)
            except:
                break
                
        # Format logs
        content = Text()
        for log in logs[-8:]:  # Show last 8 logs
            timestamp = log['timestamp'].strftime("%H:%M:%S")
            level = log['level']
            message = log['message']
            
            level_style = {
                'INFO': 'bright_white',
                'WARNING': 'bright_yellow',
                'ERROR': 'bright_red',
                'SUCCESS': 'bright_green'
            }.get(level, 'white')
            
            content.append(f"[{timestamp}] ", style="dim")
            content.append(f"{level}: ", style=level_style)
            content.append(f"{message}\n", style="white")
            
        return Panel(
            content,
            title="Logs (Press 'L' to toggle)",
            title_align="left",
            border_style="bright_blue"
        )
        
    def _add_help_overlay(self, layout: Layout) -> Layout:
        """Add keyboard shortcuts help overlay."""
        help_text = Text()
        help_text.append("Keyboard Shortcuts: ", style="bold bright_cyan")
        help_text.append("P", style="bold bright_yellow")
        help_text.append("ause  ")
        help_text.append("Q", style="bold bright_yellow")
        help_text.append("uit  ")
        help_text.append("L", style="bold bright_yellow")
        help_text.append("ogs  ")
        help_text.append("D", style="bold bright_yellow")
        help_text.append("etails  ")
        help_text.append("R", style="bold bright_yellow")
        help_text.append("efresh")
        
        # Add help as a small overlay
        help_panel = Panel(
            Align.center(help_text),
            style="on grey23",
            height=3
        )
        
        # This would normally be positioned as an overlay
        # For simplicity, we'll add it to the header
        return layout
        
    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for UI control."""
        def on_press(key):
            try:
                if hasattr(key, 'char'):
                    if key.char == 'p':
                        self.is_paused = not self.is_paused
                        self.log_queue.put({
                            'timestamp': datetime.now(),
                            'level': 'INFO',
                            'message': f"Execution {'paused' if self.is_paused else 'resumed'}"
                        })
                    elif key.char == 'q':
                        self.console.print("\n[bright_yellow]Stopping execution...[/]")
                        self.stop_monitoring()
                        self.orchestrator.abort_execution()
                    elif key.char == 'l':
                        self.show_logs = not self.show_logs
                    elif key.char == 'd':
                        self.show_details = not self.show_details
                    elif key.char == 'r':
                        self.update_interval = 0.5 if self.update_interval == 2.0 else 2.0
            except Exception:
                pass
                
        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()
        
    def _get_waves_data(self, state: ExecutionState) -> List[Dict[str, Any]]:
        """Extract wave data from execution state."""
        waves_data = []
        
        for wave in state.execution.waves:
            wave_phases = []
            wave_status = "COMPLETED"
            
            for phase_id in wave.phase_ids:
                if phase_id in state.execution.phases:
                    phase = state.execution.phases[phase_id]
                    phase_data = {
                        'id': phase_id,
                        'status': phase.status.value,
                        'progress': getattr(phase, 'progress', 0)
                    }
                    wave_phases.append(phase_data)
                    
                    if phase.status.value == "IN_PROGRESS":
                        wave_status = "IN_PROGRESS"
                    elif phase.status.value == "PENDING" and wave_status != "IN_PROGRESS":
                        wave_status = "PENDING"
                        
            waves_data.append({
                'name': wave.name,
                'status': wave_status,
                'phases': wave_phases
            })
            
        return waves_data
        
    def _get_agents_data(self, state: ExecutionState) -> List[Dict[str, Any]]:
        """Extract agent data from execution state."""
        agents_data = []
        
        for agent in state.agents.values():
            agent_data = {
                'id': agent.agent_id,
                'status': agent.status.value,
                'phase': agent.phase_id or "Idle",
                'progress': agent.progress,
                'cpu': 15.2,  # Mock data - would be real metrics
                'memory': 256.8  # Mock data - would be real metrics
            }
            agents_data.append(agent_data)
            
        return agents_data
        
    def _get_status_style(self, status: str) -> str:
        """Get style for status text."""
        return {
            'PENDING': 'bright_white',
            'IN_PROGRESS': 'bright_yellow',
            'COMPLETED': 'bright_green',
            'FAILED': 'bright_red',
            'BLOCKED': 'bright_magenta'
        }.get(status, 'white')
        
    def _get_status_icon(self, status: str) -> str:
        """Get icon for status."""
        return {
            'PENDING': '⏸',
            'IN_PROGRESS': '▶',
            'COMPLETED': '✓',
            'FAILED': '✗',
            'BLOCKED': '⚠'
        }.get(status, '•')
        
    def _create_progress_bar(self, progress: float) -> Text:
        """Create a mini progress bar."""
        filled = int(progress / 10)
        empty = 10 - filled
        
        bar = Text()
        bar.append("█" * filled, style="bright_green")
        bar.append("░" * empty, style="dim")
        bar.append(f" {progress}%", style="bright_white")
        
        return bar


# Utility functions for standalone usage
def monitor_execution(orchestrator: ParallelOrchestrator) -> None:
    """Monitor a parallel execution with the terminal UI.
    
    Args:
        orchestrator: The orchestrator to monitor
    """
    ui = ParallelExecutionUI(orchestrator)
    ui.start_monitoring()
    
    try:
        # Wait for execution to complete
        while orchestrator.is_running():
            time.sleep(1)
    except KeyboardInterrupt:
        ui.console.print("\n[bright_yellow]Execution interrupted by user[/]")
    finally:
        ui.stop_monitoring()


async def monitor_execution_async(orchestrator: ParallelOrchestrator) -> None:
    """Async version of execution monitoring.
    
    Args:
        orchestrator: The orchestrator to monitor
    """
    ui = ParallelExecutionUI(orchestrator)
    ui.start_monitoring()
    
    try:
        # Wait for execution to complete
        while orchestrator.is_running():
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        ui.console.print("\n[bright_yellow]Execution cancelled[/]")
    finally:
        ui.stop_monitoring()