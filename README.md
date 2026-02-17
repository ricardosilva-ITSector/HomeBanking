# Home Banking Application

A modern home banking demo application showcasing account management, transaction history, and money transfers. Built with .NET Core 9 API backend and React+Vite frontend as a demonstration and portfolio project.

[![.NET](https://img.shields.io/badge/.NET-9.0-512BD4?logo=dotnet)](https://dotnet.microsoft.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-7.3-646CFF?logo=vite)](https://vite.dev/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Testing](#-testing)
- [API Documentation](#-api-documentation)
- [Technology Stack](#-technology-stack)
- [Design Decisions](#-design-decisions)
- [Contributing](#-contributing)

---

## ✨ Features

- **Account Balance Display**: View multiple accounts (checking, savings) with real-time balance updates
- **Transaction History**: Chronological transaction list with category badges, date sorting, and filtering
- **Money Transfer**: Transfer funds between accounts with client and server-side validation
- **Transaction Categories**: Color-coded categories (Income, Expenses, Transfers)
- **Modern UI**: Dark theme with responsive design, built with Tailwind CSS and shadcn/ui
- **API Documentation**: Interactive API docs powered by Scalar
- **Accessibility**: WCAG 2.1 Level AA compliant with keyboard navigation and screen reader support

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

### Required

- **.NET 9 SDK** (9.0 or higher)
  - Download: https://dotnet.microsoft.com/download/dotnet/9.0
  - Verify: `dotnet --version`

- **Node.js** (22 LTS or higher)
  - Download: https://nodejs.org/
  - Verify: `node --version`

- **npm** (10+ or higher, comes with Node.js)
  - Verify: `npm --version`

### Recommended

- **Visual Studio 2022** (17.8+) or **Visual Studio Code** with C# extension
- **Git** for version control
- **Windows Terminal** or equivalent for better command-line experience

---

## 🚀 Quick Start

### 1. Clone the Repository

```powershell
git clone https://github.com/yourusername/HomeBanking.git
cd HomeBanking
```

### 2. Backend Setup (API)

```powershell
# Navigate to API project
cd src/api

# Restore dependencies
dotnet restore

# Build the project
dotnet build --configuration Release

# Run the API (starts on https://localhost:5001)
dotnet run
```

The API will be available at:
- HTTPS: `https://localhost:5001`
- HTTP: `http://localhost:5000`
- API docs: `https://localhost:5001/scalar/v1`

### 3. Frontend Setup (Web)

Open a **new terminal window** and:

```powershell
# Navigate to web project
cd src/web

# Install dependencies
npm install

# Start development server (runs on http://localhost:5173)
npm run dev
```

The web application will be available at:
- Development: `http://localhost:5173`

### 4. Access the Application

1. Ensure both API and web servers are running
2. Open your browser to `http://localhost:5173`
3. Start exploring accounts, transactions, and transfers!

---

## 📁 Project Structure

```
HomeBanking/
├── .github/
│   └── workflows/
│       └── ci.yml                    # CI/CD pipeline (GitHub Actions)
├── docs/                             # Additional documentation
├── src/
│   ├── api/                          # Backend (.NET Core 9)
│   │   ├── Controllers/              # API endpoints
│   │   ├── Models/                   # Domain models (Account, Transaction)
│   │   ├── Data/                     # EF Core DbContext
│   │   ├── Services/                 # Business logic (transfer service)
│   │   ├── Validators/               # Input validation
│   │   ├── Program.cs                # Application configuration
│   │   ├── appsettings.json          # API settings
│   │   └── HomeBanking.Api.csproj
│   │
│   └── web/                          # Frontend (React + Vite + TypeScript)
│       ├── src/
│       │   ├── components/           # React components
│       │   │   ├── ui/               # shadcn/ui components
│       │   │   ├── AccountCard.tsx   # Account display
│       │   │   ├── TransactionList.tsx
│       │   │   └── TransferForm.tsx
│       │   ├── lib/                  # Utilities and API client
│       │   ├── hooks/                # Custom React hooks
│       │   ├── types/                # TypeScript interfaces
│       │   ├── App.tsx               # Main application component
│       │   └── main.tsx              # Application entry point
│       ├── tests/
│       │   ├── unit/                 # Vitest unit tests
│       │   └── e2e/                  # Playwright E2E tests
│       ├── package.json
│       ├── vite.config.ts            # Vite configuration
│       ├── tailwind.config.js        # Tailwind CSS config
│       └── tsconfig.json             # TypeScript config
├── .gitignore
├── README.md                         # This file
├── spec.md                           # Technical specification
└── plan.md                           # Implementation plan
```

---

## 💻 Development

### Backend Development

#### Running the API

```powershell
cd src/api
dotnet run
```

#### Building for Production

```powershell
dotnet build --configuration Release
```

#### Running Tests

```powershell
dotnet test --verbosity normal
```

#### Code Quality

```powershell
# Restore dependencies
dotnet restore

# Build with warnings as errors
dotnet build --configuration Release /p:TreatWarningsAsErrors=true

# Run code analysis
dotnet build /p:EnforceCodeStyleInBuild=true
```

### Frontend Development

#### Running Dev Server

```powershell
cd src/web
npm run dev
```

#### Building for Production

```powershell
npm run build
```

The production build will be in `src/web/dist/`.

#### Preview Production Build

```powershell
npm run preview
```

#### Code Quality

```powershell
# Lint code
npm run lint

# Type check
npm run type-check
# or
npx tsc --noEmit

# Format code (if Prettier is configured)
npm run format
```

### Environment Variables

#### Backend (src/api/appsettings.json)

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  },
  "AllowedHosts": "*",
  "Cors": {
    "AllowedOrigins": ["http://localhost:5173"]
  }
}
```

#### Frontend (src/web/.env)

Create a `.env` file if needed:

```env
VITE_API_BASE_URL=http://localhost:5000
```

---

## 🧪 Testing

### Backend Tests (xUnit)

```powershell
cd src/api

# Run all tests
dotnet test

# Run with coverage
dotnet test /p:CollectCoverage=true

# Run specific test
dotnet test --filter "FullyQualifiedName~TransferServiceTests"
```

### Frontend Tests

#### Unit Tests (Vitest)

```powershell
cd src/web

# Run unit tests
npm run test:unit

# Run with watch mode
npm run test:unit -- --watch

# Run with coverage
npm run test:unit -- --coverage
```

#### E2E Tests (Playwright)

```powershell
cd src/web

# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests (requires API running at localhost:5000)
npm run test:e2e

# Run E2E tests in UI mode
npm run test:e2e -- --ui

# Run specific test file
npm run test:e2e tests/e2e/transfer.spec.ts
```

**Important**: E2E tests require both the API and frontend servers to be running.

### Full Validation (Pre-Push)

Run this complete validation before pushing to ensure CI will pass:

```powershell
# From repository root

# 1. Backend validation
cd src/api
dotnet restore
dotnet build --configuration Release /p:TreatWarningsAsErrors=true
dotnet test --configuration Release

# 2. Frontend validation
cd ../web
npm ci
npm run lint
npm run build
npm run test:unit

# 3. E2E tests (in separate terminals)
# Terminal 1: cd src/api && dotnet run
# Terminal 2: cd src/web && npm run dev
# Terminal 3: cd src/web && npm run test:e2e
```

---

## 📚 API Documentation

### Interactive API Documentation

Once the API is running, access the interactive Scalar API documentation:

**URL**: `https://localhost:5001/scalar/v1`

The Scalar interface provides:
- Complete API endpoint reference
- Request/response schemas
- Interactive request testing
- Code generation examples

### API Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/accounts` | Retrieve all user accounts |
| `GET` | `/api/transactions` | Retrieve transaction history (with optional filtering) |
| `POST` | `/api/transfers` | Create a new transfer between accounts |
| `GET` | `/health` | Health check endpoint |

### Example API Calls

#### Get All Accounts

```bash
curl https://localhost:5001/api/accounts
```

#### Get Transactions (with filtering)

```bash
curl "https://localhost:5001/api/transactions?accountId=<guid>&limit=50"
```

#### Create Transfer

```bash
curl -X POST https://localhost:5001/api/transfers \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccountId": "guid-here",
    "toAccountId": "guid-here",
    "amount": 100.00,
    "description": "Monthly transfer"
  }'
```

---

## 🔧 Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| .NET Core | 9.0 | Runtime framework |
| ASP.NET Core | 9.0 | Web API framework |
| Entity Framework Core | 9.0 | ORM with InMemory provider |
| Scalar.AspNetCore | 1.2+ | API documentation |
| xUnit | 2.9+ | Test framework |
| FluentAssertions | 7.0+ | Test assertions |
| Moq | 4.20+ | Mocking framework |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3+ | UI framework |
| TypeScript | 5.9+ | Type safety |
| Vite | 7.3+ | Build tool |
| Tailwind CSS | 4.0+ | Styling framework |
| shadcn/ui | latest | Component library |
| Radix UI | latest | Accessible primitives |
| Vitest | 2.1+ | Unit testing |
| Playwright | 1.48+ | E2E testing |
| ESLint | 9.0+ | Linting |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| GitHub Actions | CI/CD pipeline |
| EF Core InMemory | Demo database (no persistence) |

---

## 🎯 Design Decisions

### Why Monorepo?

- Simplified dependency management
- Atomic commits across frontend/backend
- Shared CI/CD pipeline
- Single source of truth for versioning

### Why InMemory Database?

- Zero infrastructure setup for demos
- Fast query performance
- Easy to seed with demo data
- Migration-ready for real database

### Why Vite over Create React App?

- CRA is deprecated
- 10-100x faster HMR during development
- Smaller bundle sizes
- Better plugin ecosystem

### Why Scalar over Swagger?

- Modern, beautiful UI
- Better dark mode support
- Improved code generation features
- Active development

### Why No Authentication?

- Reduces complexity for demo
- Focus on core banking features
- Easier for reviewers to test
- Can add JWT authentication later

---

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run tests and validation (see [Testing](#-testing))
5. Commit using conventional commits: `git commit -m "feat(api): add feature"`
6. Push to your fork: `git push origin feat/your-feature`
7. Open a Pull Request

### Commit Message Convention

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat(scope): add new feature`
- `fix(scope): fix bug`
- `docs(scope): update documentation`
- `test(scope): add tests`
- `refactor(scope): refactor code`
- `chore(scope): maintenance task`
- `ci(scope): CI/CD changes`

### Code Quality Requirements

- All tests must pass
- No ESLint warnings
- No compiler warnings
- Code coverage maintained or improved
- Documentation updated

---

## 📄 License

This project is for demonstration and portfolio purposes.

---

## 📞 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using .NET 9 and React**