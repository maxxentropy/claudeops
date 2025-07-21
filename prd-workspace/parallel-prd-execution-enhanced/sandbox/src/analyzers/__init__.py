"""Dependency analysis and conflict detection components."""

from .dependency_analyzer import DependencyAnalyzer, ValidationError, CircularDependencyError
from .wave_calculator import WaveCalculator, WaveMetrics
from .conflict_detector import ConflictDetector, ConflictInfo, FileAccessPattern

__all__ = [
    'DependencyAnalyzer',
    'ValidationError', 
    'CircularDependencyError',
    'WaveCalculator',
    'WaveMetrics',
    'ConflictDetector',
    'ConflictInfo',
    'FileAccessPattern'
]