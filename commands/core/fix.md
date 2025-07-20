# /fix - Systematic Fix Workflow

Embody these expert personas:
<!-- INCLUDE: system/personas.md#SENIOR_TEST_ENGINEER -->
<!-- INCLUDE: system/personas.md#SRE_ENGINEER -->

First, load and follow these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->

Fix issues using the COMPLETE verification process:

1. **Investigation Phase** (MANDATORY):
   - Check last 3 commits: `git log -3 --oneline`
   - Look for recent changes that might have introduced the issue
   - Run existing tests to understand current state
   - Read error messages carefully and completely

2. **Implementation Phase**:
   - Make the minimal change needed to fix the issue
   - Do NOT add extra features or refactoring
   - Follow language standards:
   <!-- INCLUDE: system/principles.md#LANG_STANDARDS -->

3. **Verification Phase**:
   <!-- INCLUDE: system/principles.md#VERIFICATION_STEPS -->

4. **Completion**:
   - Only mark as complete when ALL verification passes
   - Document what was wrong and how it was fixed
   - If cannot fix, explain why and what's blocking

REMEMBER: No shortcuts. No "this should work". Prove it works or it's not fixed.