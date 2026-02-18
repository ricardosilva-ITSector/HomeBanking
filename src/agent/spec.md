# HomeBanking Agent Migration Spec

## 1) Objective

Migrate the current HomeBanking Python agent implementation to **Azure AI Foundry Agent Service** so it runs as a **persistent, server-managed agent** with **Foundry-hosted threads**.

This migration keeps the current Python service boundary and preserves the existing banking assistant behavior where possible, while moving conversation state ownership from local process memory to Foundry.

## 2) Confirmed Decisions

- **SDK lane**: Foundry new **2.x preview** track (explicitly chosen)
- **Hosting mode (phase 1)**: persistent managed agent + Foundry-hosted threads via current Python service
- **API contract**: migrate to a new endpoint contract now (no compatibility façade)
- **Thread scope**: per browser session

## 3) Current State (Baseline)

### 3.1 Agent runtime

- Two parallel runtime paths exist:
  - `src/agent/main.py` (Agent Framework adapter/server mode)
  - `src/agent/server.py` (FastAPI service with `/agent/chat` and `/agent/stream`)
- This causes runtime ambiguity and different endpoint surfaces.

### 3.2 Threading behavior

- Frontend currently generates and sends a thread id.
- Server path currently creates a fresh thread context per request in key flows, so continuity is not guaranteed end-to-end.

### 3.3 Tooling

- Banking tools are Python functions in `src/agent/tools.py` and call backend APIs (`/api/accounts`, `/api/transactions`, `/api/transfers`).

### 3.4 Frontend integration

- Agent integration flows through:
  - `src/web/src/services/agentService.ts`
  - `src/web/src/components/ChatWidget.tsx`
  - `src/web/vite.config.ts`

## 4) Target Architecture

### 4.1 Core model

- Foundry owns durable state for:
  - agent identity/lifecycle
  - threads/conversations
  - run execution
- Python service becomes a thin orchestration/API layer that:
  - resolves/creates persistent agent (once, cached)
  - creates/reuses Foundry threads
  - streams run output to frontend
  - maps tool calls and errors to app contracts

### 4.2 High-level request flow

1. Frontend sends message + optional `threadId`
2. Agent service resolves persistent agent id
3. If `threadId` absent, create Foundry thread and return it
4. Append user message to Foundry thread
5. Run agent against thread (streaming)
6. Stream events/tokens back to frontend
7. Return/emit the authoritative Foundry `threadId`

## 5) Migration Scope

### In scope

- Persistent Foundry agent lifecycle and Foundry-hosted thread lifecycle
- New server endpoint contract and matching frontend updates
- Preservation of current banking tool behaviors and transfer confirmation safety gates
- Dependency/version strategy for chosen 2.x preview lane
- Updated docs and env configuration

### Out of scope (phase 1)

- Foundry hosted container runtime (hosted agents capability-host deployment)
- Multi-tenant thread persistence policy beyond per-browser-session
- Major domain changes to transfer/business logic in backend API

## 6) Work Plan

## Phase 0 — Contract and dependency baseline

1. Select authoritative runtime entrypoint (`src/agent/server.py`)
2. Align endpoint contracts and remove ambiguity
3. Pin compatible SDK package set for Foundry 2.x preview lane
4. Update env templates and startup docs

Deliverables:
- `src/agent/requirements.txt` updated with pinned preview-compatible set
- `src/agent/.env.example` updated for Foundry 2.x settings
- `src/agent/README.md` runtime and endpoint surface corrected

## Phase 1 — Persistent agent + thread implementation

1. Introduce Foundry client abstraction module (new)
2. Implement persistent agent resolution/creation (startup or lazy init)
3. Implement Foundry thread create/reuse semantics
4. Replace ephemeral request-thread behavior with durable thread flow

Deliverables:
- `src/agent/server.py` refactored to Foundry persistent flow
- New module for Foundry operations (e.g., `src/agent/foundry_runtime.py`)
- Explicit `thread_id` honor/reuse logic

## Phase 2 — Frontend integration update

1. Update frontend service contract to new endpoints/event schema
2. Ensure session-level thread continuity in chat state
3. Keep robust error handling and health checks

Deliverables:
- `src/web/src/services/agentService.ts` updated request/stream parsing
- `src/web/src/components/ChatWidget.tsx` updated thread lifecycle handling
- Vite proxy remains stable for agent route

## Phase 3 — Validation and hardening

1. Add regression tests for continuity and tool correctness
2. Validate transfer confirmation gate still enforced
3. Validate restart behavior and degraded-mode responses

Deliverables:
- Tests added/updated under `src/agent/tests/`
- Clear runbook in `src/agent/README.md`

## 7) API Contract (Target)

> Exact payload/event schema will be finalized in implementation PR #1.

### POST `/agent/threads`
- Purpose: create Foundry thread
- Response: `{ threadId: string }`

### POST `/agent/messages`
- Purpose: send message to a thread and stream response
- Request: `{ threadId: string, input: string }`
- Response: SSE stream events including text chunks and completion state

### GET `/agent/health`
- Purpose: service + Foundry dependency health summary

## 8) Security and Safety Requirements

- Keep transfer confirmation as mandatory before execution
- Never fabricate balances/transactions/transfers
- Sanitize operational errors returned to UI
- Prefer Entra identity for service authentication to Foundry in production
- Keep API-key fallback policy explicit and environment-scoped

## 9) Risks and Mitigations

### Risk: preview SDK churn
- Mitigation: strict version pinning, changelog review before upgrades, smoke tests

### Risk: endpoint breakage during contract switch
- Mitigation: implement server + frontend changes in same branch and validate E2E before merge

### Risk: thread continuity bugs
- Mitigation: dedicated tests for same-thread multi-turn and new-thread creation paths

### Risk: auth/environment misconfiguration
- Mitigation: startup validation and actionable diagnostics in health endpoint

## 10) Acceptance Criteria

- Agent runs as persistent Foundry-backed runtime (no per-request agent recreation)
- Conversation continues across turns using Foundry thread id for same browser session
- Frontend chat works end-to-end with updated endpoint contract
- Tool calls for accounts/transactions/transfers succeed against backend API
- Transfer still requires explicit confirmation before execution
- Health endpoints report meaningful ready/degraded states

## 11) Rollout Strategy

1. Merge Phase 0 + Phase 1 behind a feature branch
2. Add Phase 2 frontend updates and run local E2E validation
3. Merge after green regression checks
4. Plan follow-up for hosted-agent deployment track (phase 4)

## 12) Branch

- Active implementation branch:
  - `feature/agent-foundry-persistent-threads-migration`
