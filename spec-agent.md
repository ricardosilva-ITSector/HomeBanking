# Home Banking Agent - Technical Specification

**Version**: 1.0  
**Last Updated**: February 17, 2026  
**Status**: Draft (MVP)

---

## 1. Overview

This document defines the first agent capability for HomeBanking using **Microsoft Agent Framework** with **Azure AI Foundry Agent Service**.

The selected direction for MVP is:
- **Primary use case**: Transfer Copilot
- **Runtime topology**: Python sidecar service + existing .NET API
- **Authentication (MVP)**: API key / connection string approach
- **Delivery target**: 1-2 weeks

The agent helps users prepare and execute account-to-account transfers through natural language while enforcing explicit confirmation and existing business validation rules.

---

## 2. Product Goals and Scope

### 2.1 Goals

1. Provide a conversational assistant that can understand transfer intent.
2. Reuse existing backend transfer logic (`POST /api/transfers`) without bypassing validation.
3. Minimize risk in MVP by requiring explicit user confirmation before transfer execution.
4. Establish a production-ready architecture path (Managed Identity + RBAC) after MVP.

### 2.2 In Scope (MVP)

- Conversational transfer assistance (amount, source account, destination account, description).
- Read account balances and recent transactions to support user decisions.
- Transfer execution only after explicit confirmation in the same conversation.
- Basic traceability for agent requests, tool calls, and transfer outcomes.

### 2.3 Out of Scope (MVP)

- External bank transfers/wire/ACH.
- Autonomous transfers without explicit confirmation.
- Long-term memory and personalization across sessions.
- New financial analytics or budgeting features.

---

## 3. Functional Requirements

### FR-A001: Conversational Transfer Intent Detection
- Agent can parse user intent such as: “transfer $50 from checking to savings”.
- Agent asks follow-up questions when required fields are missing.

### FR-A002: Transfer Drafting
- Agent builds a transfer draft with:
  - `fromAccountId`
  - `toAccountId`
  - `amount`
  - `description` (optional)
- Agent displays a structured summary before execution.

### FR-A003: Explicit Confirmation Gate
- Agent must request explicit confirmation (`yes`, `confirm`, or equivalent).
- Without confirmation, no transfer API call is made.

### FR-A004: Transfer Execution
- On confirmation, sidecar calls existing API endpoint:
  - `POST /api/transfers`
- Existing backend validation remains source of truth (balance, amount, account constraints).
- Agent returns user-friendly success/failure response from API result.

### FR-A005: Account and Transaction Context
- Agent can read:
  - `GET /api/accounts`
  - `GET /api/transactions?accountId={optional}&limit={optional}&offset={optional}`
- Agent uses this data to disambiguate account names and explain available balance.

### FR-A006: Safe Error Handling
- Agent handles and surfaces:
  - Validation failures (400)
  - Unexpected server errors (500)
  - Timeout/connection failures from sidecar to API
- Agent never fabricates transfer completion.

---

## 4. Non-Functional Requirements

### NFR-A001: Security (MVP)
- Foundry and sidecar secrets stored in environment variables / secret store.
- No secrets in prompts, logs, code, or client payloads.
- Sidecar endpoint exposed only to trusted app/backend boundary.

### NFR-A002: Security (Post-MVP Target)
- Migrate from key-based auth to Managed Identity + RBAC.
- Use least-privilege role assignments for agent runtime and tool invocations.

### NFR-A003: Reliability
- If agent tool/function call fails, user gets actionable fallback guidance.
- Run orchestration handles multi-step calls and terminal statuses (`failed`, `cancelled`, `expired`).

### NFR-A004: Performance
- Target p95 end-to-end response for read operations: < 4s.
- Target p95 transfer confirmation flow (excluding user typing): < 6s.

### NFR-A005: Observability
- Correlate conversation, tool call, and transfer execution with request IDs.
- Log: intent, tool name, latency, status, transfer IDs (on success), error code (on failure).

---

## 5. Architecture

### 5.1 Logical Architecture

```text
React Web (existing)
   |
   | HTTP
   v
.NET API (existing, src/api)
   |\
   | \ existing controllers + transfer rules
   |  \
   |   v
   |  InMemory DB (existing)
   |
   | HTTP (internal trusted call)
   v
Agent Sidecar (new, Python, Microsoft Agent Framework)
   |
   | SDK calls
   v
Azure AI Foundry Agent Service (model + hosted agent runtime)
```

### 5.2 Integration Pattern

- **Primary orchestration location**: Python sidecar.
- **Business action source of truth**: existing .NET transfer endpoint.
- **Agent tools** wrap existing HomeBanking endpoints, not direct DB access.

### 5.3 Proposed Sidecar Tool Contracts

1. `list_accounts()`
   - Calls `GET /api/accounts`
2. `list_transactions(account_id?: Guid, limit?: int, offset?: int)`
   - Calls `GET /api/transactions`
3. `create_transfer(from_account_id: Guid, to_account_id: Guid, amount: decimal, description?: string)`
   - Calls `POST /api/transfers`
   - Invoked only after confirmation gate is satisfied

### 5.4 Conversation Safety State

For MVP, sidecar keeps a short-lived in-memory transfer draft per conversation:
- state: `drafted` -> `awaiting_confirmation` -> `submitted`/`cancelled`
- TTL: 10 minutes
- prevents accidental stale execution

---

## 6. API Surface Changes

### 6.1 Existing API Reuse
No mandatory changes to existing endpoints are required for MVP.

### 6.2 Optional API Additions (Post-MVP)
- `POST /api/transfers/preview` for explicit pre-checks before submission.
- Agent session endpoint(s) for first-party web chat orchestration.

---

## 7. Security and Compliance Considerations

1. Use environment-based configuration for:
   - Foundry endpoint / project connection
   - model deployment name
   - API key(s)
2. Restrict CORS and network paths so sidecar is not publicly callable by default.
3. Audit all transfer attempts initiated via agent channel.
4. Plan identity hardening milestone (Managed Identity + RBAC).

---

## 8. Testing Strategy

### 8.1 Unit Tests
- Sidecar tool adapters for accounts/transactions/transfers.
- Confirmation gate state transitions.
- Error mapping from API failures to user-safe messages.

### 8.2 Integration Tests
- Sidecar -> API endpoint interactions (happy + validation failures).
- Foundry run status handling (`requires_action`, `completed`, `failed`).

### 8.3 E2E Tests
- User asks for transfer, confirms, sees success message and updated balances.
- User cancels transfer, no mutation occurs.

---

## 9. Acceptance Criteria (MVP)

1. User can complete an internal transfer via conversation with explicit confirmation.
2. Agent uses existing backend transfer validations and surfaces backend error messages safely.
3. No transfer executes without confirmation.
4. Logs include enough metadata to trace each transfer request across web, sidecar, and API.
5. Basic regression tests pass for backend and agent integration paths.

---

## 10. Risks and Mitigations

1. **Model/tool misfire risk**
   - Mitigation: strict tool instructions + confirmation gate.
2. **Auth hardening deferred in MVP**
   - Mitigation: isolate secrets + timebox migration task in implementation plan.
3. **Latency variance from external agent runtime**
   - Mitigation: timeout + retry strategy + user-facing fallback messaging.

---

## 11. Open Decisions for Next Iteration

1. Move to Managed Identity + RBAC timeline and prerequisite infra.
2. Durable conversation state (Redis/Cosmos DB) if multi-session memory is required.
3. Expand scope from transfer copilot to read-only financial guidance features.
