# HomeBanking Agent Service

Conversational transfer copilot powered by Microsoft Agent Framework and Azure AI Foundry Agent Service.

## Architecture

- **Runtime**: Python sidecar service
- **Framework**: Microsoft Agent Framework
- **AI Platform**: Azure AI Foundry Agent Service
- **Integration**: Calls existing HomeBanking .NET API (`/api/accounts`, `/api/transactions`, `/api/transfers`)

## Prerequisites

1. **Python 3.10+** installed
2. **Azure subscription** with access to Azure AI Foundry
3. **Foundry project** created with a deployed model (e.g., gpt-4o, gpt-4.1)
4. **HomeBanking API** running locally at `http://localhost:5091` (or configured endpoint)

## Setup

### 1. Create Python Virtual Environment

```powershell
# From repository root
cd src/agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify activation (should show .venv path)
python -c "import sys; print(sys.executable)"
```

### 2. Install Dependencies

```powershell
# Install pinned Agent Framework dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy template to .env
Copy-Item .env.template .env

# Edit .env with your values
notepad .env
```

**Required configuration:**
- `FOUNDRY_PROJECT_ENDPOINT`: Your Foundry project endpoint from Azure portal
- `FOUNDRY_MODEL_DEPLOYMENT_NAME`: Name of deployed model in your Foundry project
- `HOMEBANKING_API_BASE_URL`: Base URL for HomeBanking API (default: `http://localhost:5091`)

### 4. Get Foundry Configuration

**📖 Complete Setup Guide**: See [docs/foundry-setup.md](../../docs/foundry-setup.md) for detailed step-by-step instructions including:
- Creating an Azure AI Foundry project
- Deploying a language model
- Configuring authentication
- Assigning required permissions
- Cost considerations

**Quick Reference** (if you already have Foundry setup):

From [Azure AI Foundry portal](https://ai.azure.com):
1. Select your project → **Project settings** → **Properties**
2. Copy **Project endpoint**
3. Note your **deployment name** from **Deployments** section

Or via Azure CLI:
```powershell
# Get project endpoint
az cognitiveservices account show \
  --name <your-foundry-resource> \
  --resource-group <your-rg> \
  --query properties.endpoint -o tsv
```

### 5. Authenticate to Azure

The agent uses `DefaultAzureCredential` which supports multiple auth methods:

```powershell
# Option 1: Azure CLI (recommended for local development)
az login

# Option 2: Set environment variables
$env:AZURE_CLIENT_ID = "<your-client-id>"
$env:AZURE_TENANT_ID = "<your-tenant-id>"
$env:AZURE_CLIENT_SECRET = "<your-client-secret>"
```

For production, use **Managed Identity** (planned post-MVP).

## Running the Agent

### Start HomeBanking API First

```powershell
# In separate terminal, from repository root
cd src/api
dotnet run
```

Verify API is running at: `http://localhost:5091/health`

### Start Agent Service

```powershell
# From src/agent directory with venv activated
python main.py
```

Expected output:
```
{"event": "Loading configuration", "timestamp": "..."}
{"event": "Configuration loaded", "foundry_endpoint": "...", ...}
{"event": "✓ Agent sidecar initialized successfully", ...}
```

## Development

### Run Tests

```powershell
pytest
```

### Enable Debug Mode

```powershell
# Set log level in .env
LOG_LEVEL=DEBUG

# Run with verbose output
python main.py
```

### VS Code Debugging

See `.vscode/launch.json` for Python debugger configuration (to be added in A003).

## Project Status

**Current**: A002 - Sidecar scaffolding complete ✓

**Next Steps**:
- A001: Document Foundry prerequisites
- A003: Implement agent workflow with tools
- A004: Add read tool implementations
- A005: Add transfer tool with confirmation gate

See [plan-agent.md](../../plan-agent.md) for full roadmap.

## Troubleshooting

### Import Errors

```
ModuleNotFoundError: No module named 'agent_framework'
```
**Fix**: Ensure virtual environment is activated and dependencies installed:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Authentication Errors

```
DefaultAzureCredentialError: No credential available
```
**Fix**: Run `az login` or set Azure environment variables.

### API Connection Errors

```
Failed to retrieve accounts: Connection refused
```
**Fix**: Ensure HomeBanking API is running at configured `HOMEBANKING_API_BASE_URL`.

## Architecture Diagram

```
┌─────────────────┐
│  React Web App  │
│  (src/web)      │
└────────┬────────┘
         │ HTTP
         v
┌─────────────────┐      HTTP        ┌──────────────────┐
│  .NET API       │◄─────────────────┤  Agent Sidecar   │
│  (src/api)      │      (internal)  │  (src/agent)     │
│                 │                  │  Python + AF     │
│  Controllers:   │                  └────────┬─────────┘
│  - Accounts     │                           │
│  - Transactions │                           │ SDK
│  - Transfers    │                           v
└────────┬────────┘                  ┌──────────────────┐
         │                           │  Azure Foundry   │
         v                           │  Agent Service   │
  ┌─────────────┐                    └──────────────────┘
  │ InMemory DB │
  └─────────────┘
```

## Security Notes (MVP)

- Secrets in `.env` file (not committed to git)
- Agent endpoint exposed only to trusted internal boundary
- Post-MVP: Migrate to Managed Identity + RBAC

## References

- [Microsoft Agent Framework Docs](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry Agent Service](https://learn.microsoft.com/azure/ai-foundry/agents/)
- [Project Spec](../../spec-agent.md)
- [Implementation Plan](../../plan-agent.md)
