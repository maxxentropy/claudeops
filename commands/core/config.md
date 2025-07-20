# /config - Configuration Change Workflow

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SECURITY_ENGINEER -->
<!-- INCLUDE: system/personas.md#DEVOPS_ENGINEER -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->
<!-- INCLUDE: system/principles.md#SECURITY_RULES -->

Make configuration changes with API version verification:

1. **Version Check** (ABSOLUTELY FIRST):
   <!-- INCLUDE: system/principles.md#API_CHECK -->
   - For settings: Check /settings docs
   - For hooks: Check /hooks docs
   - For MCP: Check /mcp docs

2. **Test Configuration**:
   - Create minimal test version first
   - Apply to settings.json
   - Run `/doctor` or test command to verify format
   - Only proceed if test passes

3. **Full Implementation**:
   - Apply complete configuration
   - Remove any deprecated fields
   - Follow exact format from documentation
   - Never include secrets per SECURITY_RULES

4. **Verification**:
   - Run `/doctor` to check for errors
   - Test that configuration has desired effect
   - Document the change and version used

CRITICAL: Never assume format. Always check current docs first.