"""
Monitoring components for parallel PRD execution.

This module provides real-time monitoring, metrics collection,
and terminal UI for tracking parallel execution progress.
"""

from .dashboard import ProgressDashboard, display_completion_summary
from .terminal_ui import ParallelExecutionUI, monitor_execution, monitor_execution_async
from .metrics_collector import (
    MetricsCollector,
    ExecutionMetrics,
    PhaseMetrics,
    execution_time_saved,
    parallel_efficiency,
    resource_utilization,
    failure_rate,
    average_lock_wait_time
)

__all__ = [
    # Dashboard
    'ProgressDashboard',
    'display_completion_summary',
    
    # Terminal UI
    'ParallelExecutionUI',
    'monitor_execution',
    'monitor_execution_async',
    
    # Metrics
    'MetricsCollector',
    'ExecutionMetrics',
    'PhaseMetrics',
    'execution_time_saved',
    'parallel_efficiency',
    'resource_utilization',
    'failure_rate',
    'average_lock_wait_time'
]