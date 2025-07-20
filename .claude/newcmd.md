# /newcmd - Create New Slash Command

First, understand WHY slash commands work:
<!-- INCLUDE: slash-command-rationale.md#The Key Insight -->

Follow these principles for effective slash commands:
<!-- INCLUDE: principles.md#CORE_PRINCIPLES -->

## Creating a New Slash Command

### 1. **Analyze the Need**
- What workflow is being repeated?
- What steps are being skipped or forgotten?
- Would embedding the workflow solve a discipline problem?

### 2. **Check for Duplication**
- Review `/commands` to ensure no overlap
- Can existing commands be composed instead?
- Is `/safe <task>` sufficient?

### 3. **Design Principles**
- **Single Purpose**: Each command does ONE thing well
- **Complete Workflow**: Include ALL steps, not just reminders
- **Reference Tags**: Use `<!-- INCLUDE: principles.md#TAG -->` for reusable parts
- **Explicit Steps**: Number and detail each step
- **Failure Modes**: What to do when things go wrong

### 4. **Select Appropriate Personas**
Review personas.md and choose 1-2 that best match the command's purpose:
- Test/Debug commands → Senior Test Engineer
- Architecture/Design → Software Architect
- Security/Config → Security Engineer
- Build/Deploy → DevOps Engineer
- Quality/Review → Code Reviewer

### 5. **Command Structure Template**
```markdown
# /[command-name] - [Brief Description]

Embody these expert personas:
<!-- INCLUDE: personas.md#PERSONA_NAME -->

First, load relevant principles:
<!-- INCLUDE: principles.md#RELEVANT_TAGS -->

[Purpose statement - when to use this command]

## Workflow Steps:

1. **[Phase Name]**:
   - Specific action
   - Verification step
   - What success looks like

2. **[Next Phase]**:
   - Continue pattern...

## Success Criteria:
- [ ] Specific measurable outcome
- [ ] Another verification point

## Common Issues:
- If X happens, do Y
- Watch out for Z

Example usage: `/[command-name] [parameters]`
```

### 6. **Integration Steps**
1. Create the command file: `[command-name].md`
2. Update `commands.md` with new command
3. Add any new reusable principles to `principles.md`
4. Update persona mapping in `personas.md` if needed
5. Test the command to ensure it works

### 7. **Quality Checklist**
- [ ] No duplication with existing commands?
- [ ] Workflow completely embedded (not just reminders)?
- [ ] Uses principle tags where appropriate?
- [ ] Includes appropriate expert personas?
- [ ] Clear when to use vs other commands?
- [ ] Solves a real discipline/memory problem?

## Remember the Goal

We're not creating commands for the sake of it. Each command should:
1. **Solve a real problem** where steps get skipped
2. **Embed the workflow** so it can't be ignored
3. **Be easier** than typing the full instructions
4. **Compose well** with other commands

Example: Instead of hoping Claude remembers to validate API responses, create `/api-client` that embeds validation in the generation step.