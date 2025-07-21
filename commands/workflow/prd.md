# /prd - Formal Product Requirements Document

🎯 **COMMAND**: /prd | 📋 **WORKFLOW**: Formal Product Requirements Document | 👤 **PERSONAS**: Default

Create a comprehensive PRD suitable for team planning and stakeholder review:

## Workflow:

1. **Research Phase**:
   - **Understand the domain**: Research similar features/products
   - **Identify stakeholders**: Who uses this, who maintains it
   - **Technical feasibility**: Check architecture constraints

2. **Generate PRD Content**:
   - Follow PRD structure below
   - Include all sections for completeness
   - Target 2-4 pages of content

3. **Save PRD to Project**:
   - Create filename: `YYYY-MM-DD-[feature-slug].md`
   - Save to: `docs/prds/[filename]`
   - Create workspace: `.claude/prd-workspace/[feature-slug]/`
   - Update PRD index: `docs/prds/index.md`

## PRD Structure:

### 1. Executive Summary
- Problem statement (why this matters)
- Proposed solution (high level)
- Expected impact (business value)

### 2. Background & Context
- Current state analysis
- Pain points with evidence
- Market/competitive analysis (if relevant)

### 3. Goals & Non-Goals
- **Goals**: Specific objectives (SMART)
- **Non-Goals**: Explicit scope boundaries
- **Success Metrics**: How we measure success

### 4. User Stories / Use Cases
- Primary user flows
- Edge cases to consider
- User personas affected

### 5. Requirements
- **Functional Requirements**: What it must do
- **Non-Functional Requirements**: Performance, security, scalability
- **Technical Requirements**: Platform, integration needs

### 6. Design Considerations
- UI/UX implications
- API design principles
- Data model impacts

### 7. Implementation Plan
- High-level phases
- Dependencies and blockers
- Risk mitigation

### 8. Timeline & Resources
- Effort estimation (T-shirt sizes ok)
- Team/skill requirements
- Major milestones

### 9. Open Questions
- Decisions needed
- Assumptions to validate
- Research required

## Format Requirements:
- Use clear headings and sections
- Include diagrams where helpful
- Keep language accessible to non-technical stakeholders
- Version and date the document
- Add revision history for changes

## Quality Checklist:
- [ ] Can a new team member understand the feature?
- [ ] Are success criteria measurable?
- [ ] Have we identified major risks?
- [ ] Is scope clearly defined?
- [ ] Would this survive a design review?

## Post-Creation Output:
After saving, display:
```
✓ PRD saved to: docs/prds/YYYY-MM-DD-[feature-slug].md
✓ Workspace created: .claude/prd-workspace/[feature-slug]/
✓ Added to PRD index

Next steps:
- To decompose: /prd-decompose [feature-slug]
- To share: Share docs/prds/YYYY-MM-DD-[feature-slug].md
- To review: Schedule design review with stakeholders
```