# Home Banking Application - Implementation Plan

**Version**: 1.0  
**Last Updated**: February 17, 2026  
**Total Tasks**: 23 (T000-T022)  
**Estimated Duration**: 8-10 days (single developer)

---

## Definition of Done (DoD) - MANDATORY GATE

**Purpose**: Every task must pass this gate before being marked complete. These criteria ensure quality, maintainability, and CI/CD reliability. **A task is NOT complete until the commit passes ALL GitHub Actions CI checks.**

### Core Principles

1. **Local/CI Parity**: If it passes locally, it MUST pass in CI. No surprises on PR.
2. **Known Good State**: Never leave the codebase in a broken state between tasks.
3. **Incremental Progress**: Each task is independently deployable and testable.
4. **Self-Documenting**: Code, commits, and plan updates tell the story.

---

### MANDATORY CHECKLIST (All items required)

Every task MUST satisfy ALL of the following before marking as `completed`:

#### ✅ Build & Compilation
- [ ] **Backend builds successfully** (if applicable)
  - No compilation errors
  - No build warnings (`TreatWarningsAsErrors=true`)
  - All NuGet packages restore correctly
- [ ] **Frontend builds successfully** (if applicable)
  - TypeScript compilation passes (strict mode)
  - Vite build completes without errors
  - No missing dependencies

#### ✅ Code Quality & Linting
- [ ] **Zero lint errors** across entire codebase
  - Backend: Roslyn analyzers, StyleCop (if configured)
  - Frontend: ESLint with TypeScript rules
  - No warnings suppressed without justification
- [ ] **Code formatting** consistent
  - Backend: .editorconfig rules followed
  - Frontend: Prettier configured and applied

#### ✅ Testing
- [ ] **New tests created** for all new functionality
  - Unit tests for business logic (services, utilities)
  - Component tests for UI components (if applicable)
  - Integration tests for API endpoints (if applicable)
  - E2E tests for critical user flows (if applicable)
- [ ] **ALL tests pass** (100% pass rate)
  - Existing tests still passing (no regressions)
  - New tests passing
  - Test coverage maintained or improved
  - No flaky tests introduced
- [ ] **Test quality standards met**
  - Tests are deterministic and reliable
  - Tests follow AAA pattern (Arrange/Act/Assert)
  - Tests have clear, descriptive names
  - No `skip` or `only` left in test files

#### ✅ Documentation
- [ ] **Code comments updated** where relevant
  - XML documentation for public APIs (C#)
  - JSDoc for exported functions (TypeScript)
  - Complex logic explained inline
- [ ] **README updates** (if applicable)
  - New setup steps documented
  - New scripts/commands explained
  - Prerequisites updated
- [ ] **API documentation current** (if applicable)
  - Scalar/OpenAPI specs reflect changes
  - Request/response examples accurate

#### ✅ Version Control
- [ ] **Changes committed** with conventional commit message
  - Format: `type(scope): description`
  - Types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `ci`
  - Example: `feat(api): add account balance endpoint`
- [ ] **Commit is atomic** (single logical change)
- [ ] **No unrelated changes** included
- [ ] **Sensitive data excluded** (no secrets, API keys, local paths)

#### ✅ Plan Maintenance
- [ ] **Task status updated** in plan.md
  - Status changed to `completed`
  - "Plan Changes" section filled out (see below)
- [ ] **Downstream impacts assessed**
  - Review all remaining tasks
  - Identify dependencies affected by this task
  - Update task estimates, DoD, or descriptions if needed
  - Document changes in "Plan Changes" section
- [ ] **plan.md committed** with task updates

#### ✅ CI/CD Gate (CRITICAL)
- [ ] **All GitHub Actions workflows pass** ✅ GREEN
  - Commit pushed to branch
  - CI build completes successfully
  - All CI tests pass (same commands as local validation)
  - No CI-only failures ("works on my machine" prohibited)
  - Screenshots/artifacts reviewed if applicable

---

### VALIDATION COMMANDS (Local & CI Must Match)

**These exact commands MUST pass locally before pushing, and CI MUST run the same commands:**

#### Backend Validation
```powershell
# Navigate to API project
cd src/api

# Restore dependencies
dotnet restore

# Build (with warnings as errors)
dotnet build --no-restore --configuration Release /p:TreatWarningsAsErrors=true

# Run all tests
dotnet test --no-build --configuration Release --verbosity normal

# Verify no lint warnings (if using analyzers)
dotnet build --no-restore /p:EnforceCodeStyleInBuild=true
```

#### Frontend Validation
```powershell
# Navigate to web project
cd src/web

# Clean install dependencies
npm ci

# Lint
npm run lint

# Type check
npm run type-check  # or: npx tsc --noEmit

# Build
npm run build

# Unit tests
npm run test:unit

# E2E tests (requires API running)
npm run test:e2e
```

#### Full Stack Validation (Pre-Push)
```powershell
# From repository root
# Run backend validation
cd src/api
dotnet build --configuration Release /p:TreatWarningsAsErrors=true
dotnet test --configuration Release

# Run frontend validation
cd ../web
npm ci
npm run lint
npm run build
npm run test:unit

# Start servers and run E2E (in separate terminal)
# Terminal 1: cd src/api && dotnet run
# Terminal 2: cd src/web && npm run dev
# Terminal 3: cd src/web && npm run test:e2e
```

**CRITICAL**: CI workflow MUST execute these exact commands in the same order.

---

### TASK COMPLETION WORKFLOW

Follow this workflow when completing each task:

1. **Implement** the task requirements
2. **Self-review** code for quality and completeness
3. **Run validation commands** locally (see above)
4. **Fix any issues** until all validations pass
5. **Write/update tests** for new functionality
6. **Run ALL tests** again to ensure 100% pass rate
7. **Update documentation** (code comments, README, etc.)
8. **Review downstream tasks** in plan.md
   - Identify tasks affected by this work
   - Update task descriptions, estimates, DoD items
   - Document why changes were needed
9. **Update plan.md** for this task:
   - Change status to `completed`
   - Fill in "Plan Changes" section (see template below)
10. **Commit changes** with conventional commit message
11. **Push to branch** and verify CI is green
12. **Only after CI passes**: Task is DONE ✅

---

### "PLAN CHANGES" SECTION TEMPLATE

When completing a task, fill in the "Plan Changes" section with:

```markdown
- **Plan Changes**: 
  - Completed: [Date], [Time spent vs. estimate]
  - Downstream impacts: 
    - T00X: [Briefly describe change and reason]
    - T00Y: [Briefly describe change and reason]
  - Learnings: [Any discoveries, gotchas, or decisions made]
  - Commit: [Commit SHA]
  - CI Status: ✅ GREEN [link to workflow run]
```

**Example**:
```markdown
- **Plan Changes**: 
  - Completed: Feb 17 2026, 2h (estimated 1.5h)
  - Downstream impacts:
    - T015: Added authentication headers to API client requirements
    - T019: Transfer form now needs token management
  - Learnings: CORS required credentials:true for cookies
  - Commit: abc123f
  - CI Status: ✅ GREEN https://github.com/.../actions/runs/123
```

If NO changes to downstream tasks: 
```markdown
- **Plan Changes**: 
  - Completed: Feb 17 2026, 1.5h (as estimated)
  - Downstream impacts: None
  - Learnings: None
  - Commit: abc123f
  - CI Status: ✅ GREEN https://github.com/.../actions/runs/123
```

---

### AI-ASSISTED DEVELOPMENT BEST PRACTICES

Additional guidelines for working with AI coding assistants:

1. **Explicit Validation**: Always run exact commands, never assume AI output is correct
2. **Incremental Verification**: Test after each logical change, not just at task end
3. **Plan Synchronization**: Update plan.md immediately when tasks evolve
4. **Context Preservation**: Commit frequently to preserve working states
5. **Reproducibility**: Document environment setup, versions, non-obvious steps
6. **Error Transparency**: When validation fails, include full error output in context
7. **Human Review Gates**: Final code review before marking task complete
8. **Regression Prevention**: Always run full test suite, not just new tests

---

### FAILURE STATES & RECOVERY

If a validation gate FAILS:

1. **DO NOT mark task as complete**
2. **DO NOT move to next task**
3. **Fix the failure** immediately
4. **Re-run full validation** from scratch
5. **Document** what went wrong and how it was fixed
6. **Update plan.md** if failure revealed wrong estimates/approach

If **CI fails** but local passes:

1. **Investigate differences** (environment, dependencies, timing)
2. **Reproduce failure locally** (use same Node/dotnet versions)
3. **Fix root cause** (usually missing dependency, env var, or race condition)
4. **Update validation commands** if gap found
5. **Document** in "Learnings" section

---

### SUCCESS CRITERIA

A task achieves "DONE" status when:

- ✅ All mandatory checklist items satisfied
- ✅ All validation commands pass locally
- ✅ Changes committed with good message
- ✅ Pushed to branch
- ✅ **GitHub Actions CI is GREEN** 🟢
- ✅ plan.md updated with completion details
- ✅ No known issues or technical debt introduced

**Remember**: GREEN CI is the ultimate gate. If CI is red, the task is NOT done.

---

## Table of Contents
0. [Environment Bootstrap](#phase-0-environment-bootstrap)
1. [Project Setup](#phase-1-project-setup)
2. [Backend API](#phase-2-backend-api)
3. [Frontend Foundation](#phase-3-frontend-foundation)
4. [Frontend Features](#phase-4-frontend-features)
5. [Testing](#phase-5-testing)
6. [CI/CD & Documentation](#phase-6-cicd--documentation)

---

## Phase 0: Environment Bootstrap

### Task T000: Project Scaffold and Build Verification
- **Status**: completed
- **Dependencies**: none
- **Estimate**: S
- **Description**: Scaffold both projects and verify clean builds before implementation begins
- **DoD**: 
  - [x] Folder structure created (src/api, src/web, docs, .github/workflows)
  - [x] .NET Core 9 Web API project scaffolded in src/api
  - [x] TreatWarningsAsErrors enabled in .csproj
  - [x] React+Vite+TypeScript project scaffolded in src/web
  - [x] Both projects build successfully (dotnet build, npm run build)
  - [x] No application code written (template code only)
  - [x] Dependencies installed and verified
  - [x] Committed with message: "T000: project scaffold and build verification"
  - [x] plan.md updated with T000 task
- **Plan Changes**: 
  - Completed: Feb 17 2026, ~30min
  - Downstream impacts:
    - T001: Now focuses only on .gitignore and README (folder structure already done)
    - T002: .NET project already exists, task will focus on configuration only
    - T013: React+Vite project already exists, task will focus on configuration only
  - Learnings: 
    - React 19.2.0 scaffolded (newer than spec's 18.3, compatible)
    - TypeScript 5.9.3 scaffolded (close to spec's 5.7+)
    - Vite 7.3.1 scaffolded (newer than spec's 6.0+, compatible)
    - npm install required after Vite create (dependencies partially installed)
    - .gitignore created at root level for monorepo
  - Commit: 7737c0c
  - CI Status: (not yet pushed to remote)

---

## Phase 1: Project Setup

### Task T001: Initialize Monorepo Structure
- **Status**: completed
- **Dependencies**: none
- **Estimate**: S
- **Description**: Create root folder structure, .gitignore, and README
- **DoD**: 
  - [x] Root folder structure created (src/api, src/web, docs, .github/workflows)
  - [x] .gitignore configured for .NET and Node.js
  - [x] README.md with project overview and setup instructions
  - [x] Git repository initialized
  - [x] Builds successfully (no projects yet)
  - [x] No lint errors
  - [x] New tests: N/A
  - [x] All tests pass: N/A
  - [x] Docs updated: README.md created
  - [x] Committed with message: "chore: initialize monorepo structure"
- **Plan Changes**: 
  - Completed: Feb 17 2026, ~30min (as estimated)
  - Downstream impacts:
    - None (T000 already created folder structure, T001 focused on documentation)
  - Learnings:
    - README.md updated with comprehensive setup instructions, tech stack, and project structure
    - .gitignore already comprehensive (no changes needed)
  - Commit: a7b133b
  - CI Status: N/A (CI workflow not yet configured - will be added in T022)

---

## Phase 2: Backend API

### Task T002: Create .NET Core 9 API Project
- **Status**: completed
- **Dependencies**: T001
- **Estimate**: S
- **Description**: Initialize ASP.NET Core 9 Web API project with essential configuration
- **DoD**:
  - [x] `dotnet new webapi` in src/api/HomeBanking.Api
  - [x] Project references .NET 9.0 SDK
  - [x] Nullable reference types enabled
  - [x] CORS configured for localhost:5173 (Vite default)
  - [x] appsettings.json and appsettings.Development.json configured
  - [x] Builds without warnings
  - [x] No lint errors (Roslyn analyzers)
  - [x] New tests: N/A
  - [x] All tests pass: N/A
  - [x] Docs updated: N/A
  - [x] Committed with message: "feat(api): initialize .NET Core 9 Web API project"
- **Plan Changes**: 
  - Completed: Feb 17 2026, ~45min (estimated 1-2h)
  - Downstream impacts:
    - None (configuration baseline established for subsequent API tasks)
  - Learnings:
    - Configured CORS for localhost:5173 (Vite) with credentials support
    - Added comprehensive .editorconfig with .NET best practices
    - Enabled Roslyn analyzers (EnforceCodeStyleInBuild, AnalysisLevel=latest)
    - Created folder structure (Controllers/, Models/, Data/, Services/, Validators/)
    - Added health check endpoint at /health
    - Removed WeatherForecast template code
  - Commit: 5ada63f
  - CI Status: N/A (CI workflow not yet configured - will be added in T022)

---

### Task T003: Implement Domain Models
- **Status**: completed
- **Dependencies**: T002
- **Estimate**: S
- **Description**: Create Account and Transaction entities with enums
- **DoD**:
  - [x] Account.cs model created (Id, AccountNumber, AccountName, Type, Balance, Currency, CreatedAt)
  - [x] Transaction.cs model created (Id, AccountId, Date, Description, Amount, Type, Category, BalanceAfter)
  - [x] AccountType enum (Checking, Savings)
  - [x] TransactionType enum (Debit, Credit)
  - [x] Navigation properties configured
  - [x] Builds without warnings
  - [x] No lint errors
  - [x] New tests: N/A (DTOs, no business logic yet)
  - [x] All tests pass: N/A
  - [x] Docs updated: N/A
  - [x] Committed with message: "feat(api): add Account and Transaction domain models"
- **Plan Changes**: 
  - Completed: Feb 17 2026, ~20min (estimated 1-2h)
  - Downstream impacts:
    - None (models ready for EF Core configuration in T004)
  - Learnings:
    - Used .NET 9 `required` keyword for non-nullable reference types
    - Added XML documentation comments on all public members
    - Configured bidirectional navigation properties (Account.Transactions, Transaction.Account)
    - All models follow C# conventions and nullable reference type best practices
  - Commit: 9332336
  - CI Status: N/A (CI workflow not yet configured - will be added in T022)

---

### Task T004: Configure EF Core InMemory DbContext
- **Status**: completed
- **Dependencies**: T003
- **Estimate**: M
- **Description**: Setup EF Core InMemory database with DbContext and demo data seeding
- **DoD**:
  - [x] Install Microsoft.EntityFrameworkCore.InMemory (version 9.0+)
  - [x] HomeBankingDbContext.cs created with DbSet<Account> and DbSet<Transaction>
  - [x] OnModelCreating configured with entity relationships
  - [x] SeedData.cs utility class created
  - [x] Demo data: 2 accounts (Checking $5000, Savings $15000)
  - [x] Demo data: 50+ realistic transactions (last 90 days, varied categories)
  - [x] DbContext registered in Program.cs with InMemory provider
  - [x] Database seeded on application start
  - [x] Builds without warnings
  - [x] No lint errors
  - [x] New tests: N/A (integration with API in later tasks)
  - [x] All tests pass: N/A
  - [x] Docs updated: N/A
  - [x] Committed with message: "feat(api): configure EF Core InMemory with demo data seeding"
- **Plan Changes**: 
  - Completed: Feb 17 2026, ~35min (estimated 3-4h)
  - Downstream impacts:
    - None (DbContext ready for controller implementation in T005+)
  - Learnings:
    - Installed Microsoft.EntityFrameworkCore.InMemory 9.0.0
    - Configured entity relationships with cascade delete
    - Created 60+ realistic transactions spanning 90 days
    - All categories from spec implemented: Salary, Refund, Groceries, Utilities, Entertainment, Transport, Shopping, Healthcare, Internal Transfer
    - Decimal precision set to (18,2) for all monetary values
    - Database seeded on application startup with SeedData.Initialize()
  - Commit: 727cdca
  - CI Status: N/A (CI workflow not yet configured - will be added in T022)

---

### Task T005: Implement AccountsController (GET /api/accounts)
- **Status**: pending
- **Dependencies**: T004
- **Estimate**: S
- **Description**: Create API endpoint to retrieve all accounts
- **DoD**:
  - [ ] AccountsController.cs created
  - [ ] GET /api/accounts endpoint implemented
  - [ ] Returns List<Account> with 200 OK
  - [ ] Proper async/await pattern
  - [ ] XML documentation comments
  - [ ] Manually tested via Swagger/browser
  - [ ] Builds without warnings
  - [ ] No lint errors
  - [ ] New tests: Unit test for controller action
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(api): add GET /api/accounts endpoint"
- **Plan Changes**: _(filled post-completion)_

---

### Task T006: Implement TransactionsController (GET /api/transactions)
- **Status**: pending
- **Dependencies**: T004
- **Estimate**: M
- **Description**: Create API endpoint to retrieve transactions with optional filtering
- **DoD**:
  - [ ] TransactionsController.cs created
  - [ ] GET /api/transactions endpoint with query params (accountId, limit, offset)
  - [ ] Returns paginated transaction list with total count
  - [ ] Transactions ordered by date descending
  - [ ] Filter by accountId if provided
  - [ ] Default limit: 100, max limit: 500
  - [ ] Manually tested with various query params
  - [ ] Builds without warnings
  - [ ] No lint errors
  - [ ] New tests: Unit tests for filtering and pagination logic
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(api): add GET /api/transactions with filtering"
- **Plan Changes**: _(filled post-completion)_

---

### Task T007: Implement Transfer Service (Business Logic)
- **Status**: pending
- **Dependencies**: T004
- **Estimate**: M
- **Description**: Create service layer for transfer logic with validation
- **DoD**:
  - [ ] ITransferService interface created
  - [ ] TransferService.cs implementation
  - [ ] ExecuteTransferAsync method with validation:
    - [ ] Sufficient balance check
    - [ ] Valid account IDs (both exist)
    - [ ] Prevent self-transfer
    - [ ] Amount within limits ($0.01 - $10,000)
  - [ ] Creates two transactions (debit from source, credit to destination)
  - [ ] Updates account balances atomically
  - [ ] Service registered in Program.cs DI container
  - [ ] Builds without warnings
  - [ ] No lint errors
  - [ ] New tests: Unit tests for all validation rules and success case
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(api): implement transfer service with validation"
- **Plan Changes**: _(filled post-completion)_

---

### Task T008: Implement TransfersController (POST /api/transfers)
- **Status**: pending
- **Dependencies**: T007
- **Estimate**: S
- **Description**: Create API endpoint for money transfers
- **DoD**:
  - [ ] TransfersController.cs created
  - [ ] TransferRequest DTO (FromAccountId, ToAccountId, Amount, Description)
  - [ ] TransferResponse DTO (TransferId, FromTransaction, ToTransaction, Timestamp)
  - [ ] POST /api/transfers endpoint using TransferService
  - [ ] Returns 201 Created on success
  - [ ] Returns 400 Bad Request with validation errors
  - [ ] Proper exception handling and logging
  - [ ] Manually tested (success + failure scenarios)
  - [ ] Builds without warnings
  - [ ] No lint errors
  - [ ] New tests: Controller unit tests for success and validation errors
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(api): add POST /api/transfers endpoint"
- **Plan Changes**: _(filled post-completion)_

---

### Task T009: Add Scalar OpenAPI Documentation
- **Status**: pending
- **Dependencies**: T008
- **Estimate**: S
- **Description**: Configure Scalar for interactive API documentation
- **DoD**:
  - [ ] Install Scalar.AspNetCore NuGet package (1.2+)
  - [ ] Configure Swagger/OpenAPI generation in Program.cs
  - [ ] Add Scalar middleware (MapScalarApiReference)
  - [ ] Configure API metadata (title, version, description)
  - [ ] Endpoint accessible at /scalar/v1
  - [ ] All endpoints documented with XML comments
  - [ ] Request/response examples included
  - [ ] Manually tested in browser
  - [ ] Builds without warnings
  - [ ] No lint errors
  - [ ] New tests: N/A (UI validation)
  - [ ] All tests pass
  - [ ] Docs updated: README with Scalar URL
  - [ ] Committed with message: "feat(api): add Scalar OpenAPI documentation"
- **Plan Changes**: _(filled post-completion)_

---

### Task T010: Add Health Check Endpoint
- **Status**: pending
- **Dependencies**: T004
- **Estimate**: S
- **Description**: Implement health check endpoint for monitoring
- **DoD**:
  - [ ] Health checks configured in Program.cs
  - [ ] Database health check added (EF Core InMemory)
  - [ ] GET /health endpoint returns JSON with status
  - [ ] Returns 200 (Healthy) or 503 (Unhealthy)
  - [ ] Includes individual check results
  - [ ] Manually tested
  - [ ] Builds without warnings
  - [ ] No lint errors
  - [ ] New tests: Integration test for health endpoint
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(api): add health check endpoint"
- **Plan Changes**: _(filled post-completion)_

---

### Task T011: API Unit Tests Setup
- **Status**: pending
- **Dependencies**: T002
- **Estimate**: S
- **Description**: Create test project and configure testing infrastructure
- **DoD**:
  - [ ] Create HomeBanking.Api.Tests project (xUnit)
  - [ ] Install xUnit, FluentAssertions, Moq, Microsoft.AspNetCore.Mvc.Testing
  - [ ] Setup test utilities (InMemory DbContext factory, test data builders)
  - [ ] Example test for TransferService validates setup
  - [ ] Tests run via `dotnet test`
  - [ ] Builds without warnings
  - [ ] No lint errors
  - [ ] New tests: 1 example test
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "test(api): setup unit test project infrastructure"
- **Plan Changes**: _(filled post-completion)_

---

### Task T012: Complete API Unit Test Coverage
- **Status**: pending
- **Dependencies**: T011, T008
- **Estimate**: M
- **Description**: Write comprehensive unit tests for services and controllers
- **DoD**:
  - [ ] TransferService tests (all validation rules, success case, edge cases)
  - [ ] AccountsController tests (GET all accounts)
  - [ ] TransactionsController tests (filtering, pagination)
  - [ ] TransfersController tests (success, validation failures)
  - [ ] Test coverage: 80%+ for business logic
  - [ ] All tests use proper mocking (Moq for dependencies)
  - [ ] Builds without warnings
  - [ ] No lint errors
  - [ ] New tests: 20+ unit tests
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "test(api): add comprehensive unit test coverage"
- **Plan Changes**: _(filled post-completion)_

---

## Phase 3: Frontend Foundation

### Task T013: Create React+Vite+TypeScript Project
- **Status**: pending
- **Dependencies**: T001
- **Estimate**: S
- **Description**: Initialize frontend project with Vite and TypeScript
- **DoD**:
  - [ ] `npm create vite@latest` in src/web (react-swc-ts template)
  - [ ] TypeScript configured (strict mode enabled)
  - [ ] Vite config updated (proxy to API at localhost:5000)
  - [ ] ESLint configured (@typescript-eslint, react-hooks rules)
  - [ ] Prettier configured
  - [ ] package.json scripts (dev, build, lint, preview)
  - [ ] npm install completes successfully
  - [ ] npm run dev starts dev server
  - [ ] Builds without errors
  - [ ] No lint errors
  - [ ] New tests: N/A
  - [ ] All tests pass: N/A
  - [ ] Docs updated: README with frontend setup instructions
  - [ ] Committed with message: "feat(web): initialize React+Vite+TypeScript project"
- **Plan Changes**: _(filled post-completion)_

---

### Task T014: Configure Tailwind CSS + shadcn/ui
- **Status**: pending
- **Dependencies**: T013
- **Estimate**: M
- **Description**: Setup Tailwind CSS and install shadcn/ui components
- **DoD**:
  - [ ] Install Tailwind CSS (4.0+) and dependencies
  - [ ] Configure tailwind.config.js (dark theme, content paths)
  - [ ] Update index.css with Tailwind directives
  - [ ] Initialize shadcn/ui (`npx shadcn@latest init`)
  - [ ] Configure dark theme in components.json
  - [ ] Install initial components: Button, Card, Input, Label, Select
  - [ ] Create ui/ folder with components
  - [ ] Verify Tailwind classes work in App.tsx
  - [ ] Builds without errors
  - [ ] No lint errors
  - [ ] New tests: N/A (UI validation)
  - [ ] All tests pass: N/A
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(web): configure Tailwind CSS and shadcn/ui"
- **Plan Changes**: _(filled post-completion)_

---

### Task T015: Create API Client Service
- **Status**: pending
- **Dependencies**: T013, T008
- **Estimate**: S
- **Description**: Implement typed API client for backend communication
- **DoD**:
  - [ ] TypeScript interfaces (Account, Transaction, TransferRequest, TransferResponse)
  - [ ] api.ts service with functions: getAccounts(), getTransactions(), createTransfer()
  - [ ] Proper error handling and typing
  - [ ] Base URL from environment variable
  - [ ] Fetch API with JSON headers
  - [ ] Builds without errors
  - [ ] No lint errors
  - [ ] New tests: N/A (integration tested with components)
  - [ ] All tests pass: N/A
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(web): implement typed API client service"
- **Plan Changes**: _(filled post-completion)_

---

### Task T016: Create App Layout and Theme
- **Status**: pending
- **Dependencies**: T014
- **Estimate**: S
- **Description**: Build main app layout with header and dark theme styling
- **DoD**:
  - [ ] App.tsx with main layout container
  - [ ] Header component (app title, logo placeholder)
  - [ ] Dark theme background (bg-slate-950, text-slate-50)
  - [ ] Responsive container (max-width, padding)
  - [ ] Global font (system font stack or Inter)
  - [ ] Visually verified in browser
  - [ ] Builds without errors
  - [ ] No lint errors
  - [ ] New tests: N/A
  - [ ] All tests pass: N/A
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(web): create app layout with dark theme"
- **Plan Changes**: _(filled post-completion)_

---

## Phase 4: Frontend Features

### Task T017: Implement Account Balance Cards
- **Status**: pending
- **Dependencies**: T015, T016
- **Estimate**: M
- **Description**: Create AccountCard component to display account balances
- **DoD**:
  - [ ] AccountCard.tsx component (props: account)
  - [ ] Display account name, account number (masked), balance, currency
  - [ ] Styled with shadcn Card component
  - [ ] Currency formatting (Intl.NumberFormat)
  - [ ] Account type badge (Checking/Savings)
  - [ ] Responsive grid layout (1 col mobile, 2 col desktop)
  - [ ] useEffect to fetch accounts on mount
  - [ ] Loading state (skeleton or spinner)
  - [ ] Error handling UI
  - [ ] Visually verified with API running
  - [ ] Builds without errors
  - [ ] No lint errors
  - [ ] New tests: Vitest unit test for AccountCard component
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(web): implement account balance cards"
- **Plan Changes**: _(filled post-completion)_

---

### Task T018: Implement Transactions Table
- **Status**: pending
- **Dependencies**: T015, T016
- **Estimate**: M
- **Description**: Create TransactionList component with category badges
- **DoD**:
  - [ ] TransactionList.tsx component
  - [ ] Table layout (Date, Description, Category, Amount, Balance)
  - [ ] Category badges with color coding:
    - [ ] Income (green): Salary, Refund
    - [ ] Expense (red): Groceries, Utilities, Entertainment, etc.
    - [ ] Transfer (blue): Internal Transfer
  - [ ] Amount formatting (+ for credit, - for debit)
  - [ ] Date formatting (relative or short date)
  - [ ] Responsive table (horizontal scroll on mobile)
  - [ ] Loading and error states
  - [ ] Fetch transactions on mount
  - [ ] Visually verified with API
  - [ ] Builds without errors
  - [ ] No lint errors
  - [ ] New tests: Unit test for TransactionList component
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(web): implement transactions table with category badges"
- **Plan Changes**: _(filled post-completion)_

---

### Task T019: Implement Transfer Form
- **Status**: pending
- **Dependencies**: T015, T016, T017
- **Estimate**: L
- **Description**: Create TransferForm component with validation
- **DoD**:
  - [ ] TransferForm.tsx component
  - [ ] Form fields: From Account (select), To Account (select), Amount (input), Description (textarea)
  - [ ] shadcn/ui form components (Select, Input, Label, Button)
  - [ ] Client-side validation:
    - [ ] Required fields
    - [ ] Amount between $0.01 and $10,000
    - [ ] Prevent self-transfer (disable same account in To dropdown)
    - [ ] Amount has max 2 decimals
  - [ ] Form submission with loading state
  - [ ] Success feedback (toast or message)
  - [ ] Error handling (display API validation errors)
  - [ ] Form reset after success
  - [ ] Refresh account balances after transfer
  - [ ] Accessible form (labels, ARIA, keyboard nav)
  - [ ] Visually verified with API
  - [ ] Builds without errors
  - [ ] No lint errors
  - [ ] New tests: Unit tests for validation logic
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "feat(web): implement transfer form with validation"
- **Plan Changes**: _(filled post-completion)_

---

## Phase 5: Testing

### Task T020: Setup Vitest for Component Testing
- **Status**: pending
- **Dependencies**: T013
- **Estimate**: S
- **Description**: Configure Vitest and React Testing Library
- **DoD**:
  - [ ] Install Vitest, @testing-library/react, @testing-library/jest-dom, jsdom
  - [ ] vitest.config.ts configured (jsdom environment)
  - [ ] Test setup file (test-setup.ts with global imports)
  - [ ] Example component test runs successfully
  - [ ] npm run test:unit script in package.json
  - [ ] Builds without errors
  - [ ] No lint errors
  - [ ] New tests: 1 example test
  - [ ] All tests pass
  - [ ] Docs updated: N/A
  - [ ] Committed with message: "test(web): setup Vitest for component testing"
- **Plan Changes**: _(filled post-completion)_

---

### Task T021: Setup Playwright for E2E Testing
- **Status**: pending
- **Dependencies**: T019
- **Estimate**: M
- **Description**: Configure Playwright and write critical E2E tests
- **DoD**:
  - [ ] Install @playwright/test
  - [ ] playwright.config.ts configured (baseURL, browsers, screenshots)
  - [ ] Install browsers via `npx playwright install`
  - [ ] E2E test: Dashboard load (accounts and transactions visible)
  - [ ] E2E test: Transaction list displays correctly
  - [ ] E2E test: Transfer flow (fill form, submit, verify success)
  - [ ] Tests run against local dev servers (API + Web)
  - [ ] npm run test:e2e script
  - [ ] All tests pass in headless mode
  - [ ] Builds without errors
  - [ ] No lint errors
  - [ ] New tests: 3 E2E tests
  - [ ] All tests pass
  - [ ] Docs updated: README with E2E test instructions
  - [ ] Committed with message: "test(web): add Playwright E2E tests for critical flows"
- **Plan Changes**: _(filled post-completion)_

---

## Phase 6: CI/CD & Documentation

### Task T022: Setup GitHub Actions CI Pipeline
- **Status**: pending
- **Dependencies**: T012, T020, T021
- **Estimate**: M
- **Description**: Create CI workflow to build, lint, and test on PR
- **DoD**:
  - [ ] .github/workflows/ci.yml created
  - [ ] Jobs: 
    - [ ] Backend build (.NET 9 SDK)
    - [ ] Backend tests (dotnet test)
    - [ ] Frontend build (Node.js 22, npm ci, npm run build)
    - [ ] Frontend lint (npm run lint)
    - [ ] Frontend unit tests (npm run test:unit)
    - [ ] E2E tests (Playwright with both servers running)
  - [ ] Trigger on: pull_request, push to main
  - [ ] Test matrix: Ubuntu latest (optional: Windows, macOS)
  - [ ] Parallel job execution where possible
  - [ ] Upload test results as artifacts
  - [ ] CI badge in README
  - [ ] Successfully runs on test PR
  - [ ] Builds without errors
  - [ ] No lint errors
  - [ ] New tests: N/A (CI validation)
  - [ ] All tests pass in CI
  - [ ] Docs updated: README with CI badge
  - [ ] Committed with message: "ci: add GitHub Actions workflow for build and tests"
- **Plan Changes**: _(filled post-completion)_

---

## Task Summary

| Phase | Tasks | Total Estimate |
|-------|-------|----------------|
| Environment Bootstrap | T000 | S (0.5h) ✅ |
| Project Setup | T001 | S (2h) |
| Backend API | T002-T012 | 7S + 3M = 9.5 days |
| Frontend Foundation | T013-T016 | 2S + 2M = 1.5 days |
| Frontend Features | T017-T019 | 2M + 1L = 2 days |
| Testing | T020-T021 | S + M = 1 day |
| CI/CD & Docs | T022 | M (4h) |
| **Total** | **23 tasks** | **~8-10 days** |

**Size Legend**:
- **S (Small)**: 1-2 hours
- **M (Medium)**: 3-4 hours
- **L (Large)**: 6-8 hours

---

## Execution Strategy

### Recommended Sequence
1. Complete **Phase 1** (foundation)
2. Build **Backend API** end-to-end (T002-T010) before frontend
3. Ensure **T011-T012** (API tests) pass before starting frontend
4. Build **Frontend Foundation** (T013-T016)
5. Implement **Frontend Features** (T017-T019)
6. Add **Testing** (T020-T021)
7. Finalize with **CI/CD** (T022)

### Parallel Work Opportunities
- T011 (test project setup) can happen alongside T005-T008
- T013 (frontend init) can start after T004 (API has endpoints contract)
- T020 (Vitest setup) can happen while building features

### Checkpoints
- **Checkpoint 1** (After T010): API fully functional, manually testable via Scalar
- **Checkpoint 2** (After T012): API tested, ready for frontend integration
- **Checkpoint 3** (After T019): Full application functional in dev mode
- **Checkpoint 4** (After T022): Production-ready with CI/CD

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| CORS issues between API/Web | High | Configure CORS early (T002), test with real requests |
| EF Core InMemory race conditions | Medium | Use single-threaded seeding, document limitations |
| Tailwind/shadcn version conflicts | Medium | Pin versions, follow official setup guide |
| E2E flakiness | Medium | Use Playwright's built-in waits, run locally before CI |
| CI/CD timeout with E2E tests | Low | Optimize test runtime, use parallelization |

---

## Post-MVP Enhancements (Backlog)

- **Authentication**: Add JWT-based auth with login flow
- **Multi-user**: Support multiple demo users with separate data
- **Database**: Migrate to SQL Server or PostgreSQL
- **Real-time**: Add SignalR for live balance updates
- **Export**: PDF statement generation
- **Mobile**: React Native or PWA conversion
- **Analytics**: Dashboard charts (Chart.js or Recharts)
- **Accessibility**: Full WCAG 2.1 AAA audit
- **Performance**: Lighthouse optimization, code splitting
- **Deployment**: Docker containerization, Azure/AWS hosting

---

**Document Control**  
Created: February 17, 2026  
Author: Development Team  
Status: Ready for Execution
