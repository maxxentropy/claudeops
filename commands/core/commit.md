# /commit - Safe Commit Workflow

Embody these expert personas:
<!-- INCLUDE: system/personas.md#CODE_REVIEWER -->
<!-- INCLUDE: system/personas.md#SECURITY_ENGINEER -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->
<!-- INCLUDE: system/principles.md#SECURITY_RULES -->

Execute the COMPLETE commit workflow:

1. **Pre-Commit Verification**:
   <!-- INCLUDE: system/principles.md#VERIFICATION_STEPS -->

2. **Review Changes**:
   - Run `git status` to see all changes
   - Run `git diff --staged` to review what will be committed
   - Verify all changes align with the task requirements
   - Check for any security issues per SECURITY_RULES

3. **Create Commit**:
   - Stage changes: `git add -A`
   <!-- INCLUDE: system/principles.md#COMMIT_FORMAT -->

4. **Post-Commit**:
   - Show the commit hash and message
   - Run `git log -1 --oneline` to confirm

CRITICAL: If ANY step fails, STOP and report the issue. Do not proceed with partial verification.