# Create Documentation Command

🎯 **COMMAND**: /create-docs | 📋 **WORKFLOW**: Workflow | 👤 **PERSONAS**: Default

You will analyze the codebase and create comprehensive documentation. Follow these steps:

## 1. Analyze Project Structure
- Scan all directories and files
- Identify the project type and technology stack
- Map out the component hierarchy

## 2. Generate Documentation Sections

### README.md (if needed or update existing)
- Project overview and purpose
- Key features
- Technology stack
- Getting started guide
- Build and run instructions
- Testing procedures
- Contributing guidelines

### API Documentation (if applicable)
- Endpoint descriptions
- Request/response formats
- Authentication requirements
- Error codes and handling
- Usage examples

### Architecture Documentation
- System architecture diagram (in Mermaid format)
- Component relationships
- Data flow diagrams
- Design patterns used
- Key architectural decisions

### Code Documentation
- Class and interface summaries
- Public API documentation
- Complex algorithm explanations
- Configuration options

### Development Guide
- Setup instructions
- Development workflow
- Coding standards
- Common tasks and solutions
- Troubleshooting guide

## 3. Documentation Format
- Use Markdown for all documentation
- Include code examples where helpful
- Add diagrams using Mermaid syntax
- Create a documentation index/table of contents
- Keep language clear and concise

## 4. Special Considerations
- Document any non-obvious design decisions
- Include performance considerations
- Note security implications
- Document known limitations
- Add references to external resources

## 5. Output Structure
Create documentation files in a `docs/` folder (automatically resolves to repository root):
```
docs/
├── README.md           # Main documentation
├── ARCHITECTURE.md     # System architecture
├── API.md             # API documentation
├── DEVELOPMENT.md     # Developer guide
├── DEPLOYMENT.md      # Deployment instructions
└── TROUBLESHOOTING.md # Common issues and solutions
```

**Path Resolution**: Documentation will be created in the repository root's `docs/` directory, regardless of where the command is run from.

## Implementation Note:
When implementing this command, always use the path resolution utilities to ensure consistent paths:

```python
# Import path resolution utilities
import sys
import os
sys.path.insert(0, os.path.expanduser('~/.claude'))
from system.utils import path_resolver

# Ensure docs directory exists
docs_dir = path_resolver.ensure_directory('docs')

# Create documentation files
readme_path = docs_dir / "README.md"
architecture_path = docs_dir / "ARCHITECTURE.md"
api_path = docs_dir / "API.md"

# Write content
readme_path.write_text(readme_content)
architecture_path.write_text(architecture_content)

# Format output message
output_paths = {
    "Documentation created in": docs_dir,
    "Main README": readme_path,
    "Architecture docs": architecture_path,
    "API documentation": api_path if api_path.exists() else None
}
# Filter out None values
output_paths = {k: v for k, v in output_paths.items() if v}
print(path_resolver.format_output_message(output_paths))
```

**Important**: Never hardcode paths like `docs/`. Always use the path resolver to ensure documentation is created in the correct location.

Begin by analyzing the project structure and then create appropriate documentation based on what you find.