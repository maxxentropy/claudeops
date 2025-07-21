"""
Metrics collection and reporting for parallel PRD execution.

This module collects performance metrics, calculates statistics,
and exports data for analysis and benchmarking.
"""

import json
import csv
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
import psutil
import os

from ..models.execution_state import ExecutionState, PhaseState
from ..models.parallel_execution import ParallelExecution, Wave


@dataclass
class ExecutionMetrics:
    """Comprehensive metrics for a parallel execution."""
    # Time metrics
    start_time: datetime
    end_time: Optional[datetime]
    total_duration_seconds: float
    sequential_estimated_hours: float
    parallel_actual_hours: float
    time_saved_hours: float
    time_saved_percentage: float
    
    # Phase metrics
    total_phases: int
    completed_phases: int
    failed_phases: int
    average_phase_duration: float
    
    # Wave metrics
    total_waves: int
    average_wave_duration: float
    max_wave_duration: float
    wave_parallelism: float  # Average phases per wave
    
    # Resource metrics
    max_concurrent_agents: int
    average_cpu_usage: float
    peak_cpu_usage: float
    average_memory_mb: float
    peak_memory_mb: float
    
    # Lock metrics
    total_lock_requests: int
    average_lock_wait_time: float
    max_lock_wait_time: float
    lock_contention_rate: float
    
    # Efficiency metrics
    parallel_efficiency: float
    resource_utilization: float
    agent_utilization: float
    
    # Failure metrics
    failure_rate: float
    retry_count: int
    recovery_success_rate: float


@dataclass
class PhaseMetrics:
    """Metrics for individual phase execution."""
    phase_id: str
    phase_name: str
    wave_number: int
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: float
    estimated_hours: float
    actual_vs_estimated_ratio: float
    agent_id: str
    resource_locks_held: int
    lock_wait_time: float
    cpu_usage_avg: float
    memory_usage_mb: float
    status: str
    error_message: Optional[str]


class MetricsCollector:
    """Collects and analyzes execution metrics."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize metrics collector.
        
        Args:
            output_dir: Directory for metric exports (creates if needed)
        """
        self.output_dir = output_dir or Path("./metrics")
        self.output_dir.mkdir(exist_ok=True)
        
        # Runtime collection
        self.phase_metrics: List[PhaseMetrics] = []
        self.lock_events: List[Dict[str, Any]] = []
        self.resource_samples: List[Dict[str, Any]] = []
        self.start_time = None
        self.execution_id = None
        
    def start_collection(self, execution_id: str) -> None:
        """Start metrics collection for an execution.
        
        Args:
            execution_id: Unique identifier for this execution
        """
        self.execution_id = execution_id
        self.start_time = datetime.now()
        self.phase_metrics.clear()
        self.lock_events.clear()
        self.resource_samples.clear()
        
    def collect_phase_metrics(self, phase: PhaseState, wave_number: int,
                            agent_id: str, metrics: Dict[str, Any]) -> None:
        """Collect metrics for a completed phase.
        
        Args:
            phase: The phase that completed
            wave_number: Which wave it executed in
            agent_id: Agent that executed it
            metrics: Additional metrics (cpu, memory, locks)
        """
        duration = 0
        if phase.started_at and phase.completed_at:
            duration = (phase.completed_at - phase.started_at).total_seconds()
            
        phase_metric = PhaseMetrics(
            phase_id=phase.phase_id,
            phase_name=phase.name,
            wave_number=wave_number,
            start_time=phase.started_at or datetime.now(),
            end_time=phase.completed_at,
            duration_seconds=duration,
            estimated_hours=phase.estimated_hours,
            actual_vs_estimated_ratio=duration / (phase.estimated_hours * 3600) if phase.estimated_hours > 0 else 1.0,
            agent_id=agent_id,
            resource_locks_held=len(metrics.get('locks', [])),
            lock_wait_time=metrics.get('lock_wait_time', 0),
            cpu_usage_avg=metrics.get('cpu_avg', 0),
            memory_usage_mb=metrics.get('memory_mb', 0),
            status=phase.status.value,
            error_message=phase.error_message
        )
        
        self.phase_metrics.append(phase_metric)
        
    def record_lock_event(self, resource: str, phase_id: str, 
                         event_type: str, wait_time: float = 0) -> None:
        """Record a resource lock event.
        
        Args:
            resource: Resource path
            phase_id: Phase requesting/holding lock
            event_type: 'acquired', 'released', 'waited'
            wait_time: Time waited for lock (if applicable)
        """
        self.lock_events.append({
            'timestamp': datetime.now(),
            'resource': resource,
            'phase_id': phase_id,
            'event_type': event_type,
            'wait_time': wait_time
        })
        
    def sample_resources(self, agents: Dict[str, Any]) -> None:
        """Sample current resource usage.
        
        Args:
            agents: Current agent states
        """
        process = psutil.Process(os.getpid())
        
        self.resource_samples.append({
            'timestamp': datetime.now(),
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'active_agents': sum(1 for a in agents.values() if a.get('status') == 'IN_PROGRESS'),
            'total_agents': len(agents)
        })
        
    def calculate_execution_metrics(self, execution: ParallelExecution,
                                  state: ExecutionState) -> ExecutionMetrics:
        """Calculate comprehensive metrics for the execution.
        
        Args:
            execution: The parallel execution
            state: Final execution state
            
        Returns:
            Complete execution metrics
        """
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Time calculations
        sequential_hours = sum(p.estimated_hours for p in execution.phases.values())
        parallel_hours = total_duration / 3600
        time_saved_hours = sequential_hours - parallel_hours
        time_saved_pct = (time_saved_hours / sequential_hours * 100) if sequential_hours > 0 else 0
        
        # Phase statistics
        completed = [p for p in self.phase_metrics if p.status == "COMPLETED"]
        failed = [p for p in self.phase_metrics if p.status == "FAILED"]
        
        avg_phase_duration = statistics.mean([p.duration_seconds for p in completed]) if completed else 0
        
        # Wave statistics
        wave_durations = self._calculate_wave_durations(execution, self.phase_metrics)
        avg_wave_duration = statistics.mean(wave_durations) if wave_durations else 0
        max_wave_duration = max(wave_durations) if wave_durations else 0
        
        wave_parallelism = statistics.mean([len(w.phase_ids) for w in execution.waves])
        
        # Resource statistics
        if self.resource_samples:
            cpu_samples = [s['cpu_percent'] for s in self.resource_samples]
            memory_samples = [s['memory_mb'] for s in self.resource_samples]
            agent_samples = [s['active_agents'] for s in self.resource_samples]
            
            avg_cpu = statistics.mean(cpu_samples)
            peak_cpu = max(cpu_samples)
            avg_memory = statistics.mean(memory_samples)
            peak_memory = max(memory_samples)
            max_concurrent = max(agent_samples)
        else:
            avg_cpu = peak_cpu = avg_memory = peak_memory = max_concurrent = 0
            
        # Lock statistics
        lock_waits = [e['wait_time'] for e in self.lock_events if e['event_type'] == 'waited']
        avg_lock_wait = statistics.mean(lock_waits) if lock_waits else 0
        max_lock_wait = max(lock_waits) if lock_waits else 0
        
        total_lock_requests = len([e for e in self.lock_events if e['event_type'] in ['acquired', 'waited']])
        lock_contention_rate = len(lock_waits) / total_lock_requests if total_lock_requests > 0 else 0
        
        # Efficiency calculations
        parallel_efficiency = time_saved_pct
        resource_utilization = avg_cpu / 100  # Normalized
        
        # Agent utilization (percentage of time agents were busy)
        if self.resource_samples and max_concurrent > 0:
            busy_samples = [s['active_agents'] / max_concurrent for s in self.resource_samples]
            agent_utilization = statistics.mean(busy_samples) * 100
        else:
            agent_utilization = 0
            
        # Failure statistics
        failure_rate = len(failed) / len(self.phase_metrics) * 100 if self.phase_metrics else 0
        retry_count = sum(1 for p in self.phase_metrics if 'retry' in p.phase_id.lower())
        recovery_success_rate = 0  # Would need retry tracking
        
        return ExecutionMetrics(
            start_time=self.start_time,
            end_time=end_time,
            total_duration_seconds=total_duration,
            sequential_estimated_hours=sequential_hours,
            parallel_actual_hours=parallel_hours,
            time_saved_hours=time_saved_hours,
            time_saved_percentage=time_saved_pct,
            total_phases=len(execution.phases),
            completed_phases=len(completed),
            failed_phases=len(failed),
            average_phase_duration=avg_phase_duration,
            total_waves=len(execution.waves),
            average_wave_duration=avg_wave_duration,
            max_wave_duration=max_wave_duration,
            wave_parallelism=wave_parallelism,
            max_concurrent_agents=max_concurrent,
            average_cpu_usage=avg_cpu,
            peak_cpu_usage=peak_cpu,
            average_memory_mb=avg_memory,
            peak_memory_mb=peak_memory,
            total_lock_requests=total_lock_requests,
            average_lock_wait_time=avg_lock_wait,
            max_lock_wait_time=max_lock_wait,
            lock_contention_rate=lock_contention_rate,
            parallel_efficiency=parallel_efficiency,
            resource_utilization=resource_utilization,
            agent_utilization=agent_utilization,
            failure_rate=failure_rate,
            retry_count=retry_count,
            recovery_success_rate=recovery_success_rate
        )
        
    def export_metrics_csv(self, metrics: ExecutionMetrics, 
                          phase_metrics: Optional[List[PhaseMetrics]] = None) -> Path:
        """Export metrics to CSV format.
        
        Args:
            metrics: Execution metrics
            phase_metrics: Optional phase-level metrics
            
        Returns:
            Path to exported CSV file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export execution summary
        summary_path = self.output_dir / f"execution_summary_{timestamp}.csv"
        with open(summary_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(asdict(metrics).keys()))
            writer.writeheader()
            writer.writerow(asdict(metrics))
            
        # Export phase details if provided
        if phase_metrics or self.phase_metrics:
            phases = phase_metrics or self.phase_metrics
            phases_path = self.output_dir / f"phase_metrics_{timestamp}.csv"
            
            with open(phases_path, 'w', newline='') as f:
                if phases:
                    fieldnames = list(asdict(phases[0]).keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for phase in phases:
                        row = asdict(phase)
                        # Convert datetime objects to strings
                        for key in ['start_time', 'end_time']:
                            if row[key]:
                                row[key] = row[key].isoformat()
                        writer.writerow(row)
                        
        return summary_path
        
    def export_metrics_json(self, metrics: ExecutionMetrics) -> Path:
        """Export metrics to JSON format for dashboards.
        
        Args:
            metrics: Execution metrics
            
        Returns:
            Path to exported JSON file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = self.output_dir / f"execution_metrics_{timestamp}.json"
        
        # Convert to dict and handle datetime objects
        metrics_dict = asdict(metrics)
        for key, value in metrics_dict.items():
            if isinstance(value, datetime):
                metrics_dict[key] = value.isoformat()
                
        # Add phase metrics
        phase_data = []
        for phase in self.phase_metrics:
            phase_dict = asdict(phase)
            for key in ['start_time', 'end_time']:
                if phase_dict[key]:
                    phase_dict[key] = phase_dict[key].isoformat()
            phase_data.append(phase_dict)
            
        full_data = {
            'execution_id': self.execution_id,
            'summary': metrics_dict,
            'phases': phase_data,
            'lock_events': self.lock_events,
            'resource_samples': [
                {**s, 'timestamp': s['timestamp'].isoformat()} 
                for s in self.resource_samples
            ]
        }
        
        with open(json_path, 'w') as f:
            json.dump(full_data, f, indent=2)
            
        return json_path
        
    def generate_report(self, metrics: ExecutionMetrics) -> str:
        """Generate a human-readable metrics report.
        
        Args:
            metrics: Execution metrics
            
        Returns:
            Formatted report string
        """
        report = f"""
Parallel PRD Execution Metrics Report
=====================================
Execution ID: {self.execution_id}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Time Performance
----------------
Total Duration: {metrics.total_duration_seconds / 3600:.2f} hours
Sequential Estimate: {metrics.sequential_estimated_hours:.2f} hours
Time Saved: {metrics.time_saved_hours:.2f} hours ({metrics.time_saved_percentage:.1f}%)
Parallel Efficiency: {metrics.parallel_efficiency:.1f}%

Phase Execution
---------------
Total Phases: {metrics.total_phases}
Completed: {metrics.completed_phases}
Failed: {metrics.failed_phases}
Failure Rate: {metrics.failure_rate:.1f}%
Average Duration: {metrics.average_phase_duration / 60:.1f} minutes

Wave Analysis
-------------
Total Waves: {metrics.total_waves}
Average Parallelism: {metrics.wave_parallelism:.1f} phases/wave
Average Wave Duration: {metrics.average_wave_duration / 60:.1f} minutes
Max Wave Duration: {metrics.max_wave_duration / 60:.1f} minutes

Resource Utilization
--------------------
Max Concurrent Agents: {metrics.max_concurrent_agents}
Agent Utilization: {metrics.agent_utilization:.1f}%
Average CPU Usage: {metrics.average_cpu_usage:.1f}%
Peak CPU Usage: {metrics.peak_cpu_usage:.1f}%
Average Memory: {metrics.average_memory_mb:.1f} MB
Peak Memory: {metrics.peak_memory_mb:.1f} MB

Lock Performance
----------------
Total Lock Requests: {metrics.total_lock_requests}
Average Wait Time: {metrics.average_lock_wait_time:.2f}s
Max Wait Time: {metrics.max_lock_wait_time:.2f}s
Contention Rate: {metrics.lock_contention_rate:.1f}%

Summary
-------
The parallel execution achieved a {metrics.time_saved_percentage:.1f}% reduction in total
execution time compared to sequential processing. Resource utilization averaged
{metrics.resource_utilization * 100:.1f}% with {metrics.max_concurrent_agents} agents working
concurrently.
"""
        return report
        
    def _calculate_wave_durations(self, execution: ParallelExecution,
                                 phase_metrics: List[PhaseMetrics]) -> List[float]:
        """Calculate duration for each wave."""
        wave_durations = []
        
        for i, wave in enumerate(execution.waves):
            wave_phases = [p for p in phase_metrics if p.wave_number == i]
            if wave_phases:
                # Wave duration is from first start to last end
                starts = [p.start_time for p in wave_phases]
                ends = [p.end_time for p in wave_phases if p.end_time]
                
                if starts and ends:
                    duration = (max(ends) - min(starts)).total_seconds()
                    wave_durations.append(duration)
                    
        return wave_durations


# Utility functions
def execution_time_saved(metrics: ExecutionMetrics) -> float:
    """Calculate time saved in hours."""
    return metrics.time_saved_hours


def parallel_efficiency(metrics: ExecutionMetrics) -> float:
    """Calculate parallel efficiency percentage."""
    return metrics.parallel_efficiency


def resource_utilization(metrics: ExecutionMetrics) -> Dict[str, float]:
    """Get resource utilization statistics."""
    return {
        'cpu_average': metrics.average_cpu_usage,
        'cpu_peak': metrics.peak_cpu_usage,
        'memory_average': metrics.average_memory_mb,
        'memory_peak': metrics.peak_memory_mb,
        'agent_utilization': metrics.agent_utilization
    }


def failure_rate(metrics: ExecutionMetrics) -> float:
    """Get failure rate percentage."""
    return metrics.failure_rate


def average_lock_wait_time(metrics: ExecutionMetrics) -> float:
    """Get average lock wait time in seconds."""
    return metrics.average_lock_wait_time