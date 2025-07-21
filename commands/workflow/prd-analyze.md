# /prd-analyze - Analyze PRD Dependencies and Execution Plan

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->
<!-- INCLUDE: system/personas.md#SYSTEMS_ANALYST -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->

Analyze PRD phase dependencies, identify conflicts, and generate optimal execution plans for both sequential and parallel execution.

## Workflow:

1. **Load PRD Structure**:
   ```
   Loading PRD: continuous-improvement
   ✓ Original PRD loaded
   ✓ 6 phases identified
   ✓ Phase specifications parsed
   ```

2. **Dependency Analysis**:
   ```
   Phase Dependency Graph:
   =======================
   
   phase-1-foundation
   ├── phase-2-api-layer
   │   ├── phase-4-business-logic
   │   │   └── phase-6-integration-tests
   │   └── phase-5-frontend
   │       └── phase-6-integration-tests
   └── phase-3-database-layer
       └── phase-4-business-logic
   
   Dependency Statistics:
   - Total dependencies: 7
   - Max dependency depth: 3
   - Circular dependencies: None
   - Orphaned phases: None
   ```

3. **Critical Path Analysis**:
   ```
   Critical Path Identification:
   =============================
   
   Critical path (longest execution chain):
   phase-1 → phase-3 → phase-4 → phase-6
   Total duration: 11.5 hours
   
   Alternative paths:
   - phase-1 → phase-2 → phase-4 → phase-6 (11h)
   - phase-1 → phase-2 → phase-5 → phase-6 (10.5h)
   
   Bottleneck: phase-4 (depends on both phase-2 and phase-3)
   ```

4. **Parallelization Opportunities**:
   ```
   Parallel Execution Analysis:
   ============================
   
   Execution Waves:
   Wave 1: [phase-1] - 1 agent, 2h
   Wave 2: [phase-2, phase-3] - 2 agents, 3h max
   Wave 3: [phase-4, phase-5] - 2 agents, 4h max
   Wave 4: [phase-6] - 1 agent, 2h
   
   Parallelization Metrics:
   - Sequential time: 17 hours
   - Parallel time: 11 hours
   - Time savings: 6 hours (35%)
   - Efficiency score: 65%
   - Max concurrent agents: 2
   ```

5. **Resource Conflict Detection**:
   ```
   Conflict Analysis:
   ==================
   
   File Conflicts:
   ⚠ /src/config.yaml
     - Modified by: phase-1, phase-2, phase-3
     - Resolution: Sequential access required
   
   ⚠ /src/models/base.py
     - Created by: phase-1
     - Modified by: phase-3, phase-4
     - Resolution: Dependency ordering sufficient
   
   Resource Conflicts:
   ✓ No database conflicts detected
   ✓ No port conflicts detected
   ✓ No memory constraints exceeded
   ```

6. **Optimization Recommendations**:
   ```
   Optimization Opportunities:
   ===========================
   
   1. Phase Restructuring:
      - Consider splitting phase-4 into smaller units
      - Current duration: 4h (bottleneck)
      - Suggested split: auth (2h) + core logic (2h)
   
   2. Dependency Reduction:
      - phase-5 could start earlier if API contracts are defined
      - Potential time saving: 1.5h
   
   3. Resource Allocation:
      - Waves 2-3 underutilize available agents (2/5 used)
      - Consider moving phase-5 validation to wave 2
   ```

7. **Risk Assessment**:
   ```
   Execution Risk Analysis:
   ========================
   
   High Risk Phases:
   - phase-4: Complex dependencies, longest duration
   - phase-6: Depends on all other phases
   
   Medium Risk:
   - phase-2/3: Parallel execution with shared files
   
   Mitigation Strategies:
   - Implement file locking for config.yaml
   - Add integration checkpoints after wave 2
   - Enable rollback points before phase-4
   ```

## Output Formats:

### Visual Dependency Graph:
```
/prd-analyze [project] --graph

Generates interactive HTML visualization:
- Nodes: Phases with duration and status
- Edges: Dependencies with type
- Colors: Critical path highlighting
- Hover: Detailed phase information
```

### JSON Report:
```
/prd-analyze [project] --json

{
  "phases": [...],
  "dependencies": [...],
  "waves": [...],
  "conflicts": [...],
  "metrics": {...},
  "recommendations": [...]
}
```

### Markdown Report:
```
/prd-analyze [project] --report

Generates comprehensive analysis report:
- Executive summary
- Detailed dependency analysis
- Optimization recommendations
- Risk assessment
- Execution timeline
```

## Command Options:

```bash
# Basic analysis
/prd-analyze [project-name]

# Generate visual graph
/prd-analyze [project-name] --graph

# Export analysis as JSON
/prd-analyze [project-name] --json > analysis.json

# Generate detailed report
/prd-analyze [project-name] --report > report.md

# Check specific aspects
/prd-analyze [project-name] --check conflicts
/prd-analyze [project-name] --check critical-path
/prd-analyze [project-name] --check parallelization
```

## Integration with Execution:

The analysis informs execution strategy:

```bash
# Analyze first
/prd-analyze continuous-improvement

# Then execute based on analysis
/prd-parallel continuous-improvement --waves 4 --max-agents 2

# Or execute sequentially if conflicts detected
/prd-implement continuous-improvement phase-1
```

## Example Usage:

```
/prd-analyze continuous-improvement

> Analyzing PRD structure...
> Building dependency graph...
> Detecting conflicts...
> 
> Analysis Summary:
> =================
> Phases: 6
> Dependencies: 7 (no cycles)
> Optimal waves: 4
> Time savings: 35% with parallel execution
> Conflicts: 2 file conflicts (resolvable)
> 
> Critical path: phase-1 → phase-3 → phase-4 → phase-6
> Bottleneck: phase-4 (4h duration, 2 dependencies)
> 
> Recommendation: Execute in parallel with 2 agents
> Estimated time: 11h (vs 17h sequential)
> 
> Run '/prd-parallel continuous-improvement' to execute
```

This provides complete visibility into PRD complexity and enables informed decisions about execution strategy.