"""
Resource conflict detection for parallel PRD execution.

This module analyzes phases to detect potential file conflicts and
suggests appropriate locking strategies.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path

from models.parallel_execution import PhaseInfo, ResourceLock, LockType, ExecutionWave


@dataclass
class ConflictInfo:
    """Information about a resource conflict between phases."""
    resource_path: str
    conflicting_phases: List[str]
    conflict_type: str  # "write-write", "read-write", "write-read"
    severity: str  # "high", "medium", "low"
    suggested_resolution: str
    
    def involves_phase(self, phase_id: str) -> bool:
        """Check if this conflict involves a specific phase."""
        return phase_id in self.conflicting_phases


@dataclass 
class FileAccessPattern:
    """Describes how a phase accesses a file."""
    phase_id: str
    file_path: str
    access_type: str  # "read", "write", "modify", "create", "delete"
    confidence: float  # 0-1, how confident we are about this access


class ConflictDetector:
    """Detects and analyzes resource conflicts between phases."""
    
    # Keywords that suggest different access patterns
    READ_KEYWORDS = {
        'read', 'parse', 'load', 'import', 'fetch', 'get', 'check', 'analyze',
        'examine', 'inspect', 'review', 'scan', 'search', 'find'
    }
    
    WRITE_KEYWORDS = {
        'write', 'save', 'create', 'generate', 'produce', 'output', 'export',
        'store', 'persist', 'dump', 'emit'
    }
    
    MODIFY_KEYWORDS = {
        'modify', 'update', 'change', 'edit', 'alter', 'transform', 'refactor',
        'rename', 'move', 'append', 'extend', 'patch'
    }
    
    DELETE_KEYWORDS = {
        'delete', 'remove', 'clean', 'clear', 'purge', 'erase', 'unlink'
    }
    
    def __init__(self):
        """Initialize the conflict detector."""
        self._access_patterns_cache: Dict[str, List[FileAccessPattern]] = {}
    
    def analyze_file_conflicts(self, phases: List[PhaseInfo]) -> List[ConflictInfo]:
        """
        Analyze phases to detect potential file conflicts.
        
        Args:
            phases: List of phases to analyze
            
        Returns:
            List of detected conflicts
        """
        # Extract file access patterns for all phases
        all_patterns = self._extract_all_access_patterns(phases)
        
        # Group patterns by file
        file_accesses: Dict[str, List[FileAccessPattern]] = defaultdict(list)
        for pattern in all_patterns:
            file_accesses[pattern.file_path].append(pattern)
        
        # Analyze conflicts for each file
        conflicts = []
        for file_path, patterns in file_accesses.items():
            if len(patterns) > 1:
                file_conflicts = self._analyze_file_conflicts(file_path, patterns)
                conflicts.extend(file_conflicts)
        
        # Sort by severity
        conflicts.sort(key=lambda c: self._severity_rank(c.severity))
        
        return conflicts
    
    def suggest_lock_requirements(self, conflicts: List[ConflictInfo]) -> List[ResourceLock]:
        """
        Suggest resource locks based on detected conflicts.
        
        Args:
            conflicts: List of conflicts to resolve
            
        Returns:
            List of suggested ResourceLock configurations
        """
        lock_suggestions = []
        processed_resources = set()
        
        for conflict in conflicts:
            if conflict.resource_path in processed_resources:
                continue
            
            # Determine lock type based on conflict
            if conflict.conflict_type == "write-write":
                # Multiple writers need exclusive locks
                for phase_id in conflict.conflicting_phases:
                    lock = ResourceLock(
                        resource_path=conflict.resource_path,
                        owner_phase=phase_id,
                        lock_type=LockType.EXCLUSIVE
                    )
                    lock_suggestions.append(lock)
            
            elif conflict.conflict_type in ["read-write", "write-read"]:
                # Writers need exclusive, readers need shared
                patterns = self._get_access_patterns_for_file(conflict.resource_path)
                for pattern in patterns:
                    if pattern.phase_id in conflict.conflicting_phases:
                        lock_type = (
                            LockType.EXCLUSIVE 
                            if pattern.access_type in ["write", "modify", "create", "delete"]
                            else LockType.SHARED
                        )
                        lock = ResourceLock(
                            resource_path=conflict.resource_path,
                            owner_phase=pattern.phase_id,
                            lock_type=lock_type
                        )
                        lock_suggestions.append(lock)
            
            processed_resources.add(conflict.resource_path)
        
        return lock_suggestions
    
    def validate_parallel_safety(self, wave: ExecutionWave, phases: Dict[str, PhaseInfo]) -> bool:
        """
        Validate if phases in a wave can safely execute in parallel.
        
        Args:
            wave: Execution wave to validate
            phases: Dictionary mapping phase IDs to PhaseInfo
            
        Returns:
            True if the wave is safe for parallel execution
        """
        # Get phases in this wave
        wave_phases = [phases[pid] for pid in wave.phases if pid in phases]
        
        # Check for conflicts within the wave
        conflicts = self.analyze_file_conflicts(wave_phases)
        
        # High severity conflicts make parallel execution unsafe
        for conflict in conflicts:
            if conflict.severity == "high":
                # Check if all conflicting phases are in this wave
                wave_phase_ids = set(wave.phases)
                conflicting_in_wave = set(conflict.conflicting_phases) & wave_phase_ids
                if len(conflicting_in_wave) > 1:
                    return False
        
        return True
    
    def generate_conflict_report(self, conflicts: List[ConflictInfo]) -> str:
        """
        Generate a human-readable conflict report.
        
        Args:
            conflicts: List of conflicts to report
            
        Returns:
            Formatted conflict report
        """
        if not conflicts:
            return "No conflicts detected."
        
        report_lines = ["# Resource Conflict Report", ""]
        
        # Summary
        report_lines.append(f"Total conflicts detected: {len(conflicts)}")
        
        # Count by severity
        severity_counts = defaultdict(int)
        for conflict in conflicts:
            severity_counts[conflict.severity] += 1
        
        report_lines.append("\nConflicts by severity:")
        for severity in ["high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            report_lines.append(f"  - {severity.capitalize()}: {count}")
        
        # Detailed conflicts
        report_lines.append("\n## Detailed Conflicts\n")
        
        for i, conflict in enumerate(conflicts, 1):
            report_lines.append(f"### {i}. {conflict.resource_path}")
            report_lines.append(f"   Type: {conflict.conflict_type}")
            report_lines.append(f"   Severity: {conflict.severity}")
            report_lines.append(f"   Phases: {', '.join(conflict.conflicting_phases)}")
            report_lines.append(f"   Resolution: {conflict.suggested_resolution}")
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def _extract_all_access_patterns(self, phases: List[PhaseInfo]) -> List[FileAccessPattern]:
        """Extract file access patterns from all phases."""
        all_patterns = []
        
        for phase in phases:
            patterns = self._extract_phase_access_patterns(phase)
            all_patterns.extend(patterns)
            # Cache for later use
            self._access_patterns_cache[phase.id] = patterns
        
        return all_patterns
    
    def _extract_phase_access_patterns(self, phase: PhaseInfo) -> List[FileAccessPattern]:
        """Extract file access patterns from a single phase."""
        patterns = []
        
        # Analyze outputs - these are definitely writes
        for output in phase.outputs:
            patterns.append(FileAccessPattern(
                phase_id=phase.id,
                file_path=output,
                access_type="write",
                confidence=0.9
            ))
        
        # Analyze description for access patterns
        desc_lower = phase.description.lower()
        
        # Look for file references in description
        # This is simplified - in practice, you'd want more sophisticated parsing
        words = desc_lower.split()
        
        for i, word in enumerate(words):
            # Check for action keywords followed by file-like references
            if word in self.WRITE_KEYWORDS:
                # High confidence for explicit writes
                confidence = 0.8
            elif word in self.READ_KEYWORDS:
                confidence = 0.7
            elif word in self.MODIFY_KEYWORDS:
                confidence = 0.8
            elif word in self.DELETE_KEYWORDS:
                confidence = 0.9
            else:
                continue
            
            # Look for file paths in nearby context
            # This is a simplified heuristic
            context_words = words[max(0, i-3):min(len(words), i+4)]
            for ctx_word in context_words:
                if '.' in ctx_word or '/' in ctx_word:
                    # Might be a file path
                    access_type = self._determine_access_type(word)
                    if access_type:
                        patterns.append(FileAccessPattern(
                            phase_id=phase.id,
                            file_path=ctx_word,
                            access_type=access_type,
                            confidence=confidence * 0.5  # Lower confidence for heuristic
                        ))
        
        return patterns
    
    def _determine_access_type(self, keyword: str) -> Optional[str]:
        """Determine access type from keyword."""
        if keyword in self.READ_KEYWORDS:
            return "read"
        elif keyword in self.WRITE_KEYWORDS:
            return "write"
        elif keyword in self.MODIFY_KEYWORDS:
            return "modify"
        elif keyword in self.DELETE_KEYWORDS:
            return "delete"
        return None
    
    def _analyze_file_conflicts(self, file_path: str, 
                                patterns: List[FileAccessPattern]) -> List[ConflictInfo]:
        """Analyze conflicts for a specific file."""
        conflicts = []
        
        # Group patterns by access type
        writers = [p for p in patterns if p.access_type in ["write", "create"]]
        modifiers = [p for p in patterns if p.access_type == "modify"]
        readers = [p for p in patterns if p.access_type == "read"]
        deleters = [p for p in patterns if p.access_type == "delete"]
        
        # Write-Write conflicts (high severity)
        if len(writers) > 1:
            conflicts.append(ConflictInfo(
                resource_path=file_path,
                conflicting_phases=[p.phase_id for p in writers],
                conflict_type="write-write",
                severity="high",
                suggested_resolution="Use exclusive locks or serialize write operations"
            ))
        
        # Write-Modify conflicts (high severity)
        if writers and modifiers:
            all_phases = [p.phase_id for p in writers + modifiers]
            conflicts.append(ConflictInfo(
                resource_path=file_path,
                conflicting_phases=all_phases,
                conflict_type="write-write",  # Treat as write-write
                severity="high",
                suggested_resolution="Coordinate write and modify operations with exclusive locks"
            ))
        
        # Write-Read conflicts (medium severity)
        if writers and readers:
            writer_phases = [p.phase_id for p in writers]
            reader_phases = [p.phase_id for p in readers]
            conflicts.append(ConflictInfo(
                resource_path=file_path,
                conflicting_phases=writer_phases + reader_phases,
                conflict_type="write-read",
                severity="medium",
                suggested_resolution="Ensure readers complete before writers start"
            ))
        
        # Delete conflicts (high severity)
        if deleters and (writers or modifiers or readers):
            all_phases = set()
            for p in patterns:
                all_phases.add(p.phase_id)
            conflicts.append(ConflictInfo(
                resource_path=file_path,
                conflicting_phases=list(all_phases),
                conflict_type="write-write",  # Treat delete as write
                severity="high",
                suggested_resolution="Ensure delete operations are properly sequenced"
            ))
        
        return conflicts
    
    def _get_access_patterns_for_file(self, file_path: str) -> List[FileAccessPattern]:
        """Get cached access patterns for a specific file."""
        patterns = []
        for phase_patterns in self._access_patterns_cache.values():
            for pattern in phase_patterns:
                if pattern.file_path == file_path:
                    patterns.append(pattern)
        return patterns
    
    def _severity_rank(self, severity: str) -> int:
        """Get numeric rank for severity (lower is more severe)."""
        ranks = {"high": 0, "medium": 1, "low": 2}
        return ranks.get(severity, 3)