# AI Agent Development System for LitSearch

This directory contains 10 specialized AI agents for developing and improving the Literature Search Application. Each agent handles a specific aspect of the product development workflow.

## Quick Start

1. **Check current project state** with Agent 0 (Orchestrator)
2. **Follow the recommended next action**
3. **Save outputs** to the `artifacts/` directory
4. **Return to Agent 0** after completing major milestones

## Agent Directory

| Agent | File | Use When | Output |
|-------|------|----------|--------|
| **Agent 0** | [agent-0-orchestrator.md](agent-0-orchestrator.md) | Need direction, planning v0.2, feeling stuck | Status + next actions |
| **Agent 1** | [agent-1-problem-framer.md](agent-1-problem-framer.md) | Defining new features or pivoting | `artifacts/problem-brief-v0.X.md` |
| **Agent 2** | [agent-2-competitive-mapper.md](agent-2-competitive-mapper.md) | Analyzing competitors (Zotero, Mendeley, etc.) | `artifacts/competitive-analysis-v0.X.md` |
| **Agent 3** | [agent-3-product-manager.md](agent-3-product-manager.md) | Scoping features for next version | `artifacts/prd-v0.X.md` |
| **Agent 4** | [agent-4-ux-designer.md](agent-4-ux-designer.md) | Designing user flows and UI | `artifacts/ux-flows-v0.X.md` |
| **Agent 5** | [agent-5-system-architect.md](agent-5-system-architect.md) | Technical architecture decisions | `artifacts/architecture-v0.X.md` |
| **Agent 6** | [agent-6-engineer.md](agent-6-engineer.md) | Implementing features | Code in `src/`, `backend/`, `frontend/` |
| **Agent 7** | [agent-7-qa-engineer.md](agent-7-qa-engineer.md) | Testing and quality assurance | `artifacts/test-plan-v0.X.md` + tests |
| **Agent 8** | [agent-8-devops.md](agent-8-devops.md) | Deployment and CI/CD | `artifacts/deployment-plan-v0.X.md` |
| **Agent 9** | [agent-9-analytics.md](agent-9-analytics.md) | Measuring and growth | `artifacts/analytics-plan-v0.X.md` |

## Current Project Context

**LitSearch v1.0 Status:** Production Ready

**Completed:**
- Multi-source search (7 sources: PubMed, arXiv, Crossref, Scholar, WoS, Semantic Scholar, OpenAlex)
- Intelligent deduplication
- Smart ranking
- ResearchRabbit-style discovery features
- Citation network visualization
- UCSB library authentication
- Modern React UI with themes
- PDF retrieval and extraction

**Tech Stack:**
- Backend: Python 3.10+, FastAPI, SQLAlchemy, SQLite
- Frontend: React 19, Vite, React Router, Axios
- Search: 7 integrated API sources

## Typical Workflow for v0.2

### Planning Phase (1-2 days)
```
1. Agent 0 (Orchestrator) → Get current status, identify gaps
2. Agent 1 (Problem Framer) → Define new features/improvements
3. Agent 3 (Product Manager) → Write PRD for v0.2
```

### Design Phase (1-2 days)
```
4. Agent 4 (UX Designer) → Design new flows
5. Agent 5 (Architect) → Plan technical changes
```

### Build Phase (1-2 weeks)
```
6. Agent 6 (Engineer) → Implement features
7. Agent 7 (QA) → Write tests, verify quality
```

### Deploy Phase (1 day)
```
8. Agent 8 (DevOps) → Deploy updates
9. Agent 9 (Analytics) → Instrument new features
```

## How to Use

### Option 1: Copy-Paste to Claude
1. Open the agent file
2. Copy the system prompt
3. Paste into Claude conversation
4. Provide required inputs
5. Save output to artifacts

### Option 2: Claude Projects
1. Create a Project in Claude
2. Add agent prompts as custom instructions
3. Upload relevant artifacts as context

### Option 3: Automated (Future)
Use with LangChain, CrewAI, or similar frameworks.

## Validation Gates

Before proceeding to the next phase, verify:

### Gate 1: Feature Definition Complete
- [ ] Problem is specific and tied to user need
- [ ] Success metrics are measurable
- [ ] Scope is realistic for timeline

### Gate 2: Design Complete
- [ ] PRD has ≤8 MUST features
- [ ] UX flows cover all features
- [ ] Architecture supports requirements

### Gate 3: Code Complete
- [ ] All MUST features implemented
- [ ] Tests pass (70%+ coverage)
- [ ] No critical bugs

### Gate 4: Launch Ready
- [ ] Deployed successfully
- [ ] Monitoring configured
- [ ] Analytics instrumented

## Project-Specific Context

When invoking any agent, provide:

```markdown
## Project Context

**Product:** Literature Search Application
**Target Users:** Graduate students, postdocs, faculty researchers
**Current State:** v1.0 production ready

**Tech Stack:**
- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: React 19 + Vite + React Router
- Search APIs: PubMed, arXiv, Crossref, Google Scholar, WoS, Semantic Scholar, OpenAlex

**Key Files:**
- PRD: docs/PRD.md
- Backend: backend/main.py (30+ endpoints)
- Frontend: frontend/src/pages/ (6 pages)
- Search: src/search/ (7 providers)
- Models: src/models.py, src/database/models.py

**Current Priorities:**
[List your current priorities here]

**Constraints:**
- Solo developer
- Free/low-cost infrastructure
- Must maintain backward compatibility
```

## Getting Help

- **Stuck?** Use Agent 0 (Orchestrator) to get unstuck
- **Unclear output?** Ask follow-up questions
- **Wrong agent?** Check the "Use When" column above
- **Need to cut scope?** Return to Agent 3 (PM)

## Next Steps

To start improving LitSearch v0.2:

1. Copy the Agent 0 prompt from [agent-0-orchestrator.md](agent-0-orchestrator.md)
2. Paste into Claude
3. Provide your current priorities and concerns
4. Follow the recommended actions
