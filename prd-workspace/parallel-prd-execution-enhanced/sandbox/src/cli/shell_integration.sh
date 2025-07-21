#!/bin/bash
# Shell integration for PRD parallel execution commands

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_CMD="${PYTHON_CMD:-python3}"

# Function to execute prd-parallel command
prd-parallel() {
    "$PYTHON_CMD" "$SCRIPT_DIR/prd_parallel_cli.py" "$@"
}

# Function to execute prd-analyze command
prd-analyze() {
    "$PYTHON_CMD" "$SCRIPT_DIR/prd_analyze_cli.py" "$@"
}

# Function to watch PRD execution progress
prd-watch() {
    local project="$1"
    if [ -z "$project" ]; then
        echo "Usage: prd-watch <project-name>"
        return 1
    fi
    
    # Monitor execution state file for changes
    local state_file="$HOME/.claude/prd-workspace/$project/sandbox/.execution_state.json"
    
    if [ ! -f "$state_file" ]; then
        echo "No active execution found for project: $project"
        return 1
    fi
    
    # Use watch command if available, otherwise loop
    if command -v watch >/dev/null 2>&1; then
        watch -n 2 "$PYTHON_CMD" "$SCRIPT_DIR/progress_monitor.py" "$project"
    else
        while true; do
            clear
            "$PYTHON_CMD" "$SCRIPT_DIR/progress_monitor.py" "$project"
            sleep 2
        done
    fi
}

# Function to list available PRD projects
prd-list() {
    local workspace="$HOME/.claude/prd-workspace"
    
    if [ ! -d "$workspace" ]; then
        echo "No PRD workspace found at $workspace"
        return 1
    fi
    
    echo "Available PRD projects:"
    echo "======================="
    
    for project in "$workspace"/*; do
        if [ -d "$project" ]; then
            project_name=$(basename "$project")
            phase_count=$(find "$project" -name "phase-*.md" 2>/dev/null | wc -l)
            
            # Check if there's an active execution
            if [ -f "$project/sandbox/.execution_state.json" ]; then
                status="[ACTIVE]"
            elif [ -f "$project/prd-tracker.md" ]; then
                # Try to get completion status from tracker
                if grep -q "Status: COMPLETE" "$project/prd-tracker.md" 2>/dev/null; then
                    status="[COMPLETE]"
                else
                    status="[IN PROGRESS]"
                fi
            else
                status=""
            fi
            
            printf "  %-30s %2d phases  %s\n" "$project_name" "$phase_count" "$status"
        fi
    done
}

# Function to stop a running PRD execution
prd-stop() {
    local project="$1"
    if [ -z "$project" ]; then
        echo "Usage: prd-stop <project-name>"
        return 1
    fi
    
    # Create stop signal file
    local stop_file="$HOME/.claude/prd-workspace/$project/sandbox/.stop_requested"
    touch "$stop_file"
    
    echo "Stop requested for project: $project"
    echo "Waiting for agents to finish current phases..."
}

# Completion function for bash
_prd_completion() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local cmd="${COMP_WORDS[1]}"
    local workspace="$HOME/.claude/prd-workspace"
    
    # Get list of projects
    local projects=""
    if [ -d "$workspace" ]; then
        projects=$(ls -d "$workspace"/*/ 2>/dev/null | xargs -n1 basename)
    fi
    
    case "$cmd" in
        "")
            # Complete command names
            COMPREPLY=($(compgen -W "prd-parallel prd-analyze prd-watch prd-list prd-stop" -- "$cur"))
            ;;
        *)
            # Complete project names
            COMPREPLY=($(compgen -W "$projects" -- "$cur"))
            ;;
    esac
}

# Register completion if using bash
if [ -n "$BASH_VERSION" ]; then
    complete -F _prd_completion prd-parallel
    complete -F _prd_completion prd-analyze
    complete -F _prd_completion prd-watch
    complete -F _prd_completion prd-stop
fi

# Export functions for use in current shell
export -f prd-parallel
export -f prd-analyze
export -f prd-watch
export -f prd-list
export -f prd-stop

echo "PRD parallel execution commands loaded:"
echo "  - prd-parallel: Execute PRD phases in parallel"
echo "  - prd-analyze: Analyze PRD dependencies"
echo "  - prd-watch: Monitor active execution"
echo "  - prd-list: List available projects"
echo "  - prd-stop: Stop running execution"