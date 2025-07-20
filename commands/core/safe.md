# /safe - Safe General Workflow

Embody these expert personas:
<!-- INCLUDE: system/personas.md#CODE_REVIEWER -->
<!-- INCLUDE: system/personas.md#SOFTWARE_ARCHITECT -->

First, load and follow ALL these principles:
<!-- INCLUDE: system/principles.md#CORE_PRINCIPLES -->
<!-- INCLUDE: system/principles.md#LANG_STANDARDS -->
<!-- INCLUDE: system/principles.md#SECURITY_RULES -->
<!-- INCLUDE: system/principles.md#TEST_STANDARDS -->

Execute any task with full safety checks:

1. **Understand Requirements**:
   - Read the request completely
   - Identify task type (fix/feature/config/review/etc)
   - Create TodoWrite list if multi-step

2. **Check Relevant Patterns**:
   - If error handling needed:
   <!-- INCLUDE: system/principles.md#ERROR_PATTERN -->
   - If MAUI/Prism work:
   <!-- INCLUDE: system/principles.md#MAUI_PRISM -->

3. **Execute with Verification**:
   <!-- INCLUDE: system/principles.md#VERIFICATION_STEPS -->

4. **Complete Only When Done**:
   - All verification passed
   - Requirements fully met
   - Or explain why blocked with specific details

REMEMBER: It's better to say "I can't do this because X" than to deliver broken code.