# LitSearch Agent Workflow Integration

## Overview

This document defines how the 10 agents work together to develop and improve the Literature Search Application.

---

## Workflow Timeline

**Typical v0.X development cycle: 3-4 weeks**

| Phase | Agents | Duration | Output |
|-------|--------|----------|--------|
| Planning | 0 → 1 → 2 → 3 | 3-5 days | Problem Brief, Analysis, PRD |
| Design | 4 → 5 | 2-3 days | UX Flows, Architecture |
| Build | 6 ↔ 7 | 10-14 days | Code, Tests |
| Launch | 8 → 9 | 1-2 days | Deployment, Analytics |

---

## Agent Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                 AGENT 0: ORCHESTRATOR                    │
│         (Invoke at start, milestones, when stuck)        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              PHASE 1: PLANNING (3-5 days)                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  AGENT 1    │    │  AGENT 2    │    │  AGENT 3    │  │
│  │  Problem    │───▶│  Competitive│───▶│  Product    │  │
│  │  Framer     │    │  Mapper     │    │  Manager    │  │
│  └─────────────┘    └─────────────┘    └──────┬──────┘  │
│                                               │          │
│  ✓ GATE 1: Feature Definition Complete        │          │
│    □ Problem is specific                      │          │
│    □ Differentiation is clear                 │          │
│    □ Scope is realistic                       │          │
└───────────────────────────────────────────────┼──────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────┐
│              PHASE 2: DESIGN (2-3 days)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐           ┌─────────────┐              │
│  │  AGENT 4    │           │  AGENT 5    │              │
│  │  UX         │──────────▶│  Architect  │              │
│  │  Designer   │           │             │              │
│  └─────────────┘           └──────┬──────┘              │
│                                   │                      │
│  ✓ GATE 2: Design Complete        │                      │
│    □ UX flows cover all features  │                      │
│    □ Architecture is feasible     │                      │
│    □ Backward compatible          │                      │
└───────────────────────────────────┼──────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│            PHASE 3: BUILD (10-14 days)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐           ┌─────────────┐              │
│  │  AGENT 6    │◀─────────▶│  AGENT 7    │              │
│  │  Engineer   │           │  QA Engineer│              │
│  └─────────────┘           └──────┬──────┘              │
│                                   │                      │
│  ✓ GATE 3: Code Complete          │                      │
│    □ All MUST features done       │                      │
│    □ Tests pass                   │                      │
│    □ No critical bugs             │                      │
└───────────────────────────────────┼──────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│            PHASE 4: LAUNCH (1-2 days)                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐           ┌─────────────┐              │
│  │  AGENT 8    │──────────▶│  AGENT 9    │              │
│  │  DevOps     │           │  Analytics  │              │
│  └─────────────┘           └──────┬──────┘              │
│                                   │                      │
│  ✓ GATE 4: Launch Ready           │                      │
│    □ Deployed successfully        │                      │
│    □ Monitoring active            │                      │
│    □ Analytics instrumented       │                      │
└───────────────────────────────────┼──────────────────────┘
                                    │
                                    ▼
                         ┌───────────────────┐
                         │   v0.X COMPLETE   │
                         │  Return to Agent  │
                         │  0 for v0.X+1     │
                         └───────────────────┘
```

---

## Handoff Specifications

### Agent 0 → Agent 1
**Orchestrator provides:** Direction and ready-to-use prompt
**Problem Framer needs:** Feature idea, user feedback, constraints

### Agent 1 → Agent 2
**Problem Framer outputs:** `artifacts/problem-brief-v0.X.md`
**Competitive Mapper needs:** Clear target user and pain points

### Agent 2 → Agent 3
**Competitive Mapper outputs:** `artifacts/competitive-analysis-v0.X.md`
**Product Manager needs:** Differentiation strategy, gap analysis

### Agent 3 → Agent 4
**Product Manager outputs:** `artifacts/prd-v0.X.md`
**UX Designer needs:** Feature list with acceptance criteria

### Agent 4 → Agent 5
**UX Designer outputs:** `artifacts/ux-flows-v0.X.md`
**Architect needs:** Screen inventory, component complexity

### Agent 5 → Agent 6
**Architect outputs:** `artifacts/architecture-v0.X.md`
**Engineer needs:** Data model, API design, implementation sequence

### Agent 6 ↔ Agent 7
**Bidirectional:** Engineer implements, QA tests, feedback loop

### Agent 7 → Agent 8
**QA provides:** All tests passing, no critical bugs
**DevOps needs:** Deployable code, env vars documented

### Agent 8 → Agent 9
**DevOps provides:** Running production environment
**Analytics needs:** Access to deploy tracking code

### Agent 9 → Agent 0
**Analytics provides:** Measurement plan, initial data, recommendations
**Orchestrator uses:** Plan v0.X+1 based on learnings

---

## Validation Gates

### Gate 1: Feature Definition Complete
**After:** Agents 1, 2, 3
**Checklist:**
- [ ] Problem statement is specific and testable
- [ ] Target user is clearly defined
- [ ] Competitive positioning is clear
- [ ] PRD has ≤8 MUST features
- [ ] Timeline is realistic

### Gate 2: Design Complete
**After:** Agents 4, 5
**Checklist:**
- [ ] Every PRD feature has UX flow
- [ ] Architecture supports all features
- [ ] Implementation sequence is clear
- [ ] Backward compatibility maintained

### Gate 3: Code Complete
**After:** Agents 6, 7
**Checklist:**
- [ ] All MUST features implemented
- [ ] Test coverage meets targets
- [ ] All tests pass
- [ ] No critical or high bugs
- [ ] Code follows conventions

### Gate 4: Launch Ready
**After:** Agents 8, 9
**Checklist:**
- [ ] Deployed to production
- [ ] Monitoring configured
- [ ] Error tracking active
- [ ] Analytics events firing
- [ ] Rollback procedure tested

---

## Quick Reference: Which Agent Next?

| Current State | Next Agent | Reason |
|---------------|------------|--------|
| Starting new feature | Agent 1 | Define the problem |
| Have problem brief | Agent 2 | Check competition |
| Have analysis | Agent 3 | Scope the feature |
| Have PRD | Agent 4 | Design the UX |
| Have UX flows | Agent 5 | Plan architecture |
| Have architecture | Agent 6 | Start coding |
| Have code | Agent 7 | Test it |
| Tests pass | Agent 8 | Deploy it |
| Deployed | Agent 9 | Measure it |
| Have data | Agent 0 | Plan next iteration |
| Stuck | Agent 0 | Get unstuck |

---

## Artifact Structure

```
litsearchapp/
├── agents/
│   ├── README.md
│   ├── WORKFLOW-INTEGRATION.md
│   ├── agent-0-orchestrator.md
│   ├── agent-1-problem-framer.md
│   ├── agent-2-competitive-mapper.md
│   ├── agent-3-product-manager.md
│   ├── agent-4-ux-designer.md
│   ├── agent-5-system-architect.md
│   ├── agent-6-engineer.md
│   ├── agent-7-qa-engineer.md
│   ├── agent-8-devops.md
│   └── agent-9-analytics.md
│
├── artifacts/
│   ├── problem-brief-v0.2.md
│   ├── competitive-analysis-v0.2.md
│   ├── prd-v0.2.md
│   ├── ux-flows-v0.2.md
│   ├── architecture-v0.2.md
│   ├── test-plan-v0.2.md
│   ├── deployment-plan-v0.2.md
│   └── analytics-plan-v0.2.md
│
├── docs/
│   └── PRD.md (v1.0 reference)
│
├── backend/
├── frontend/
└── src/
```

---

## Error Recovery

### Scenario: Architecture is infeasible
1. Architect documents blocker
2. Return to Agent 3 (PM) to cut scope
3. Update PRD and restart from Agent 4

### Scenario: QA finds critical bug
1. QA documents bug with reproduction
2. Engineer fixes (priority over new features)
3. Retest and continue

### Scenario: Competitive analysis invalidates approach
1. Agent 2 documents conflict
2. Return to Agent 1 to reframe
3. Continue from Agent 2

### Scenario: User feedback contradicts assumptions
1. Agent 9 documents findings
2. Return to Agent 0 for v0.X+1 planning
3. May need Agent 1 reframing

---

## Best Practices

### 1. Always provide context
Include relevant artifacts when invoking an agent.

### 2. Iterate within each agent
First draft → Review → Refine → Approve

### 3. Lock artifacts before proceeding
Get explicit approval before moving to next phase.

### 4. Challenge recommendations
Agents are advisors—push back on scope, complexity.

### 5. Return to Agent 0 regularly
After milestones, when stuck, or when priorities change.

---

## Getting Started with v0.2

1. **Copy Agent 0 prompt** from `agent-0-orchestrator.md`
2. **Paste into Claude** with your priorities
3. **Follow recommended action**
4. **Save outputs** to `artifacts/`
5. **Proceed through phases**
6. **Return to Agent 0** after completion

Good luck building LitSearch v0.2!
