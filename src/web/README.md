# HomeBanking Frontend

React + TypeScript + Vite frontend for the HomeBanking application.

## Prerequisites

- Node.js 18+ (LTS recommended)
- npm 9+

## Technology Stack

- **React** 19.2.0 - UI framework
- **TypeScript** 5.9.3 - Type-safe JavaScript
- **Vite** 7.3.1 - Build tool and dev server
- **@vitejs/plugin-react-swc** - Fast Refresh using SWC
- **ESLint** 9.39.1 - Code quality and linting
- **Prettier** - Code formatting

## Getting Started

### Installation

Install dependencies:

```bash
npm install
```

### Development

Start the development server (runs on http://localhost:5173):

```bash
npm run dev
```

The dev server includes Hot Module Replacement (HMR) for fast development.

### API Proxy

All `/api` and `/health` requests are automatically proxied to `http://localhost:5000` (the backend API).

**Note**: Ensure the backend API is running on port 5000 before starting the frontend development server.

### Build

Build for production:

```bash
npm run build
```

Production build will be output to the `dist/` directory.

### Preview

Preview the production build locally:

```bash
npm run preview
```

### Linting

Run ESLint to check code quality:

```bash
npm run lint
```

ESLint is configured with:
- TypeScript ESLint recommended rules
- React Hooks rules
- React Refresh rules

## Project Structure

```
src/web/
├── public/          # Static assets
├── src/             # Application source code
│   ├── assets/      # Images, fonts, etc.
│   ├── App.tsx      # Root component
│   ├── main.tsx     # Application entry point
│   └── index.css    # Global styles
├── index.html       # HTML entry point
├── vite.config.ts   # Vite configuration
├── tsconfig.json    # TypeScript configuration (root)
├── tsconfig.app.json # TypeScript configuration (app)
└── eslint.config.js # ESLint configuration
```

## Configuration Files

- **vite.config.ts**: Vite build configuration with API proxy settings
- **tsconfig.app.json**: TypeScript strict mode enabled
- **eslint.config.js**: ESLint with TypeScript and React rules
- **.prettierrc.json**: Prettier code formatting rules

## Testing

### Unit Testing

Run unit tests with Vitest:

```bash
npm run test
```

### E2E Testing

This project uses **Playwright** for end-to-end testing.

#### Prerequisites

Before running E2E tests, ensure:
1. **Backend API server** is running on `http://localhost:5000`
2. **Frontend dev server** is running on `http://localhost:5173`

#### Install Browsers

If you haven't installed Playwright browsers yet:

```bash
npx playwright install
```

#### Run E2E Tests

Run all E2E tests in headless mode:

```bash
npm run test:e2e
```

Run E2E tests with Playwright UI (for debugging and interactive mode):

```bash
npm run test:e2e:ui
```

#### E2E Test Coverage

The E2E test suite includes:
- **Dashboard**: Verifies accounts and transactions are loaded
- **Transactions**: Validates transaction list with categories  
- **Transfer**: Tests complete transfer flow end-to-end

All tests include screenshots on failure for debugging.

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server on http://localhost:5173 |
| `npm run build` | Build for production |
| `npm run lint` | Run ESLint |
| `npm run preview` | Preview production build |
| `npm run test` | Run unit tests with Vitest |
| `npm run test:e2e` | Run E2E tests with Playwright (headless) |
| `npm run test:e2e:ui` | Run E2E tests with Playwright UI |

## Development Notes

- TypeScript is configured with **strict mode** enabled
- ESLint enforces code quality rules for TypeScript and React
- Prettier ensures consistent code formatting
- Vite provides fast HMR during development

import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
