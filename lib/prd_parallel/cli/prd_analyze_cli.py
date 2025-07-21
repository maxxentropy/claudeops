#!/usr/bin/env python3
"""
Command-line interface for PRD dependency analysis.

This module provides tools to analyze PRD phase dependencies,
identify conflicts, and generate execution plans.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import textwrap
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.phase_parser import PhaseParser
from models.parallel_execution import PhaseInfo
from analyzers.dependency_analyzer import DependencyAnalyzer
from analyzers.wave_calculator import WaveCalculator
from analyzers.conflict_detector import ConflictDetector


class PRDAnalyzeCLI:
    """Command-line interface for PRD dependency analysis."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.workspace_root = Path.home() / ".claude" / "prd-workspace"
        self.parser = self._create_parser()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="Analyze PRD dependencies and generate execution plans",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic dependency analysis
  prd-analyze my-project
  
  # Generate visual dependency graph
  prd-analyze my-project --graph
  
  # Export analysis as JSON
  prd-analyze my-project --json > analysis.json
  
  # Generate detailed markdown report
  prd-analyze my-project --report > report.md
  
  # Check specific aspects
  prd-analyze my-project --check conflicts
  prd-analyze my-project --check critical-path
            """
        )
        
        parser.add_argument(
            "project",
            help="Name of the PRD project to analyze"
        )
        
        parser.add_argument(
            "--graph",
            action="store_true",
            help="Generate visual dependency graph (HTML)"
        )
        
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output analysis in JSON format"
        )
        
        parser.add_argument(
            "--report",
            action="store_true",
            help="Generate detailed markdown report"
        )
        
        parser.add_argument(
            "--check",
            choices=["conflicts", "critical-path", "parallelization", "all"],
            help="Check specific aspects of the PRD"
        )
        
        parser.add_argument(
            "--max-agents",
            type=int,
            default=5,
            help="Maximum agents for parallelization analysis (default: 5)"
        )
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI with given arguments.
        
        Args:
            args: Command line arguments (None uses sys.argv)
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        parsed_args = self.parser.parse_args(args)
        
        try:
            # Load project
            project_path = self.workspace_root / parsed_args.project
            if not project_path.exists():
                print(f"Error: Project '{parsed_args.project}' not found")
                return 1
            
            # Load phases
            phases = self._load_phases(project_path)
            if not phases:
                print("Error: No phases found in project")
                return 1
            
            # Perform analysis
            analysis_result = self._analyze_phases(phases, parsed_args.max_agents)
            
            # Output results based on format
            if parsed_args.graph:
                self._generate_graph(analysis_result, project_path)
            elif parsed_args.json:
                self._output_json(analysis_result)
            elif parsed_args.report:
                self._generate_report(analysis_result)
            elif parsed_args.check:
                self._check_specific(analysis_result, parsed_args.check)
            else:
                self._output_summary(analysis_result)
            
            return 0
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            if parsed_args.json:
                print(json.dumps({"error": str(e)}))
            return 1
    
    def _load_phases(self, project_path: Path) -> List[PhaseInfo]:
        """Load phase specifications from project directory."""
        phases = []
        phase_files = sorted(project_path.glob("phase-*.md"))
        
        parser = PhaseParser()
        for phase_file in phase_files:
            try:
                phase = parser.parse_phase_file(str(phase_file))
                phases.append(phase)
            except Exception as e:
                print(f"Warning: Failed to parse {phase_file.name}: {e}")
        
        return phases
    
    def _analyze_phases(self, phases: List[PhaseInfo], max_agents: int) -> Dict[str, Any]:
        """Perform comprehensive phase analysis."""
        # Initialize analyzers
        dep_analyzer = DependencyAnalyzer()
        wave_calculator = WaveCalculator()
        conflict_detector = ConflictDetector()
        
        # Build dependency graph
        graph = dep_analyzer.build_dependency_graph(phases)
        
        # Validate dependencies
        is_valid, errors = dep_analyzer.validate_dependencies(graph)
        
        # Calculate execution waves
        waves = wave_calculator.calculate_execution_waves(graph)
        optimized_waves = wave_calculator.optimize_wave_distribution(waves, max_agents)
        
        # Calculate metrics
        metrics = wave_calculator.calculate_metrics(waves, graph)
        
        # Identify critical path
        critical_path = wave_calculator.identify_critical_path(graph)
        
        # Detect conflicts
        file_conflicts = conflict_detector.analyze_file_conflicts(phases)
        
        # Check parallel safety
        phases_dict = {p.id: p for p in phases}
        wave_safety = {}
        for wave in waves:
            wave_safety[wave.wave_number] = conflict_detector.validate_parallel_safety(
                wave, phases_dict
            )
        
        return {
            "phases": phases,
            "graph": graph,
            "validation": {"is_valid": is_valid, "errors": errors},
            "waves": waves,
            "optimized_waves": optimized_waves,
            "metrics": metrics,
            "critical_path": critical_path,
            "conflicts": file_conflicts,
            "wave_safety": wave_safety,
            "max_agents": max_agents
        }
    
    def _output_summary(self, analysis: Dict[str, Any]):
        """Output a summary of the analysis."""
        print(f"\nPRD Analysis Summary")
        print("=" * 50)
        
        # Basic info
        print(f"\nPhases: {len(analysis['phases'])}")
        print(f"Dependencies: {sum(len(p.dependencies) for p in analysis['phases'])}")
        
        # Validation
        validation = analysis['validation']
        if validation['is_valid']:
            print("Validation: ✓ All dependencies valid")
        else:
            print(f"Validation: ✗ {len(validation['errors'])} errors found")
            for error in validation['errors'][:3]:
                print(f"  - {error}")
        
        # Execution waves
        print(f"\nExecution Waves: {len(analysis['waves'])}")
        for wave in analysis['waves']:
            print(f"  Wave {wave.wave_number}: {wave.phases}")
        
        # Metrics
        metrics = analysis['metrics']
        print(f"\nExecution Metrics:")
        print(f"  Sequential time: {metrics.total_time:.1f} hours")
        
        # Calculate parallel time
        parallel_time = sum(
            max(analysis['graph'].get_phase(p).estimated_time 
                for p in wave.phases)
            for wave in analysis['waves']
        )
        time_saved = metrics.total_time - parallel_time
        efficiency = (time_saved / metrics.total_time * 100) if metrics.total_time > 0 else 0
        
        print(f"  Parallel time: {parallel_time:.1f} hours")
        print(f"  Time savings: {time_saved:.1f} hours ({efficiency:.1f}%)")
        print(f"  Max parallelism: {metrics.max_parallelism} phases")
        print(f"  Utilization: {metrics.utilization_score:.1%}")
        
        # Critical path
        critical_path = analysis['critical_path']
        if critical_path:
            path_ids = [p.id for p in critical_path]
            path_time = sum(p.estimated_time for p in critical_path)
            print(f"\nCritical Path ({path_time:.1f} hours):")
            print(f"  {' → '.join(path_ids)}")
        
        # Conflicts
        conflicts = analysis['conflicts']
        if conflicts:
            print(f"\nConflicts: {len(conflicts)} potential conflicts detected")
            for conflict in conflicts[:3]:
                print(f"  - {conflict.conflict_type}: {conflict.resource}")
        else:
            print("\nConflicts: ✓ No conflicts detected")
    
    def _output_json(self, analysis: Dict[str, Any]):
        """Output analysis as JSON."""
        # Convert objects to JSON-serializable format
        output = {
            "phases": [
                {
                    "id": p.id,
                    "name": p.name,
                    "dependencies": p.dependencies,
                    "outputs": p.outputs,
                    "estimated_time": p.estimated_time
                }
                for p in analysis['phases']
            ],
            "validation": analysis['validation'],
            "waves": [
                {
                    "wave_number": w.wave_number,
                    "phases": w.phases,
                    "status": w.status
                }
                for w in analysis['waves']
            ],
            "metrics": {
                "total_waves": analysis['metrics'].total_waves,
                "max_parallelism": analysis['metrics'].max_parallelism,
                "total_time": analysis['metrics'].total_time,
                "critical_path_length": analysis['metrics'].critical_path_length,
                "utilization_score": analysis['metrics'].utilization_score
            },
            "critical_path": [p.id for p in analysis['critical_path']],
            "conflicts": [
                {
                    "type": c.conflict_type,
                    "resource": c.resource,
                    "phases": c.phases
                }
                for c in analysis['conflicts']
            ]
        }
        
        print(json.dumps(output, indent=2))
    
    def _generate_report(self, analysis: Dict[str, Any]):
        """Generate detailed markdown report."""
        print("# PRD Dependency Analysis Report")
        print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n## Executive Summary\n")
        
        metrics = analysis['metrics']
        parallel_time = sum(
            max(analysis['graph'].get_phase(p).estimated_time 
                for p in wave.phases)
            for wave in analysis['waves']
        )
        time_saved = metrics.total_time - parallel_time
        
        print(f"- **Total Phases**: {len(analysis['phases'])}")
        print(f"- **Execution Waves**: {len(analysis['waves'])}")
        print(f"- **Sequential Time**: {metrics.total_time:.1f} hours")
        print(f"- **Parallel Time**: {parallel_time:.1f} hours")
        print(f"- **Time Savings**: {time_saved:.1f} hours "
              f"({time_saved/metrics.total_time*100:.1f}%)")
        print(f"- **Max Parallelism**: {metrics.max_parallelism} concurrent phases")
        
        print("\n## Phase Dependencies\n")
        
        print("```mermaid")
        print("graph TD")
        for phase in analysis['phases']:
            for dep in phase.dependencies:
                print(f"    {dep} --> {phase.id}")
        print("```")
        
        print("\n## Execution Waves\n")
        
        for wave in analysis['waves']:
            print(f"\n### Wave {wave.wave_number}")
            phases_in_wave = [analysis['graph'].get_phase(p) for p in wave.phases]
            max_time = max(p.estimated_time for p in phases_in_wave)
            
            print(f"\n- **Phases**: {len(wave.phases)}")
            print(f"- **Duration**: {max_time:.1f} hours")
            print(f"- **Parallel Safety**: "
                  f"{'✓ Safe' if analysis['wave_safety'][wave.wave_number] else '✗ Unsafe'}")
            
            print("\n| Phase | Name | Duration | Dependencies |")
            print("|-------|------|----------|--------------|")
            for phase in phases_in_wave:
                deps = ", ".join(phase.dependencies) or "None"
                print(f"| {phase.id} | {phase.name} | {phase.estimated_time:.1f}h | {deps} |")
        
        print("\n## Critical Path Analysis\n")
        
        critical_path = analysis['critical_path']
        if critical_path:
            path_time = sum(p.estimated_time for p in critical_path)
            print(f"The critical path determines the minimum execution time: **{path_time:.1f} hours**")
            
            print("\n| Step | Phase | Duration | Cumulative |")
            print("|------|-------|----------|------------|")
            cumulative = 0
            for i, phase in enumerate(critical_path, 1):
                cumulative += phase.estimated_time
                print(f"| {i} | {phase.id} | {phase.estimated_time:.1f}h | {cumulative:.1f}h |")
        
        print("\n## Conflict Analysis\n")
        
        conflicts = analysis['conflicts']
        if conflicts:
            print(f"Found {len(conflicts)} potential conflicts:\n")
            
            # Group conflicts by type
            by_type = {}
            for conflict in conflicts:
                by_type.setdefault(conflict.conflict_type, []).append(conflict)
            
            for conflict_type, type_conflicts in by_type.items():
                print(f"\n### {conflict_type.title()} Conflicts\n")
                for conflict in type_conflicts:
                    print(f"- **{conflict.resource}**: {', '.join(conflict.phases)}")
        else:
            print("No conflicts detected. All phases can execute safely in parallel.")
        
        print("\n## Recommendations\n")
        
        # Generate recommendations based on analysis
        recommendations = []
        
        if metrics.utilization_score < 0.6:
            recommendations.append(
                "- **Low utilization**: Consider restructuring phases to improve parallelism"
            )
        
        if len(conflicts) > 5:
            recommendations.append(
                "- **High conflict count**: Review phase outputs to reduce resource contention"
            )
        
        if metrics.critical_path_length > len(analysis['phases']) * 0.7:
            recommendations.append(
                "- **Long critical path**: Consider breaking down phases on the critical path"
            )
        
        if not recommendations:
            recommendations.append("- **Well optimized**: The PRD structure allows efficient parallel execution")
        
        for rec in recommendations:
            print(rec)
    
    def _generate_graph(self, analysis: Dict[str, Any], project_path: Path):
        """Generate visual dependency graph."""
        graph_path = project_path / "dependency-graph.html"
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>PRD Dependency Graph</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css" />
    <style>
        #mynetwork {
            width: 100%;
            height: 600px;
            border: 1px solid lightgray;
        }
        .info {
            padding: 10px;
            background: #f0f0f0;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>PRD Dependency Graph</h1>
    <div class="info">
        <strong>Phases:</strong> {phase_count} | 
        <strong>Waves:</strong> {wave_count} | 
        <strong>Critical Path:</strong> {critical_path}
    </div>
    <div id="mynetwork"></div>
    <script>
        var nodes = new vis.DataSet({nodes});
        var edges = new vis.DataSet({edges});
        
        var container = document.getElementById('mynetwork');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            layout: {{
                hierarchical: {{
                    direction: 'UD',
                    sortMethod: 'directed'
                }}
            }},
            edges: {{
                arrows: 'to'
            }}
        }};
        
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
        """
        
        # Prepare nodes and edges
        nodes = []
        edges = []
        critical_path_ids = {p.id for p in analysis['critical_path']}
        
        for phase in analysis['phases']:
            is_critical = phase.id in critical_path_ids
            nodes.append({
                "id": phase.id,
                "label": f"{phase.id}\\n{phase.estimated_time:.1f}h",
                "color": "#ff6b6b" if is_critical else "#4ecdc4",
                "title": f"{phase.name}\\nDuration: {phase.estimated_time}h"
            })
            
            for dep in phase.dependencies:
                edges.append({
                    "from": dep,
                    "to": phase.id
                })
        
        # Format HTML
        critical_path_str = " → ".join(p.id for p in analysis['critical_path'])
        html = html_content.format(
            phase_count=len(analysis['phases']),
            wave_count=len(analysis['waves']),
            critical_path=critical_path_str,
            nodes=json.dumps(nodes),
            edges=json.dumps(edges)
        )
        
        # Write file
        graph_path.write_text(html)
        print(f"Dependency graph generated: {graph_path}")
    
    def _check_specific(self, analysis: Dict[str, Any], check_type: str):
        """Check specific aspects of the PRD."""
        if check_type == "all":
            check_types = ["conflicts", "critical-path", "parallelization"]
        else:
            check_types = [check_type]
        
        for ct in check_types:
            print(f"\n{ct.upper()} CHECK")
            print("=" * 50)
            
            if ct == "conflicts":
                conflicts = analysis['conflicts']
                if conflicts:
                    print(f"\n✗ Found {len(conflicts)} conflicts:")
                    for conflict in conflicts:
                        print(f"  - {conflict.conflict_type}: {conflict.resource}")
                        print(f"    Phases: {', '.join(conflict.phases)}")
                else:
                    print("\n✓ No conflicts detected")
            
            elif ct == "critical-path":
                critical_path = analysis['critical_path']
                if critical_path:
                    path_time = sum(p.estimated_time for p in critical_path)
                    print(f"\nCritical path length: {len(critical_path)} phases, {path_time:.1f} hours")
                    print("Path: " + " → ".join(p.id for p in critical_path))
                    
                    # Check if critical path is too long
                    total_phases = len(analysis['phases'])
                    if len(critical_path) > total_phases * 0.7:
                        print("\n⚠ Warning: Critical path contains >70% of all phases")
                        print("  Consider restructuring to improve parallelization")
            
            elif ct == "parallelization":
                metrics = analysis['metrics']
                print(f"\nParallelization potential:")
                print(f"  Max concurrent phases: {metrics.max_parallelism}")
                print(f"  Utilization score: {metrics.utilization_score:.1%}")
                print(f"  Waves: {metrics.total_waves}")
                
                if metrics.utilization_score < 0.5:
                    print("\n⚠ Warning: Low utilization score")
                    print("  Many agents will be idle during execution")
                elif metrics.utilization_score > 0.8:
                    print("\n✓ Excellent utilization score")
                    print("  Phases are well-structured for parallel execution")


def main():
    """Main entry point."""
    cli = PRDAnalyzeCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()