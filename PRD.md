# ZeroTask - Product Requirements Document

## PRD — "Daily Brief (Local)": A Privacy-First Cross-App Summary for Gmail, Slack & GitHub

### 0) One-liner

A local-first desktop/web app that pulls your Gmail, Slack, and GitHub items, deduplicates overlaps, and generates an action-ready daily brief with evidence links—running entirely on the user’s machine with Bring-Your-Own-Key (BYOK) LLM support (or fully local via Ollama).

### 1) Problem Statement

Knowledge workers lose 30–90 minutes each day triaging across email, Slack, and GitHub. Existing tools summarize within each product but don’t:

Consolidate across apps

Remove duplicates (e.g., the same PR appears in email & Slack)

Prioritize by role/ownership

Let users act (reply, assign, snooze) from a single view

Respect strict privacy needs without centralizing data

We’ll ship a small, privacy-safe tool that lives on the user’s laptop, keeps data local, and provides one trustworthy “what matters today” brief.

2) Goals & Non-Goals

#### Goals (MVP)

Single “Daily Brief” summarizing:

Gmail: today’s important threads + decision requests

Slack: @mentions and unread replies in chosen channels

GitHub: assigned issues/PRs & requested reviews

Deduplication across surfaces (email ↔ Slack ↔ GitHub) into one card per topic

Action-ready cards: open source item, create Gmail draft reply, mark follow-up, snooze

Evidence links: every bullet cites the exact email/Slack message/PR line

Local-first & BYOK:

Runs on localhost (or Docker)

Users paste their own LLM API key or select a fully local model via Ollama

All tokens & data stored locally; no central server

Non-#### Goals (MVP)

No auto-sending emails or Slack messages (draft/reply suggestions only)

No company-wide admin console or centralized storage

No calendar/Docs integration (considered for vNext)

No complex team analytics—focus on personal productivity first

3) Users & Personas

IC Engineer / Analyst: wants a 5-minute morning sweep; cares about PRs/mentions

Tech Lead / Manager: needs a prioritized digest across repos/channels for decisions

PM / Ops: quickly identify decision requests and blockers from long threads

**Deployment Context**: Company internal team use (5-50 users)
Primary environment: laptop (Linux/macOS/Windows). Data sensitivity: high.

**Authentication Model**: Shared service account managed by IT team for simplified deployment and consistent permissions across all users.

4) Key Use Cases (MVP)

Morning Brief (auto at 9am or on demand): “Show me what I missed and what needs my action.”

On-demand Summarize: “/brief” in Slack posts a personal recap card.

Thread→Action: From a card, open source item, create a Gmail draft reply, add a follow-up, or snooze to tomorrow.

Noise Control: Mute specific channels/repos; only show @mentions & assigned items.

5) Functional Requirements
5.1 Connectors (read-only for MVP)

Slack: fetch unread messages in selected channels where user is @mentioned; fetch thread context. Socket Mode (no public URL).

Gmail: fetch today’s messages + recent long threads; read metadata/snippets; create draft replies.

GitHub: list assigned issues/PRs and requested reviews; pull PR titles/descriptions, changed files summary.

5.2 Summarization & Ranking

Generate a single, deduped list of cards:

Group items by canonical URL/thread (e.g., PR URL, Gmail threadId, Slack permalink)

Priority score (simple v1): @mention + ownership + due date + recency

LLM summaries must quote source snippets & include deep links (no “naked” claims)

5.3 Actions (MVP)

Open source (Gmail thread / Slack message / GitHub PR) in the browser/native app

Draft Reply (Gmail only): prefill body; user must review & send in Gmail

Add Follow-Up: lightweight local todo with due-date; shown in tomorrow’s brief

Snooze to tomorrow

5.4 Preferences

Choose LLM provider: Ollama (local) or BYOK (OpenAI/Anthropic/etc. via LiteLLM)

Choose sources (which Slack channels/repos, Gmail labels)

Schedule (daily time) & “only show @mentions/assigned”

6) Non-Functional Requirements

Privacy: all data & tokens local by default; remote LLMs allowed only via user-provided keys

Security: encrypt tokens at rest (OS Keychain preferred; fallback = local encryption with passphrase)

Reliability: brief generation < 10 seconds median (cached fetch + fast summarization)

Portability: cross-platform; simple docker-compose up or single script

7) Data Engineering Requirements

#### 7.1 Data Pipeline Stability
- **Error handling & retries**: Exponential backoff for API failures (Slack/Gmail/GitHub rate limits)
- **Incremental sync strategy**: Only fetch new/changed items since last run using timestamps/cursors
- **Data validation schemas**: Pydantic models to ensure connector responses match expected format
- **Graceful degradation**: Generate partial briefs if one connector fails (mark unavailable sources)
- **Dead letter queue**: Store failed items for manual review/retry

#### 7.2 Data Consistency & Integrity
- **Transaction boundaries**: Atomic updates to cards/events tables using SQLite transactions
- **Schema migration strategy**: Alembic-style migrations for SQLite schema changes
- **Data deduplication integrity**: Consistent hashing for canonical URL identification
- **Referential integrity**: Foreign key constraints between events/cards/todos tables
- **Backup/recovery**: Export/import functionality for critical user data (tokens, preferences)

#### 7.3 Performance & Caching
- **LLM response caching**: Cache summarization results by content hash (24hr TTL)
- **API response caching**: Cache connector responses to reduce API calls during development
- **Batch processing**: Process multiple items in single LLM calls when possible
- **Connection pooling**: Reuse HTTP connections for API clients
- **Lazy loading**: Only fetch full content when generating summaries

#### 7.4 Monitoring & Observability
- **Pipeline health checks**: Monitor connector status, API quotas, processing times
- **Data quality metrics**: Track deduplication accuracy, summary hallucinations, broken links
- **Performance metrics**: p50/p95 processing times, cache hit rates, API response times
- **Alert thresholds**: Failed syncs >3 consecutive, processing timeout >30s
- **Audit logging**: All user actions (snooze, draft, follow-up) logged with timestamps

#### 7.5 Data Governance
- **Data retention policies**: Auto-delete events older than 30 days, keep cards for 7 days
- **Privacy compliance**: Clear data lineage, ability to purge user data completely
- **Secret management**: Encrypted token storage with key rotation capability
- **Access patterns**: Read-only API access with minimal required scopes
- **Data export**: Structured export of all user data in portable formats

### 8) Architecture (MVP)

Process model (local):

UI: Next.js (http://localhost:3000
) or simple React SPA

API: FastAPI or Node/Express (http://localhost:8000
)

Jobs: lightweight scheduler (APScheduler / cron) to poll sources every N minutes and at daily time

Storage: SQLite (or DuckDB) file in app data dir; small events, cards, prefs, tokens, todos tables

LLM:

Option A: Ollama (fully on-device)

Option B: LiteLLM local proxy → user’s provider (BYOK)

No telemetry by default; optional opt-in

Auth specifics (Company Deployment):

**Shared Service Account Approach:**

Slack: Company-wide Slack app with Socket Mode tokens managed by IT team
- One app for entire organization
- Bot has access to relevant channels/workspaces
- Scopes: app_mentions:read, channels:history, chat:write, im:history

GitHub: Service account with organization access managed by IT team
- Single GitHub service account with repo access across relevant repositories
- Scopes: repo (read), read:user, notifications
- IT manages token rotation and permissions

Gmail: Company OAuth application (when implemented)
- Company-registered OAuth client
- Desktop flow redirects to localhost
- Scopes: gmail.readonly, gmail.compose (draft only)

9) Data Model (sketch)
tokens(id, provider, encrypted_token, created_at, updated_at)
prefs(user_id, llm_provider, model, slack_channels[], github_repos[], gmail_labels[], show_only_mentions boolean, daily_time)
events(id, source, source_id, url, title, snippet, author, ts, raw_json)
links(event_id, related_event_id)  -- for dedupe mapping across sources
cards(id, primary_event_id, priority_score, summary_md, evidence_links[], created_at)
todos(id, card_id, title, due_date, status)
runs(id, started_at, finished_at, status, stats_json)  -- audit log


Dedupe rule (v1):

If two events share the same canonical URL (GitHub PR), or Slack message contains that URL or Gmail snippet contains it → merge into one card with multiple evidence_links.

### 10) UX Flows

#### IT Setup (One-Time Company Configuration)

IT team sets up shared service accounts:

**Slack Setup:**
- Create company Slack app "ZeroTask" with Socket Mode
- Generate App Token (xapp-) and Bot Token (xoxb-)
- Install app to company workspace with required scopes
- Configure tokens in ZeroTask deployment configuration

**GitHub Setup:**
- Create service account (e.g., "zerotask-bot@company.com")
- Add service account to relevant GitHub organization/repositories
- Generate Personal Access Token with required scopes
- Configure token in ZeroTask deployment configuration

**Gmail Setup (Future):**
- Register company OAuth application with Google Cloud
- Configure OAuth credentials for desktop flow

#### First-Run Setup (End Users)

User launches app → chooses LLM: Ollama (default) or BYOK key(s)

Sources are pre-configured by IT (no individual tokens needed)

Select which Slack channels to include in brief

Select which GitHub repositories to monitor

Set personal brief time (default 9:00 AM) → generate first brief

Daily Brief

Open app or type /brief in Slack → personal card list appears

Each card shows: title, 2–4 bullet summary with quoted snippets, icons for sources, and buttons: Open, Draft Reply (if email), Follow-Up, Snooze

“View sources” reveals direct deep links

### 11) Security, Privacy & Compliance

Local-first: email/Slack/PR content stored locally; users may wipe data via “Reset & Wipe”

BYOK: users managing their own API keys; clear indicator when remote LLM is used

Scopes minimization: smallest necessary read scopes; Gmail draft-only (no send)

Logs: local only; runs table contains minimal metadata (counts & timings); no content unless user opts in to debugging

Backups: none by default; user can export/import settings

### 12) Metrics & Success Criteria (Pilot)

Adoption: ≥70% of pilot users run the brief daily by end of week 2

Time Saved: median self-reported ≥15 min/day

Quality: ≥90% of cards have working deep links; <1% user-reported hallucinations

Reliability: p50 brief generation ≤10s; p95 ≤20s

Safety: 0 unintended sends; 100% actions logged locally

Exit criteria (MVP “done”)

All connectors working on macOS & Windows

Dedupe working for PR shared in Slack + email

Gmail draft creation successful from a card

Evidence links present for every summary bullet

### 13) Release Plan

Milestone 1 (Week 1):

Slack + GitHub only; /brief Slack command; local LLM (Ollama)

Basic cards + Open/Snooze; dedupe by URL; manual run button

Milestone 2 (Week 2):

Add Gmail read + draft-only replies

Priority score; daily scheduled brief; “Follow-Up” (local todos)

Milestone 3 (Week 3):

Preferences UI; mute rules; export brief to Markdown

Optional BYOK via LiteLLM; encrypted token storage; wipe/reset flow

### 14) Risks & Mitigations

OAuth friction (Gmail) → step-by-step guide, Desktop OAuth client, retry hints

Model latency on local hardware → small context windows; summarize per-source first, then fuse; use templates

Over-summarization → hard rule: include quoted snippets + links; user trust > brevity

Token safety → prefer OS Keychain; otherwise encrypt at rest with user passphrase

Scope creep → keep calendar/docs/integrations out of MVP

### 15) Open Questions

Minimum OS support set for pilot (macOS only vs add Windows/Linux)?

Which Gmail labels to include by default (INBOX, STARRED?)

Do we allow Slack DMs in MVP or channels only?

Which local model defaults best balance speed/quality (e.g., llama3:8b)?

Should we offer a headless mode that posts the brief only to Slack?

### 16) Appendix
#### 16.1 Example .env (local dev)
# LLM (choose one)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
LITELLM_BASE_URL=http://localhost:4000
OLLAMA_BASE_URL=http://localhost:11434

# Slack (Socket Mode)
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...

# Gmail (Desktop OAuth)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/oauth2/callback

# GitHub
GITHUB_TOKEN=

#### 16.2 Minimal API Endpoints
GET  /health
POST /auth/slack/connect
POST /auth/github/connect
GET  /auth/google/start
GET  /auth/google/callback
POST /brief/run              # on-demand execution
GET  /brief/latest           # fetch last brief (cards)
POST /cards/:id/draft_reply  # Gmail draft
POST /cards/:id/followup
POST /cards/:id/snooze
GET  /prefs
POST /prefs
POST /wipe                   # reset & wipe local data

#### 16.3 Required OAuth Scopes (MVP)

Slack: app_mentions:read, channels:history (selected), chat:write (IM to user), Socket Mode

Gmail: gmail.readonly, gmail.compose (draft only)

GitHub: repo (read), read:user, notifications

### 17) Crisp MVP Acceptance Tests

 After first-run setup, clicking Run Brief retrieves items from all three sources

 A GitHub PR shared in Slack and mentioned in an email appears as one card with both sources listed

 Each summary bullet expands to show quoted text and a deep link to the exact source

 Clicking Draft Reply opens a Gmail draft prefilled with suggested text

 Snoozed card disappears from today and reappears tomorrow

 With Ollama selected and no internet, the brief still generates from cached content