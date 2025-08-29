# ZeroTask Subagent Architecture

## Overview
Domain-specific subagents configured in `.claude/agents/` for specialized knowledge during development. These agents are called automatically by Claude Code when their expertise is needed.

## Active Subagents

### 1. **ui-ux-designer** ✅
**Domain**: User Interface & User Experience Design
**Responsibilities**:
- Component layouts and design system recommendations
- User interface improvements and modern design patterns
- Dashboard and navigation design
- Responsive design and accessibility
- Design consistency and user flow optimization

**Auto-triggered when**: User requests UI/UX design guidance, component layouts, or interface improvements.

### 2. **backend-system-architect** ✅
**Domain**: Backend Architecture & System Design
**Responsibilities**:
- Microservices architecture design
- API design and system scalability
- Security best practices in backend systems
- Database design and data flow architecture
- Integration patterns and system reliability

**Auto-triggered when**: User needs backend system design, API architecture review, or system scalability guidance.

### 3. **data-pipeline-security-engineer** ✅
**Domain**: Data Pipeline Security & Compliance
**Responsibilities**:
- Data pipeline design with security focus
- ETL processes for sensitive data
- Data encryption and access controls
- GDPR/HIPAA compliance in data workflows
- Security audits of data infrastructure

**Auto-triggered when**: User works with data pipelines, sensitive data processing, or needs compliance guidance.

### 4. **lessons-learned-documentor** ✅ **(NEW)**
**Domain**: Technical Documentation & Knowledge Capture
**Responsibilities**:
- Capturing development mistakes and insights
- Documenting better approaches discovered during development
- Creating actionable guidance from development experiences
- Organizing lessons by technology and problem domain
- Preventing future issues through knowledge sharing

**Auto-triggered when**: User mentions making a mistake, discovering a better approach, learning something new, or explicitly reflects on lessons learned.

## How Claude Code Subagents Work

### Automatic Agent Detection
Claude Code automatically detects when to call subagents based on:
- **Context analysis** of user requests
- **Keyword triggers** in the agent descriptions
- **Domain expertise** required for the task
- **Code patterns** and implementation needs

### Agent Communication Flow
```
1. User makes a request requiring specialized knowledge
2. Claude Code analyzes the context and domain requirements
3. Appropriate subagent is automatically invoked via Task tool
4. Subagent provides specialized implementation/guidance
5. Claude integrates response and continues development
6. Updates todo list and project documentation
```

### Cross-Domain Coordination Examples
- **ui-ux-designer** + **backend-system-architect**: Full-stack feature design
- **data-pipeline-security-engineer** + **backend-system-architect**: Secure data architecture
- **lessons-learned-documentor**: Called after any significant development insight
- **ui-ux-designer**: Dashboard and component design decisions

## Integration with ZeroTask Development

### Current Implementation (Milestone 1) ✅
- `backend-system-architect`: Designed FastAPI + SQLite architecture
- `ui-ux-designer`: Created sidebar navigation and Sources UI
- `data-pipeline-security-engineer`: Implemented shared service account security

### Next Phase (Milestone 2)
- `backend-system-architect`: Gmail OAuth integration architecture
- `data-pipeline-security-engineer`: Data deduplication and privacy compliance
- `ui-ux-designer`: Daily brief card design and action buttons
- `lessons-learned-documentor`: Capture development insights as they occur

### Future Phase (Milestone 3)
- `backend-system-architect`: Background job scheduling and API optimization
- `ui-ux-designer`: Advanced preferences and export features
- `data-pipeline-security-engineer`: Data export/wipe functionality
- `lessons-learned-documentor`: Comprehensive development knowledge base

## Agent Quality Standards
Each subagent provides:
- ✅ **PRD-compliant solutions** referencing specific sections
- ✅ **Security-first approach** maintaining local-first architecture
- ✅ **Production-ready code** with proper error handling
- ✅ **Clear documentation** and implementation guidance
- ✅ **Future-proof designs** following established patterns

## Proactive Learning with lessons-learned-documentor
The lessons-learned-documentor agent is **proactively triggered** when:
- Development mistakes are mentioned or discovered
- Better approaches are found during implementation
- Unexpected issues arise and are resolved
- Performance problems are identified and fixed
- Architecture decisions prove suboptimal
- Security vulnerabilities are found and patched

This ensures continuous learning and knowledge capture throughout the development process.

---
*These subagents provide specialized expertise while maintaining consistency with ZeroTask's architecture and security requirements.*