# Claude Code Rules for ZeroTask

## PRD Governance

### 🔒 PRD Lock Policy
- **PRD.md is IMMUTABLE once development starts** (post v0.1.0)
- No modifications to PRD.md allowed after project launch
- All scope changes must go through proper change management process

### 📋 Pre-Development Checklist
Before writing any code, Claude must:
1. ✅ Read and understand the complete PRD.md
2. ✅ Verify all requirements are clear and implementable
3. ✅ Identify any ambiguities or missing details
4. ✅ Request clarification from user if needed
5. ✅ Confirm PRD is complete and ready for implementation

### 🔄 Scope Change Process
If Claude identifies need for scope changes during development:

1. **STOP coding immediately**
2. Document the proposed change with:
   - Current requirement (from PRD)
   - Proposed new requirement
   - Justification for change
   - Impact assessment (timeline, complexity)
3. Request user approval for scope change
4. If approved, update CHANGELOG.md with:
   - Version bump (following semantic versioning)
   - Detailed change description in appropriate section
   - Reference to original PRD requirement
5. Only proceed with implementation after changelog is updated

## Development Rules

### 🔍 Research-First Development Protocol
**CRITICAL**: Always research requirements thoroughly before implementing major changes.

**Before ANY significant implementation:**
1. ✅ Research API documentation and best practices for the technology
2. ✅ Use WebSearch tool to verify requirements make technical sense
3. ✅ Consider if there are simpler solutions (configuration vs code changes)
4. ✅ Question whether requirements fit development vs production context
5. ✅ Validate that complex implementations are truly necessary

**Examples of research-required changes:**
- Adding HTTPS/SSL configurations
- Implementing new authentication flows
- Making architectural changes (databases, servers, protocols)
- Adding external service integrations
- Security implementations

**Research Tools Available:**
- WebSearch for official documentation
- WebFetch for specific API documentation pages
- Task tool with specialized agents for domain expertise

**When user provides error messages:**
- Research the error in official documentation first
- Verify if the requirement is actually needed for development environment
- Consider configuration-based solutions before code changes

### 🎯 Implementation Fidelity
- Implement exactly what's specified in PRD.md
- No feature creep or "improvements" without explicit approval
- Follow architecture decisions specified in PRD
- Respect non-goals and MVP limitations

### 📝 Documentation Standards
- All code changes must reference PRD sections (e.g., "Implements PRD 5.1 Connectors")
- Use CHANGELOG.md format for all change documentation
- Include impact assessment for any deviations
- Maintain traceability between code and requirements

### 🚨 Exception Handling
If Claude encounters technical blockers during implementation:
1. Document the blocker and attempted solutions
2. Propose alternative approaches that maintain PRD compliance
3. Request user guidance before deviating from PRD specifications
4. Update changelog if alternative approach is approved

## Quality Gates

### Before Each Milestone
- [ ] All PRD requirements for milestone implemented
- [ ] No undocumented scope changes
- [ ] CHANGELOG.md updated with all changes
- [ ] Code matches PRD architecture decisions
- [ ] Acceptance criteria from PRD verified

### Code Review Standards
- Reference specific PRD sections in commit messages
- Verify implementation matches PRD specifications
- Check that data engineering requirements (Section 7) are followed
- Ensure no scope creep beyond defined MVP boundaries

## Available Specialized Agents

### 🎨 ui-ux-designer
**Use for**: Daily brief UI, card layouts, action buttons, responsive design
**ZeroTask Context**: PRD Section 10 (UX Flows), card component design, accessibility
**Example**: "Design the daily brief card component following PRD UX specifications"

### 🏗️ backend-system-architect  
**Use for**: API architecture, OAuth flows, service design, scalability planning
**ZeroTask Context**: PRD Section 8 (Architecture), connector design, security patterns
**Example**: "Review the FastAPI + SQLite architecture for ZeroTask following PRD specs"

### 🔒 data-pipeline-security-engineer
**Use for**: Data deduplication, encryption, compliance, pipeline monitoring
**ZeroTask Context**: PRD Section 7 (Data Engineering Requirements), token security
**Example**: "Implement secure token storage following PRD privacy requirements"

### 📚 lessons-learned-documentor
**Use for**: Capturing development mistakes, documenting better approaches, knowledge sharing
**ZeroTask Context**: Development insights, architecture learnings, troubleshooting experiences
**Example**: "Document the lesson learned from switching to shared service accounts vs individual tokens"
**Auto-triggered when**: User mentions mistakes, discoveries, or reflects on development experiences

**Output Location**: 
- **Primary File**: `LESSONS_LEARNED.md` (root directory)
- **Format**: Markdown with timestamped entries, categorized by topic
- **Structure**: Date, Category, Lesson Title, Description, Impact, Prevention
- **Categories**: Architecture, Environment, Dependencies, Security, UX/UI, Development Process

## Agent Usage Protocol

### 🤖 Automatic Agent Invocation
Claude Code should **proactively call agents** in these scenarios:

**ui-ux-designer**:
- User requests UI/UX design guidance
- Building new components or layouts  
- Interface improvements needed
- User mentions design patterns or user experience

**backend-system-architect**:
- Designing APIs or system architecture
- Security implementation questions
- Scalability and performance concerns
- Database design decisions

**data-pipeline-security-engineer**:
- Working with sensitive data or tokens
- Implementing encryption or security measures
- Data pipeline design or ETL processes
- Compliance or privacy requirements

**lessons-learned-documentor** (PROACTIVE):
- User mentions making a mistake
- User discovers a better approach
- User learns something new during development
- Unexpected issues arise during coding
- User reflects on development experiences
- Architecture decisions prove suboptimal

**Documentation Requirements**:
- Create/append to `LESSONS_LEARNED.md` in project root
- Use structured format with categories and timestamps
- Reference specific files, functions, or PRD sections when applicable
- Include prevention strategies for future development

### 🔧 Manual Agent Guidelines
1. **Consult agents for domain expertise** on complex implementations
2. **Always reference PRD sections** when calling agents
3. **Agents must follow PRD constraints** (local-first, privacy, MVP scope)
4. **Update CHANGELOG.md** if agent recommendations require scope changes
5. **Integrate agent guidance** with overall ZeroTask architecture

## Development Environment Setup

### 🐍 Python Backend Environment
**CRITICAL**: Always activate the Python virtual environment before running backend code or tests.

**Windows Command:**
```bash
cd zerotask-backend && venv\Scripts\activate
```

**Required before ANY backend operations:**
- Installing Python packages (`pip install`)
- Running FastAPI server (`uvicorn app.main:app`)
- Running database migrations (`alembic upgrade head`)
- Running backend tests (`pytest`)
- Any Python script execution

### 🌐 Frontend Environment
**Frontend runs in Node.js (no virtual environment needed):**
```bash
cd zerotask-frontend && npm run dev
```

## Environment File Safety Guidelines

### 🔒 .env File Protection Protocol
**CRITICAL**: Always check existing .env files before creating or modifying them.

**Before ANY .env file operations:**
1. ✅ Use Read tool to check if .env file exists in target directory
2. ✅ Review existing .env content completely
3. ✅ Only add/modify specific variables requested by user
4. ✅ NEVER overwrite entire .env file unless explicitly confirmed by user
5. ✅ Preserve ALL existing environment variables and comments

**Modification Process:**
- Use Edit tool for targeted changes to specific variables
- Use MultiEdit tool for multiple variable updates in same file
- Create backup mental note of original content before changes
- If complete rewrite needed, explicitly ask user for confirmation

**Emergency Protocol:**
- If .env file accidentally overwritten, immediately restore from memory
- Ask user to verify restored content matches their expectations
- Document the incident for future prevention

## Environment Validation
Before coding, Claude must verify:
1. ✅ Backend venv is activated (check for `(venv)` in terminal prompt)
2. ✅ Frontend dependencies are installed (`node_modules/` exists)
3. ✅ Required services running (Ollama for LLM, database accessible)
4. ✅ Existing .env files read and preserved (if working with environment configs)

## Enforcement
- Claude will refuse to implement features not in PRD without proper change process
- All scope discussions must result in CHANGELOG.md updates before coding
- PRD.md remains the single source of truth for project requirements
- User approval required for any deviations from PRD specifications
- Specialized agents must maintain PRD compliance in their recommendations
- **Claude must activate Python venv before any backend operations**

---
*This file ensures ZeroTask development maintains strict adherence to documented requirements and proper change management practices.*