# ZeroTask Subagent Architecture

## Overview
Domain-specific subagents to be called via Claude Code's Task tool for specialized knowledge during development.

## Core Domain Subagents

### 1. **api-connector-specialist**
**Domain**: API Integration & OAuth
**Responsibilities**:
- Slack Socket Mode implementation
- Gmail OAuth Desktop flow
- GitHub API integration
- Rate limiting and retry logic
- Token management and encryption

**Usage Pattern**:
```
Task(
    subagent_type="api-connector-specialist",
    description="Implement Slack connector",
    prompt="Implement Slack Socket Mode connector following PRD 5.1 specs..."
)
```

### 2. **data-pipeline-engineer**
**Domain**: Data Processing & ETL
**Responsibilities**:
- SQLite schema design and migrations
- Event deduplication logic
- Data validation pipelines
- Incremental sync strategies
- Transaction management

**Usage Pattern**:
```
Task(
    subagent_type="data-pipeline-engineer", 
    description="Design deduplication system",
    prompt="Implement event deduplication following PRD section 8 data model..."
)
```

### 3. **llm-integration-specialist**
**Domain**: LLM Integration & Summarization
**Responsibilities**:
- Ollama local LLM setup
- LiteLLM BYOK integration
- Prompt engineering for summaries
- Response caching strategies
- Context window management

**Usage Pattern**:
```
Task(
    subagent_type="llm-integration-specialist",
    description="Setup Ollama integration", 
    prompt="Configure Ollama for local summarization following PRD 7.3..."
)
```

### 4. **frontend-architect**
**Domain**: Next.js UI/UX Implementation
**Responsibilities**:
- Next.js component architecture
- Daily brief UI design
- Action buttons (draft, snooze, follow-up)
- Real-time updates
- Responsive design

**Usage Pattern**:
```
Task(
    subagent_type="frontend-architect",
    description="Build daily brief UI",
    prompt="Create daily brief card component following PRD UX flows..."
)
```

### 5. **security-compliance-expert**
**Domain**: Security & Privacy
**Responsibilities**:
- Token encryption at rest
- OS Keychain integration
- OAuth security best practices
- Data privacy compliance
- Local-first architecture validation

**Usage Pattern**:
```
Task(
    subagent_type="security-compliance-expert",
    description="Implement token encryption",
    prompt="Design secure token storage following PRD security requirements..."
)
```

### 6. **devops-reliability-engineer**
**Domain**: Deployment & Monitoring
**Responsibilities**:
- Docker containerization
- Cross-platform compatibility
- Performance monitoring
- Health checks
- Backup/recovery procedures

**Usage Pattern**:
```
Task(
    subagent_type="devops-reliability-engineer",
    description="Setup Docker deployment",
    prompt="Create docker-compose setup for local deployment..."
)
```

### 7. **test-automation-specialist**
**Domain**: Testing & Quality Assurance
**Responsibilities**:
- Unit test strategies
- Integration test design
- Mock API responses
- End-to-end test scenarios
- Performance testing

**Usage Pattern**:
```
Task(
    subagent_type="test-automation-specialist",
    description="Create connector tests",
    prompt="Design test suite for API connectors with mocked responses..."
)
```

## Subagent Interaction Protocol

### When to Use Subagents
1. **Complex domain-specific implementation** (>50 lines of specialized code)
2. **Architecture decisions** requiring domain expertise
3. **Integration challenges** with external services
4. **Security-critical implementations**
5. **Performance optimization** tasks

### Subagent Communication Flow
```
1. Claude identifies domain-specific task
2. Calls appropriate subagent via Task tool
3. Subagent provides specialized implementation/guidance
4. Claude integrates response with overall project
5. Updates todo list and continues development
```

### Cross-Domain Coordination
- **api-connector-specialist** + **security-compliance-expert**: OAuth implementation
- **data-pipeline-engineer** + **llm-integration-specialist**: Summary caching
- **frontend-architect** + **devops-reliability-engineer**: Production deployment

## Integration with Development Workflow

### Milestone 1 Subagents
- `api-connector-specialist`: Slack + GitHub connectors
- `llm-integration-specialist`: Ollama setup
- `data-pipeline-engineer`: Basic deduplication
- `frontend-architect`: Basic card UI

### Milestone 2 Subagents
- `api-connector-specialist`: Gmail connector
- `security-compliance-expert`: Token encryption
- `data-pipeline-engineer`: Priority scoring

### Milestone 3 Subagents
- `devops-reliability-engineer`: Docker deployment
- `test-automation-specialist`: End-to-end tests
- `security-compliance-expert`: Data export/wipe

## Quality Gates
Each subagent must:
- ✅ Reference specific PRD sections
- ✅ Follow data engineering requirements (Section 7)
- ✅ Maintain local-first architecture
- ✅ Provide implementation with error handling
- ✅ Include relevant test strategies

---
*This architecture enables specialized domain expertise while maintaining PRD compliance and architectural consistency.*