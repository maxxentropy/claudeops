"""
Configuration schema for parallel PRD execution system.

This module defines the configuration options and defaults for controlling
the behavior of the parallel execution system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import os
import json
from pathlib import Path


@dataclass
class ParallelExecutionConfig:
    """
    Configuration for parallel PRD execution.
    
    All configuration options have sensible defaults but can be overridden
    via environment variables or configuration files.
    """
    
    # Agent configuration
    max_parallel_agents: int = 3
    """Maximum number of agents that can run in parallel."""
    
    agent_spawn_delay_seconds: float = 2.0
    """Delay between spawning new agents to avoid resource contention."""
    
    agent_heartbeat_interval_seconds: int = 10
    """How often agents should report their status."""
    
    # Resource locking
    lock_timeout_seconds: int = 300
    """Default timeout for resource locks (5 minutes)."""
    
    lock_retry_attempts: int = 3
    """Number of times to retry acquiring a lock before failing."""
    
    lock_retry_delay_seconds: float = 5.0
    """Delay between lock retry attempts."""
    
    lock_cleanup_interval_seconds: int = 60
    """How often to clean up expired locks."""
    
    # Wave execution
    wave_delay_seconds: int = 5
    """Delay between starting execution waves."""
    
    wave_completion_check_interval_seconds: float = 2.0
    """How often to check if a wave has completed."""
    
    # Conflict resolution
    conflict_retry_attempts: int = 3
    """Number of times to retry on resource conflicts."""
    
    conflict_backoff_base_seconds: float = 1.0
    """Base delay for exponential backoff on conflicts."""
    
    conflict_backoff_max_seconds: float = 30.0
    """Maximum backoff delay for conflict resolution."""
    
    # Monitoring and UI
    monitoring_update_interval_seconds: int = 2
    """How often to update monitoring displays."""
    
    progress_bar_width: int = 40
    """Width of progress bars in terminal UI."""
    
    show_agent_logs: bool = True
    """Whether to display agent logs in real-time."""
    
    log_retention_count: int = 1000
    """Maximum number of log entries to retain per agent."""
    
    # Execution behavior
    fail_fast: bool = False
    """Stop all execution if any phase fails."""
    
    retry_failed_phases: bool = True
    """Whether to automatically retry failed phases."""
    
    max_phase_retries: int = 2
    """Maximum number of times to retry a failed phase."""
    
    continue_on_error: bool = True
    """Continue executing independent phases even if some fail."""
    
    # Performance tuning
    resource_check_interval_ms: int = 100
    """How often to check resource availability (milliseconds)."""
    
    state_persistence_interval_seconds: int = 30
    """How often to persist execution state to disk."""
    
    metrics_collection_enabled: bool = True
    """Whether to collect performance metrics."""
    
    # Paths and storage
    workspace_root: str = field(default_factory=lambda: os.getcwd())
    """Root directory for the workspace."""
    
    state_file_path: Optional[str] = None
    """Path to store execution state (auto-generated if not set)."""
    
    log_directory: Optional[str] = None
    """Directory for log files (auto-generated if not set)."""
    
    def __post_init__(self):
        """Initialize computed fields after dataclass creation."""
        # Auto-generate state file path if not provided
        if self.state_file_path is None:
            self.state_file_path = os.path.join(
                self.workspace_root, 
                ".prd-parallel-state.json"
            )
        
        # Auto-generate log directory if not provided
        if self.log_directory is None:
            self.log_directory = os.path.join(
                self.workspace_root,
                ".prd-parallel-logs"
            )
    
    @classmethod
    def from_env(cls) -> 'ParallelExecutionConfig':
        """
        Create configuration from environment variables.
        
        Environment variables follow the pattern: PRD_PARALLEL_<OPTION_NAME>
        For example: PRD_PARALLEL_MAX_PARALLEL_AGENTS=5
        """
        config_dict = {}
        prefix = "PRD_PARALLEL_"
        
        # Map of config field names to their types
        field_types = {
            'max_parallel_agents': int,
            'agent_spawn_delay_seconds': float,
            'agent_heartbeat_interval_seconds': int,
            'lock_timeout_seconds': int,
            'lock_retry_attempts': int,
            'lock_retry_delay_seconds': float,
            'lock_cleanup_interval_seconds': int,
            'wave_delay_seconds': int,
            'wave_completion_check_interval_seconds': float,
            'conflict_retry_attempts': int,
            'conflict_backoff_base_seconds': float,
            'conflict_backoff_max_seconds': float,
            'monitoring_update_interval_seconds': int,
            'progress_bar_width': int,
            'show_agent_logs': bool,
            'log_retention_count': int,
            'fail_fast': bool,
            'retry_failed_phases': bool,
            'max_phase_retries': int,
            'continue_on_error': bool,
            'resource_check_interval_ms': int,
            'state_persistence_interval_seconds': int,
            'metrics_collection_enabled': bool,
            'workspace_root': str,
            'state_file_path': str,
            'log_directory': str,
        }
        
        for field_name, field_type in field_types.items():
            env_var = prefix + field_name.upper()
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Convert based on type
                if field_type == bool:
                    config_dict[field_name] = value.lower() in ('true', '1', 'yes', 'on')
                elif field_type == int:
                    config_dict[field_name] = int(value)
                elif field_type == float:
                    config_dict[field_name] = float(value)
                else:
                    config_dict[field_name] = value
        
        return cls(**config_dict)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'ParallelExecutionConfig':
        """
        Load configuration from a JSON file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Configuration instance
        """
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        
        return cls(**config_dict)
    
    def to_file(self, file_path: str):
        """
        Save configuration to a JSON file.
        
        Args:
            file_path: Path to save the configuration
        """
        config_dict = self.to_dict()
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'max_parallel_agents': self.max_parallel_agents,
            'agent_spawn_delay_seconds': self.agent_spawn_delay_seconds,
            'agent_heartbeat_interval_seconds': self.agent_heartbeat_interval_seconds,
            'lock_timeout_seconds': self.lock_timeout_seconds,
            'lock_retry_attempts': self.lock_retry_attempts,
            'lock_retry_delay_seconds': self.lock_retry_delay_seconds,
            'lock_cleanup_interval_seconds': self.lock_cleanup_interval_seconds,
            'wave_delay_seconds': self.wave_delay_seconds,
            'wave_completion_check_interval_seconds': self.wave_completion_check_interval_seconds,
            'conflict_retry_attempts': self.conflict_retry_attempts,
            'conflict_backoff_base_seconds': self.conflict_backoff_base_seconds,
            'conflict_backoff_max_seconds': self.conflict_backoff_max_seconds,
            'monitoring_update_interval_seconds': self.monitoring_update_interval_seconds,
            'progress_bar_width': self.progress_bar_width,
            'show_agent_logs': self.show_agent_logs,
            'log_retention_count': self.log_retention_count,
            'fail_fast': self.fail_fast,
            'retry_failed_phases': self.retry_failed_phases,
            'max_phase_retries': self.max_phase_retries,
            'continue_on_error': self.continue_on_error,
            'resource_check_interval_ms': self.resource_check_interval_ms,
            'state_persistence_interval_seconds': self.state_persistence_interval_seconds,
            'metrics_collection_enabled': self.metrics_collection_enabled,
            'workspace_root': self.workspace_root,
            'state_file_path': self.state_file_path,
            'log_directory': self.log_directory,
        }
    
    def validate(self) -> List[str]:
        """
        Validate configuration values.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate numeric ranges
        if self.max_parallel_agents < 1:
            errors.append("max_parallel_agents must be at least 1")
        
        if self.max_parallel_agents > 10:
            errors.append("max_parallel_agents should not exceed 10 for system stability")
        
        if self.lock_timeout_seconds < 10:
            errors.append("lock_timeout_seconds should be at least 10 seconds")
        
        if self.progress_bar_width < 10:
            errors.append("progress_bar_width should be at least 10 characters")
        
        if self.resource_check_interval_ms < 10:
            errors.append("resource_check_interval_ms should be at least 10ms")
        
        # Validate paths
        if self.workspace_root and not os.path.exists(self.workspace_root):
            errors.append(f"workspace_root does not exist: {self.workspace_root}")
        
        # Validate logical constraints
        if self.conflict_backoff_base_seconds > self.conflict_backoff_max_seconds:
            errors.append("conflict_backoff_base_seconds cannot exceed conflict_backoff_max_seconds")
        
        if self.fail_fast and self.continue_on_error:
            errors.append("fail_fast and continue_on_error cannot both be true")
        
        return errors
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the configuration."""
        return f"""Parallel Execution Configuration:
  Agents: {self.max_parallel_agents} max parallel
  Locking: {self.lock_timeout_seconds}s timeout, {self.lock_retry_attempts} retries
  Waves: {self.wave_delay_seconds}s delay between waves
  Behavior: {'Fail fast' if self.fail_fast else 'Continue on error'}
  Retry: {'Enabled' if self.retry_failed_phases else 'Disabled'} (max {self.max_phase_retries} attempts)
  Monitoring: Updates every {self.monitoring_update_interval_seconds}s
  Workspace: {self.workspace_root}"""


# Global default configuration instance
_default_config: Optional[ParallelExecutionConfig] = None


def get_default_config() -> ParallelExecutionConfig:
    """Get the default configuration instance."""
    global _default_config
    if _default_config is None:
        # Try to load from environment first
        _default_config = ParallelExecutionConfig.from_env()
    return _default_config


def set_default_config(config: ParallelExecutionConfig):
    """Set the default configuration instance."""
    global _default_config
    _default_config = config