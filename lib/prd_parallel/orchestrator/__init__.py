"""
Orchestration components for parallel PRD execution.

This package provides the core orchestration functionality for executing
PRD phases in parallel with proper coordination and monitoring.
"""

from orchestrator.agent_spawner import AgentSpawner, AgentProcess, AgentStatus
from orchestrator.wave_executor import WaveExecutor, WaveResult, RecoveryAction
from orchestrator.resource_coordinator import ResourceCoordinator, ResourceConflict, Deadlock
from orchestrator.state_manager import StateManager
from orchestrator.parallel_orchestrator import (
    ParallelOrchestrator, 
    ExecutionMode, 
    ExecutionResult, 
    ProgressReport
)

__all__ = [
    # Agent spawner
    'AgentSpawner',
    'AgentProcess', 
    'AgentStatus',
    
    # Wave executor
    'WaveExecutor',
    'WaveResult',
    'RecoveryAction',
    
    # Resource coordinator
    'ResourceCoordinator',
    'ResourceConflict',
    'Deadlock',
    
    # State manager
    'StateManager',
    
    # Main orchestrator
    'ParallelOrchestrator',
    'ExecutionMode',
    'ExecutionResult',
    'ProgressReport'
]