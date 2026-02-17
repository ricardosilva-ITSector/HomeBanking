# Home Banking Agent - Implementation Plan

**Version**: 1.0  
**Last Updated**: February 17, 2026  
**Total Tasks**: 12 (A000-A011)  
**Estimated Duration**: 1-2 weeks (MVP)

---

## 1. Delivery Objective

Deliver an MVP transfer copilot using Microsoft Agent Framework + Azure AI Foundry Agent Service, integrated with existing HomeBanking API through a Python sidecar.

---

## 2. Milestones

- **M1**: Foundation and architecture setup (A000-A003)
- **M2**: Transfer copilot capabilities (A004-A007)
- **M3**: Quality, observability, and release readiness (A008-A011)

---

## 3. Task Breakdown

### A000 - Finalize agent scope and contracts
- **Status**: pending
- **Estimate**: 0.5 day
- **Deliverables**:
  - Confirm transfer-only MVP scope
  - Confirm sidecar tool contracts and confirmation flow
- **Dependencies**: None
- **Exit Criteria**:
  - Scope baselined in docs
  - Team alignment on UX and guardrails

### A001 - Provision Foundry project prerequisites
- **Status**: pending
- **Estimate**: 0.5-1 day
- **Deliverables**:
  - Foundry project and model deployment ready
  - Local/dev environment secrets configured
- **Dependencies**: A000
- **Exit Criteria**:
  - Sidecar can authenticate and connect to Foundry

### A002 - Scaffold Python sidecar service
- **Status**: pending
- **Estimate**: 1 day
- **Deliverables**:
  - `src/agent/` project structure
  - Base config, env loading, health endpoint
  - Microsoft Agent Framework dependencies pinned
- **Dependencies**: A001
- **Exit Criteria**:
  - Sidecar starts locally without runtime errors

### A003 - Define Foundry agent and instruction policy
- **Status**: pending
- **Estimate**: 0.5 day
- **Deliverables**:
  - Agent system instructions for safe transfer behavior
  - Tool usage policy (`tool_choice`, fallback wording, no fabricated success)
- **Dependencies**: A002
- **Exit Criteria**:
  - Agent created and callable in dev

### A004 - Implement read tools (accounts/transactions)
- **Status**: pending
- **Estimate**: 1 day
- **Deliverables**:
  - Tool adapters for `GET /api/accounts` and `GET /api/transactions`
  - Response normalization and error mapping
- **Dependencies**: A003
- **Exit Criteria**:
  - Agent can answer account/transaction context questions reliably

### A005 - Implement transfer tool and confirmation gate
- **Status**: pending
- **Estimate**: 1.5 days
- **Deliverables**:
  - Draft transfer state machine in sidecar
  - Explicit confirmation handling
  - `POST /api/transfers` integration
- **Dependencies**: A004
- **Exit Criteria**:
  - No transfer without confirmation
  - Successful transfer returns transaction IDs to user

### A006 - Integrate .NET API with sidecar invocation path
- **Status**: pending
- **Estimate**: 1 day
- **Deliverables**:
  - Internal API route or service call path to sidecar
  - Request correlation IDs propagated
- **Dependencies**: A005
- **Exit Criteria**:
  - Web -> API -> sidecar -> Foundry flow operational end to end

### A007 - Add web chat UX for transfer copilot
- **Status**: pending
- **Estimate**: 1-1.5 days
- **Deliverables**:
  - Minimal chat interface in existing web app
  - Transfer confirmation UI state (confirm/cancel)
- **Dependencies**: A006
- **Exit Criteria**:
  - User can complete full transfer conversation from browser

### A008 - Add automated tests
- **Status**: pending
- **Estimate**: 1 day
- **Deliverables**:
  - Sidecar unit tests (state transitions, tool wrappers)
  - Integration tests for transfer success/failure paths
- **Dependencies**: A005, A006
- **Exit Criteria**:
  - Deterministic tests for critical agent paths

### A009 - Add observability and diagnostics
- **Status**: pending
- **Estimate**: 0.5 day
- **Deliverables**:
  - Structured logs for conversation + tool execution
  - Correlation IDs across tiers
- **Dependencies**: A006
- **Exit Criteria**:
  - Single transfer request traceable across systems

### A010 - Security hardening for MVP release
- **Status**: pending
- **Estimate**: 0.5 day
- **Deliverables**:
  - Secret handling review
  - Endpoint exposure and CORS/network checks
- **Dependencies**: A006, A009
- **Exit Criteria**:
  - No plaintext secrets in codebase
  - Sidecar boundary documented and restricted

### A011 - Release readiness and handoff
- **Status**: pending
- **Estimate**: 0.5 day
- **Deliverables**:
  - README updates (setup/run/troubleshoot)
  - Decision log for post-MVP identity migration
- **Dependencies**: A007, A008, A010
- **Exit Criteria**:
  - Team can run and demo the full flow from clean environment

---

## 4. Critical Path

A000 -> A001 -> A002 -> A003 -> A004 -> A005 -> A006 -> A007 -> A011

---

## 5. Validation Checklist (MVP)

A task is complete only if all applicable checks pass:

1. Build/lint for changed projects pass.
2. New tests for new behavior pass.
3. Existing tests remain green (no regressions).
4. Logs/traceability are verified for transfer path.
5. Documentation updated for changed setup/runtime.

---

## 6. Suggested Validation Commands

### Backend (.NET)
```powershell
cd src/api
dotnet restore
dotnet build --configuration Release /p:TreatWarningsAsErrors=true
dotnet test --configuration Release
```

### Frontend (React)
```powershell
cd src/web
npm ci
npm run lint
npm run build
npm run test:unit
```

### Sidecar (Python)
```powershell
cd src/agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
```

---

## 7. Post-MVP Backlog (Already Identified)

1. Migrate auth from key-based to Managed Identity + RBAC.
2. Add durable conversation state store.
3. Introduce policy guardrails for high-risk operations.
4. Expand capability beyond transfers (spending insights, proactive alerts).

---

## 8. Risks to Schedule

1. Foundry/project setup delays or model availability by region.
2. Tool-call reliability tuning requiring prompt/instruction iteration.
3. Integration complexity between .NET API and Python sidecar under local dev.

Mitigation: finish A001-A003 early and run end-to-end smoke checks before UI work.