"""
Agent spawning and lifecycle management for parallel PRD execution.

This module handles spawning Claude agents as subprocesses, monitoring their
health, collecting logs, and ensuring graceful shutdown.
"""

import os
import subprocess
import json
import tempfile
import threading
import queue
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from models.execution_state import AgentStatus, AgentInfo


class AgentCommandType(Enum):
    """Types of commands that can be sent to agents."""
    EXECUTE_PHASE = "execute_phase"
    HEALTH_CHECK = "health_check"
    TERMINATE = "terminate"
    STATUS_UPDATE = "status_update"


@dataclass
class AgentCommand:
    """Command to send to an agent process."""
    command_type: AgentCommandType
    payload: Dict[str, Any]
    response_timeout: int = 300  # 5 minutes default


@dataclass
class AgentResponse:
    """Response from an agent process."""
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class LogEntry:
    """Single log entry from an agent."""
    timestamp: datetime
    level: str  # info, warning, error, debug
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "metadata": self.metadata
        }


class AgentProcess:
    """
    Wrapper for a Claude agent subprocess.
    
    Handles communication with the agent via files and monitors its health.
    """
    
    def __init__(self, agent_id: str, phase_info: Dict[str, Any], 
                 workspace: str, config: Dict[str, Any]):
        """
        Initialize an agent process.
        
        Args:
            agent_id: Unique identifier for this agent
            phase_info: Information about the phase to execute
            workspace: Path to the shared workspace
            config: Configuration for the agent
        """
        self.agent_id = agent_id
        self.phase_info = phase_info
        self.workspace = Path(workspace)
        self.config = config
        
        # Create agent-specific directories
        self.agent_dir = self.workspace / "agents" / agent_id
        self.agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Communication files
        self.command_file = self.agent_dir / "command.json"
        self.response_file = self.agent_dir / "response.json"
        self.log_file = self.agent_dir / "agent.log"
        self.state_file = self.agent_dir / "state.json"
        
        # Process management
        self.process: Optional[subprocess.Popen] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Thread-safe log collection
        self.log_queue: queue.Queue[LogEntry] = queue.Queue()
        self.log_thread: Optional[threading.Thread] = None
        self._stop_logging = threading.Event()
        
        # Agent info tracking
        self.agent_info = AgentInfo(agent_id=agent_id)
    
    def start(self) -> bool:
        """
        Start the agent subprocess.
        
        Returns:
            True if successfully started, False otherwise
        """
        try:
            # Prepare initial command
            initial_command = {
                "type": AgentCommandType.EXECUTE_PHASE.value,
                "phase_info": self.phase_info,
                "workspace": str(self.workspace),
                "config": self.config
            }
            
            # Write initial command
            self._write_json(self.command_file, initial_command)
            
            # Build agent command
            # In a real implementation, this would invoke claude with appropriate parameters
            # For now, we'll simulate with a Python script
            agent_script = self._create_agent_script()
            
            cmd = [
                "python", agent_script,
                "--agent-id", self.agent_id,
                "--workspace", str(self.workspace),
                "--phase-id", self.phase_info["id"]
            ]
            
            # Start subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.workspace)
            )
            
            self.start_time = datetime.now()
            self.agent_info.assign_phase(self.phase_info["id"])
            self.agent_info.start_work()
            
            # Start log monitoring
            self._start_log_monitoring()
            
            return True
            
        except Exception as e:
            self.agent_info.report_error(f"Failed to start agent: {str(e)}")
            return False
    
    def send_command(self, command: AgentCommand) -> AgentResponse:
        """
        Send a command to the agent and wait for response.
        
        Args:
            command: Command to send
            
        Returns:
            AgentResponse with the result
        """
        if not self.is_alive():
            return AgentResponse(
                success=False,
                message="Agent is not running",
                error="Agent process is not alive"
            )
        
        try:
            # Write command
            command_data = {
                "type": command.command_type.value,
                "payload": command.payload,
                "timestamp": datetime.now().isoformat()
            }
            self._write_json(self.command_file, command_data)
            
            # Wait for response
            response = self._wait_for_response(timeout=command.response_timeout)
            
            if response:
                return AgentResponse(
                    success=response.get("success", False),
                    message=response.get("message", ""),
                    data=response.get("data", {}),
                    error=response.get("error")
                )
            else:
                return AgentResponse(
                    success=False,
                    message="Response timeout",
                    error=f"No response within {command.response_timeout} seconds"
                )
                
        except Exception as e:
            return AgentResponse(
                success=False,
                message="Command failed",
                error=str(e)
            )
    
    def check_health(self) -> AgentStatus:
        """
        Check the health status of the agent.
        
        Returns:
            Current AgentStatus
        """
        if not self.process:
            return AgentStatus.IDLE
        
        # Check if process is still running
        if self.process.poll() is not None:
            # Process has terminated
            return_code = self.process.returncode
            if return_code == 0:
                return AgentStatus.COMPLETED
            else:
                return AgentStatus.ERROR
        
        # Send health check command
        health_cmd = AgentCommand(
            command_type=AgentCommandType.HEALTH_CHECK,
            payload={},
            response_timeout=10
        )
        
        response = self.send_command(health_cmd)
        
        if response.success:
            status_str = response.data.get("status", "working")
            return AgentStatus(status_str)
        else:
            # No response but process is running
            return AgentStatus.WORKING
    
    def terminate(self, graceful: bool = True, timeout: int = 30) -> bool:
        """
        Terminate the agent process.
        
        Args:
            graceful: Whether to attempt graceful shutdown
            timeout: Seconds to wait for graceful shutdown
            
        Returns:
            True if successfully terminated
        """
        if not self.process or not self.is_alive():
            return True
        
        try:
            if graceful:
                # Send terminate command
                term_cmd = AgentCommand(
                    command_type=AgentCommandType.TERMINATE,
                    payload={"reason": "requested"},
                    response_timeout=timeout
                )
                self.send_command(term_cmd)
                
                # Wait for process to exit
                try:
                    self.process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    # Force terminate
                    self.process.terminate()
                    time.sleep(2)
                    if self.is_alive():
                        self.process.kill()
            else:
                # Force terminate immediately
                self.process.terminate()
                time.sleep(2)
                if self.is_alive():
                    self.process.kill()
            
            self.end_time = datetime.now()
            self.agent_info.terminate()
            self._stop_log_monitoring()
            
            return True
            
        except Exception as e:
            self.agent_info.report_error(f"Failed to terminate: {str(e)}")
            return False
    
    def collect_logs(self) -> List[LogEntry]:
        """
        Collect all logs from the agent.
        
        Returns:
            List of log entries
        """
        logs = []
        
        # Get logs from queue
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        
        # Also read any remaining logs from file
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    for line in f:
                        try:
                            log_data = json.loads(line)
                            logs.append(LogEntry(
                                timestamp=datetime.fromisoformat(log_data["timestamp"]),
                                level=log_data["level"],
                                message=log_data["message"],
                                metadata=log_data.get("metadata", {})
                            ))
                        except (json.JSONDecodeError, KeyError):
                            continue
            except Exception:
                pass
        
        return logs
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state."""
        state = {
            "agent_id": self.agent_id,
            "phase_id": self.phase_info["id"],
            "status": self.agent_info.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "is_alive": self.is_alive(),
            "logs_count": self.log_queue.qsize()
        }
        
        # Try to read state file
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    agent_state = json.load(f)
                    state.update(agent_state)
            except Exception:
                pass
        
        return state
    
    def is_alive(self) -> bool:
        """Check if the agent process is still running."""
        return self.process is not None and self.process.poll() is None
    
    def _write_json(self, file_path: Path, data: Any):
        """Write JSON data atomically."""
        temp_file = file_path.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        temp_file.replace(file_path)
    
    def _wait_for_response(self, timeout: int) -> Optional[Dict[str, Any]]:
        """Wait for response file to be written."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.response_file.exists():
                try:
                    with open(self.response_file, 'r') as f:
                        response = json.load(f)
                    # Delete response file after reading
                    self.response_file.unlink()
                    return response
                except Exception:
                    pass
            
            time.sleep(0.1)
        
        return None
    
    def _start_log_monitoring(self):
        """Start monitoring agent logs in a separate thread."""
        self._stop_logging.clear()
        self.log_thread = threading.Thread(target=self._monitor_logs)
        self.log_thread.daemon = True
        self.log_thread.start()
    
    def _stop_log_monitoring(self):
        """Stop the log monitoring thread."""
        self._stop_logging.set()
        if self.log_thread:
            self.log_thread.join(timeout=5)
    
    def _monitor_logs(self):
        """Monitor log file for new entries."""
        # In a real implementation, this would tail the log file
        # For now, we'll simulate periodic checking
        while not self._stop_logging.is_set():
            # Check for new log entries
            # This is a simplified implementation
            time.sleep(1)
    
    def _create_agent_script(self) -> str:
        """Create a temporary agent script for simulation."""
        # In a real implementation, this would invoke the actual Claude CLI
        # For testing, we create a simple simulation script
        script_content = '''#!/usr/bin/env python3
import sys
import json
import time
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--agent-id", required=True)
parser.add_argument("--workspace", required=True)
parser.add_argument("--phase-id", required=True)
args = parser.parse_args()

# Simulate agent work
agent_dir = Path(args.workspace) / "agents" / args.agent_id
command_file = agent_dir / "command.json"
response_file = agent_dir / "response.json"
state_file = agent_dir / "state.json"

# Read initial command
with open(command_file, 'r') as f:
    command = json.load(f)

# Simulate phase execution
print(f"Agent {args.agent_id} executing phase {args.phase_id}")

# Write state
state = {
    "phase_id": args.phase_id,
    "status": "in_progress",
    "progress": 0
}
with open(state_file, 'w') as f:
    json.dump(state, f)

# Simulate work
for i in range(5):
    time.sleep(1)
    state["progress"] = (i + 1) * 20
    with open(state_file, 'w') as f:
        json.dump(state, f)

# Complete
state["status"] = "completed"
state["progress"] = 100
with open(state_file, 'w') as f:
    json.dump(state, f)

# Write response
response = {
    "success": True,
    "message": f"Phase {args.phase_id} completed",
    "data": {"outputs": []}
}
with open(response_file, 'w') as f:
    json.dump(response, f)
'''
        
        script_file = self.agent_dir / "agent_script.py"
        with open(script_file, 'w') as f:
            f.write(script_content)
        script_file.chmod(0o755)
        
        return str(script_file)


class AgentSpawner:
    """
    Manages the lifecycle of multiple agent processes.
    
    Handles spawning, monitoring, and termination of agents for
    parallel phase execution.
    """
    
    def __init__(self, workspace: str, config: Dict[str, Any]):
        """
        Initialize the agent spawner.
        
        Args:
            workspace: Path to shared workspace
            config: Configuration dictionary
        """
        self.workspace = Path(workspace)
        self.config = config
        self.max_agents = config.get("max_agents", 5)
        
        # Agent tracking
        self.agents: Dict[str, AgentProcess] = {}
        self._lock = threading.RLock()
        
        # Ensure agents directory exists
        self.agents_dir = self.workspace / "agents"
        self.agents_dir.mkdir(exist_ok=True)
    
    def spawn_agent(self, phase_info: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Spawn a new agent for a phase.
        
        Args:
            phase_info: Information about the phase to execute
            
        Returns:
            Tuple of (success, agent_id or error message)
        """
        with self._lock:
            # Check agent limit
            active_agents = sum(1 for a in self.agents.values() if a.is_alive())
            if active_agents >= self.max_agents:
                return False, f"Agent limit reached ({self.max_agents})"
            
            # Generate unique agent ID
            agent_id = f"agent-{phase_info['id']}-{uuid.uuid4().hex[:8]}"
            
            # Create agent process
            agent = AgentProcess(
                agent_id=agent_id,
                phase_info=phase_info,
                workspace=str(self.workspace),
                config=self.config
            )
            
            # Start agent
            if agent.start():
                self.agents[agent_id] = agent
                return True, agent_id
            else:
                return False, "Failed to start agent"
    
    def monitor_agent_health(self, agent_id: str) -> AgentStatus:
        """
        Check the health of a specific agent.
        
        Args:
            agent_id: ID of the agent to check
            
        Returns:
            Current AgentStatus
        """
        with self._lock:
            agent = self.agents.get(agent_id)
            if not agent:
                return AgentStatus.IDLE
            
            return agent.check_health()
    
    def terminate_agent(self, agent_id: str, graceful: bool = True) -> bool:
        """
        Terminate a specific agent.
        
        Args:
            agent_id: ID of the agent to terminate
            graceful: Whether to attempt graceful shutdown
            
        Returns:
            True if successfully terminated
        """
        with self._lock:
            agent = self.agents.get(agent_id)
            if not agent:
                return True
            
            success = agent.terminate(graceful=graceful)
            
            # Clean up if terminated
            if success and agent_id in self.agents:
                del self.agents[agent_id]
            
            return success
    
    def collect_agent_logs(self, agent_id: str) -> List[LogEntry]:
        """
        Collect logs from a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of log entries
        """
        with self._lock:
            agent = self.agents.get(agent_id)
            if not agent:
                return []
            
            return agent.collect_logs()
    
    def get_all_agents(self) -> Dict[str, AgentInfo]:
        """Get information about all agents."""
        with self._lock:
            return {
                agent_id: agent.agent_info
                for agent_id, agent in self.agents.items()
            }
    
    def get_active_agents(self) -> List[str]:
        """Get list of active agent IDs."""
        with self._lock:
            return [
                agent_id for agent_id, agent in self.agents.items()
                if agent.is_alive()
            ]
    
    def terminate_all(self, graceful: bool = True) -> int:
        """
        Terminate all agents.
        
        Args:
            graceful: Whether to attempt graceful shutdown
            
        Returns:
            Number of agents successfully terminated
        """
        terminated = 0
        
        with self._lock:
            agent_ids = list(self.agents.keys())
        
        for agent_id in agent_ids:
            if self.terminate_agent(agent_id, graceful=graceful):
                terminated += 1
        
        return terminated
    
    def cleanup_stale_agents(self, max_age_seconds: int = 3600):
        """
        Clean up agents that have been inactive for too long.
        
        Args:
            max_age_seconds: Maximum age for inactive agents
        """
        with self._lock:
            now = datetime.now()
            stale_agents = []
            
            for agent_id, agent in self.agents.items():
                if not agent.is_alive() and agent.end_time:
                    age = (now - agent.end_time).total_seconds()
                    if age > max_age_seconds:
                        stale_agents.append(agent_id)
            
            for agent_id in stale_agents:
                del self.agents[agent_id]