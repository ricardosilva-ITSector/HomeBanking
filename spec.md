# Home Banking Application - Technical Specification

**Version**: 1.0  
**Last Updated**: February 17, 2026  
**Status**: Draft

---

## 1. Overview

A modern home banking demo application showcasing account management, transaction history, and money transfers. Built as a monorepo with .NET Core 9 API backend and React+Vite frontend, designed for demonstration and portfolio purposes.

---

## 2. Functional Requirements

### 2.1 Core Features

#### FR-001: Account Balance Display
- **Description**: Display user account balances in card format
- **Details**:
  - Show account name, account number, current balance
  - Support multiple accounts (checking, savings)
  - Real-time balance updates after transfers
  - Currency formatting (USD with proper localization)

#### FR-002: Transaction History
- **Description**: Display chronological list of account transactions
- **Details**:
  - Show date, description, amount, category, balance after transaction
  - Visual category badges with color coding
  - Sort by date (newest first)
  - Filter by account (if multiple accounts)
  - Paginated or scrollable list (100+ transactions)

#### FR-003: Money Transfer
- **Description**: Transfer funds between user accounts
- **Details**:
  - Select source and destination accounts
  - Enter amount and optional description
  - Client-side and server-side validation
  - Immediate balance update upon success
  - Transaction confirmation/feedback

#### FR-004: Transaction Categories
- **Description**: Categorize transactions for better organization
- **Supported Categories**:
  - Income: Salary, Refund
  - Expenses: Groceries, Utilities, Entertainment, Transport, Shopping, Healthcare
  - Transfers: Internal Transfer
- **Visual Treatment**: Color-coded badges in transaction list

### 2.2 Validation Rules

#### VR-001: Transfer Amount
- Minimum: $0.01
- Maximum: $10,000 per transaction
- Must be positive number with max 2 decimal places

#### VR-002: Sufficient Balance
- Source account must have sufficient funds
- Overdraft not permitted

#### VR-003: Account Validation
- Source and destination accounts must exist
- Cannot transfer to same account (prevent self-transfer)
- Must be user's own accounts

#### VR-004: Input Sanitization
- Description max length: 200 characters
- No script injection in text fields
- Proper decimal formatting

---

## 3. Non-Functional Requirements

### 3.1 Performance

#### NFR-001: API Response Time
- **Target**: 95th percentile < 200ms for all endpoints
- **Measurement**: Logged via health check metrics
- **Constraints**: InMemory database ensures fast queries

#### NFR-002: Frontend Load Time
- **Target**: First Contentful Paint < 1.5s
- **Strategy**: Vite optimization, code splitting, lazy loading
- **Bundle Size**: Initial bundle < 200KB (gzipped)

#### NFR-003: Concurrent Users
- **Target**: Support 100 concurrent users (demo scenario)
- **Scaling**: Stateless API design for horizontal scaling readiness

### 3.2 Accessibility

#### NFR-004: WCAG 2.1 Level AA Compliance
- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Screen Reader Support**: Proper ARIA labels, semantic HTML
- **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Focus Indicators**: Visible focus states on all interactive elements

#### NFR-005: Responsive Design
- **Breakpoints**: Mobile (320px+), Tablet (768px+), Desktop (1024px+)
- **Touch Targets**: Minimum 44x44px for interactive elements
- **Text Scaling**: Support up to 200% zoom without loss of functionality

### 3.3 Browser Support
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

### 3.4 Code Quality
- **Test Coverage**: Minimum 80% for business logic
- **Linting**: ESLint (frontend), Roslyn analyzers (backend)
- **Type Safety**: TypeScript strict mode, C# nullable reference types enabled

---

## 4. Architecture Overview

### 4.1 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Client Browser                    │
│                 (React + Vite + TS)                  │
└───────────────────┬──────────────────────────────────┘
                    │ HTTP/JSON
                    │ (REST API)
┌───────────────────▼──────────────────────────────────┐
│              .NET Core 9 Web API                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ Controllers  │─▶│   Services   │─▶│ DbContext │  │
│  └──────────────┘  └──────────────┘  └─────┬─────┘  │
│         │                                   │        │
│         │ OpenAPI/Scalar                    │        │
│         ▼                                   ▼        │
│  ┌──────────────┐              ┌────────────────┐   │
│  │  Health      │              │  EF Core       │   │
│  │  Checks      │              │  InMemory DB   │   │
│  └──────────────┘              └────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 4.2 Folder Structure

```
HomeBanking/
├── .github/
│   └── workflows/
│       └── ci.yml                    # CI pipeline
├── src/
│   ├── api/                          # Backend (.NET Core 9)
│   │   ├── HomeBanking.Api/
│   │   │   ├── Controllers/          # API endpoints
│   │   │   ├── Models/               # Domain models
│   │   │   ├── Data/                 # EF Core DbContext
│   │   │   ├── Services/             # Business logic
│   │   │   ├── Validators/           # Input validation
│   │   │   ├── Program.cs            # App configuration
│   │   │   └── appsettings.json
│   │   └── HomeBanking.Api.Tests/
│   │       ├── Controllers/          # Controller unit tests
│   │       └── Services/             # Service unit tests
│   │
│   └── web/                          # Frontend (React+Vite+TS)
│       ├── src/
│       │   ├── components/           # React components
│       │   │   ├── ui/               # shadcn/ui components
│       │   │   ├── AccountCard.tsx
│       │   │   ├── TransactionList.tsx
│       │   │   └── TransferForm.tsx
│       │   ├── lib/                  # Utilities
│       │   │   ├── api.ts            # API client
│       │   │   └── utils.ts
│       │   ├── hooks/                # Custom React hooks
│       │   ├── types/                # TypeScript interfaces
│       │   ├── App.tsx
│       │   ├── main.tsx
│       │   └── index.css
│       ├── tests/
│       │   ├── unit/                 # Vitest unit tests
│       │   └── e2e/                  # Playwright E2E tests
│       ├── public/
│       ├── package.json
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       ├── tsconfig.json
│       └── playwright.config.ts
├── docs/
│   ├── api.md                        # API documentation
│   └── development.md                # Dev setup guide
├── .gitignore
├── README.md
├── spec.md                           # This file
└── plan.md                           # Implementation plan
```

### 4.3 API Contracts

#### 4.3.1 Endpoints

##### GET /api/accounts
**Description**: Retrieve all user accounts  
**Response**: 200 OK
```json
[
  {
    "id": "string (GUID)",
    "accountNumber": "string",
    "accountName": "string",
    "accountType": "checking | savings",
    "balance": 0.00,
    "currency": "USD"
  }
]
```

##### GET /api/transactions?accountId={optional}
**Description**: Retrieve transaction history  
**Query Parameters**: 
- `accountId` (optional): Filter by account
- `limit` (optional): Max results (default: 100)
- `offset` (optional): Pagination offset

**Response**: 200 OK
```json
{
  "transactions": [
    {
      "id": "string (GUID)",
      "accountId": "string (GUID)",
      "date": "ISO-8601 datetime",
      "description": "string",
      "amount": 0.00,
      "type": "debit | credit",
      "category": "string",
      "balanceAfter": 0.00
    }
  ],
  "total": 0
}
```

##### POST /api/transfers
**Description**: Create a new transfer  
**Request Body**:
```json
{
  "fromAccountId": "string (GUID)",
  "toAccountId": "string (GUID)",
  "amount": 0.00,
  "description": "string (optional)"
}
```

**Response**: 201 Created
```json
{
  "transferId": "string (GUID)",
  "fromTransaction": { /* transaction object */ },
  "toTransaction": { /* transaction object */ },
  "timestamp": "ISO-8601 datetime"
}
```

**Error Response**: 400 Bad Request
```json
{
  "error": "string",
  "validationErrors": {
    "field": ["error message"]
  }
}
```

##### GET /health
**Description**: Health check endpoint  
**Response**: 200 OK
```json
{
  "status": "Healthy",
  "checks": {
    "database": "Healthy"
  }
}
```

##### GET /scalar/v1
**Description**: Interactive API documentation (Scalar UI)

---

## 5. Technology Stack

### 5.1 Backend (.NET Core 9 API)

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| .NET Core | 9.0 | Runtime framework | Latest LTS, best performance, C# 13 features |
| ASP.NET Core | 9.0 | Web API framework | Built-in DI, middleware, minimal APIs support |
| Entity Framework Core | 9.0 | ORM | InMemory provider for demo, migration-ready |
| Scalar.AspNetCore | 1.2+ | API documentation | Modern OpenAPI UI, superior to Swagger |
| Microsoft.AspNetCore.Diagnostics.HealthChecks | 9.0 | Health monitoring | Built-in health check framework |
| xUnit | 2.9+ | Test framework | Industry standard for .NET |
| FluentAssertions | 7.0+ | Test assertions | Readable test assertions |
| Moq | 4.20+ | Mocking framework | Unit test isolation |

**Configuration**:
```xml
<PropertyGroup>
  <TargetFramework>net9.0</TargetFramework>
  <Nullable>enable</Nullable>
  <ImplicitUsings>enable</ImplicitUsings>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
</PropertyGroup>
```

### 5.2 Frontend (React + Vite + TypeScript)

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| React | 18.3+ | UI framework | Ecosystem maturity, performance, hooks |
| TypeScript | 5.7+ | Type safety | Catch errors at compile-time, better DX |
| Vite | 6.0+ | Build tool | Fast HMR, optimized builds, ESM native |
| @vitejs/plugin-react-swc | 3.7+ | React compiler | Faster builds than Babel (SWC) |
| Tailwind CSS | 4.0+ | Styling framework | Utility-first, consistent design system |
| shadcn/ui | latest | Component library | Accessible, customizable, copy-paste |
| Radix UI | - | Headless components | Accessibility primitives for shadcn |
| Vitest | 2.1+ | Test framework | Vite-native, fast, Jest-compatible API |
| @testing-library/react | 16.0+ | Component testing | User-centric testing approach |
| Playwright | 1.48+ | E2E testing | Cross-browser, reliable, great DX |
| ESLint | 9.0+ | Linting | Code quality, consistency |
| Prettier | 3.4+ | Formatting | Opinionated code formatting |

**Key Dependencies**:
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "tailwindcss": "^4.0.0",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.4",
    "lucide-react": "^0.468.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react-swc": "^3.7.2",
    "vite": "^6.0.3",
    "typescript": "^5.7.0",
    "vitest": "^2.1.8",
    "@playwright/test": "^1.48.0",
    "eslint": "^9.17.0",
    "prettier": "^3.4.2"
  }
}
```

**TypeScript Configuration**:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "react-jsx"
  }
}
```

### 5.3 CI/CD

| Technology | Version | Purpose |
|------------|---------|---------|
| GitHub Actions | - | CI pipeline |
| .NET SDK | 9.0 | Backend builds |
| Node.js | 22 LTS | Frontend builds |

---

## 6. Key Design Decisions

### 6.1 Monorepo Structure
**Decision**: Single repository with `src/api` and `src/web` folders  
**Rationale**:
- Simplified dependency management
- Atomic commits across frontend/backend
- Shared CI/CD pipeline
- Easier local development setup
- Single source of truth for versioning

**Trade-offs**:
- Larger repository size
- Potential for coupling (mitigated by clear boundaries)

### 6.2 InMemory Database
**Decision**: Use EF Core InMemory provider (no persistence)  
**Rationale**:
- Zero infrastructure setup for demos
- Fast query performance
- Easy to seed with demo data
- Migration-ready for real database
- Ideal for portfolio/showcase purposes

**Migration Path**: Replace `UseInMemoryDatabase()` with `UseSqlServer()` or `UseNpgsql()` for production

### 6.3 Demo Mode (No Authentication)
**Decision**: No login/authentication system  
**Rationale**:
- Reduces complexity for demo app
- Faster initial development
- Focus on core banking features
- Easier for reviewers to test

**Future Enhancement**: Add JWT authentication when needed

### 6.4 Scalar over Swagger
**Decision**: Use Scalar for OpenAPI documentation  
**Rationale**:
- Modern, beautiful UI (better UX)
- Better dark mode support
- Improved code generation features
- Lightweight and fast
- Active development and support

### 6.5 React + Vite over Create React App
**Decision**: Use Vite as build tool  
**Rationale**:
- CRA is deprecated (no longer maintained)
- 10-100x faster HMR during development
- Smaller bundle sizes (native ESM)
- Better plugin ecosystem
- Lower configuration overhead

### 6.6 shadcn/ui over Material-UI
**Decision**: Copy-paste component library (shadcn/ui)  
**Rationale**:
- Full control over component code (no black box)
- Built on Radix UI (accessibility-first)
- Tailwind integration (consistent styling)
- Smaller bundle size (only include used components)
- Easy customization without fighting framework

### 6.7 Dark Theme as Default
**Decision**: Dark theme with no light mode toggle (v1)  
**Rationale**:
- Modern aesthetic for demo
- Reduced scope for MVP
- Easier color palette management
- Bank card visuals work better in dark

**Future Enhancement**: Add theme switcher in v2

### 6.8 Client-Side Routing NOT Included
**Decision**: Single-page dashboard (no React Router)  
**Rationale**:
- All features fit on one page
- Simplified state management
- No navigation complexity
- Faster initial load

**Future Enhancement**: Add routing for multi-page flows

### 6.9 Form Validation Strategy
**Decision**: Dual validation (client + server)  
**Client**: Immediate feedback, UX improvement  
**Server**: Security boundary, data integrity  
**Libraries**: 
- Frontend: Native HTML5 validation + custom hooks
- Backend: FluentValidation or Data Annotations

### 6.10 E2E Test Strategy
**Decision**: Playwright for E2E tests in CI  
**Rationale**:
- Cross-browser support out of box
- Better reliability than Selenium
- Built-in wait mechanisms
- Video/screenshot debugging
- Parallel test execution

**CI Integration**: Run on PR, fail build on test failure

---

## 7. Data Model

### 7.1 Account Entity
```csharp
public class Account
{
    public Guid Id { get; set; }
    public string AccountNumber { get; set; } // e.g., "4532-1234-5678-9010"
    public string AccountName { get; set; }   // e.g., "Primary Checking"
    public AccountType Type { get; set; }     // Checking, Savings
    public decimal Balance { get; set; }
    public string Currency { get; set; } = "USD";
    public DateTime CreatedAt { get; set; }
    
    public ICollection<Transaction> Transactions { get; set; }
}

public enum AccountType
{
    Checking,
    Savings
}
```

### 7.2 Transaction Entity
```csharp
public class Transaction
{
    public Guid Id { get; set; }
    public Guid AccountId { get; set; }
    public DateTime Date { get; set; }
    public string Description { get; set; }
    public decimal Amount { get; set; }
    public TransactionType Type { get; set; } // Debit, Credit
    public string Category { get; set; }
    public decimal BalanceAfter { get; set; }
    
    public Account Account { get; set; }
}

public enum TransactionType
{
    Debit,   // Money out
    Credit   // Money in
}
```

### 7.3 Demo Data Seed
- 2 accounts: Primary Checking ($5,000), Savings ($15,000)
- 50+ transactions with realistic dates (last 90 days)
- Variety of categories (salary, groceries, utilities, etc.)
- Mix of debits and credits

---

## 8. Success Criteria

### 8.1 MVP Completion
- ✅ All functional requirements implemented
- ✅ Unit tests: 80%+ coverage
- ✅ E2E tests: 3 critical flows passing
- ✅ API documented (Scalar)
- ✅ Accessible (keyboard nav, screen reader basics)
- ✅ CI pipeline: builds, lints, tests
- ✅ Dark theme responsive design

### 8.2 Performance Benchmarks
- API response time: p95 < 200ms
- Bundle size: < 200KB (gzipped)
- Lighthouse score: 90+ (Performance, Accessibility)

### 8.3 Code Quality
- No ESLint/compiler warnings
- All tests passing
- Clean git history with conventional commits

---

## 9. Out of Scope (v1)

- User authentication/authorization
- Multiple user accounts (single demo user)
- Database persistence (InMemory only)
- External account transfers
- Bill pay functionality
- Account statements/exports
- Mobile native apps
- Real-time notifications
- Internationalization (English only)
- Backend for Frontend (BFF) pattern

---

## 10. References

- [.NET 9 Documentation](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-9)
- [React 18 Docs](https://react.dev/)
- [Vite Guide](https://vite.dev/guide/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Scalar API Reference](https://github.com/scalar/scalar)
- [Playwright Docs](https://playwright.dev/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Document Control**  
Created: February 17, 2026  
Author: Development Team  
Approved: Pending
