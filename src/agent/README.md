# Home Banking AI Agent

An intelligent banking assistant powered by Microsoft Agent Framework and Azure AI Foundry, providing natural language interaction for account management, transaction analysis, and financial insights.

## 🌟 Features

- **Account Information**: Check balances and account details across all accounts
- **Transaction Analysis**: View and analyze transaction history with filtering
- **Smart Transfers**: Execute money transfers with confirmation flow
- **Financial Insights**: Get spending analysis, category breakdowns, and trends
- **Natural Language**: Conversational interface powered by Claude Sonnet 4.5 or GPT-5.1
- **Safety First**: Requires explicit confirmation before executing transfers

## 📋 Prerequisites

- Python 3.12+ (tested with 3.14.3)
- Azure AI Foundry project with deployed model
- .NET 9 API backend running on port 5091
- Azure AI Foundry API key

## 🚀 Quick Start

### 1. Installation

```bash
cd src/agent
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file (copy from `.env.example`):

```env
# Azure AI Foundry Configuration
FOUNDRY_PROJECT_ENDPOINT=https://your-foundry-resource.services.ai.azure.com/api/projects/your-project-name
FOUNDRY_MODEL_DEPLOYMENT_NAME=your-model-deployment-name
FOUNDRY_API_KEY=your-api-key-here

# Backend API
BACKEND_API_URL=http://localhost:5091

# Agent Server
AGENT_PORT=8087

# Optional persistent Foundry agent id (migration phase)
FOUNDRY_AGENT_ID=

# Logging
LOG_LEVEL=DEBUG
```

**Get your Foundry credentials:**
1. Go to [Azure AI Foundry Portal](https://ai.azure.com)
2. Select your project
3. Navigate to "Keys and Endpoints"
4. Copy the endpoint URL and API key

### 3. Run the Agent

**CLI Mode** (for testing):
```bash
python main.py
```

**Server Mode** (authoritative HTTP runtime for web app integration):
```bash
python server.py
```

**Custom Port**:
```bash
AGENT_PORT=8088 python server.py
```

`python main.py --server` remains available and delegates to `server.py`.

## 💬 Usage Examples

### CLI Mode

```
You: What are my account balances?
Agent: Here are your current account balances:
- Main Checking (ending in 1234): $5,234.56
  Type: Checking
- Savings Account (ending in 5678): $12,450.23
  Type: Savings

You: Show my recent spending by category
Agent: Here's your spending breakdown for the last 20 transactions:
[Detailed analysis follows...]

You: Transfer $500 from checking to savings
Agent: I'd be happy to help you with that transfer. Let me confirm the details:

From: Main Checking (ending in 1234)
To: Savings Account (ending in 5678)
Amount: $500.00

Would you like me to proceed with this transfer? Please respond with "yes" to confirm.

You: yes
Agent: ✅ Transfer completed successfully! [details...]
```

### HTTP API Mode

When running in server mode, the agent exposes thread/message endpoints for the React chat widget:

```bash
POST http://localhost:8087/agent/threads
POST http://localhost:8087/agent/messages
GET  http://localhost:8087/agent/health
Content-Type: application/json

{
  "input": "What are my account balances?",
  "thread_id": "existing-thread-id"
}
```

Response is streamed as Server-Sent Events (SSE).

## 🏗️ Architecture

```
┌─────────────────┐
│   React Web UI  │  (Chat Widget)
└────────┬────────┘
         │ HTTP/SSE
         ▼
┌─────────────────┐
│  Agent Server   │  (port 8087)
│   server.py     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────┐   ┌──────────┐
│ LLM │   │ Tools    │
│Claude│   │(tools.py)│
└─────┘   └────┬─────┘
              │ HTTP
              ▼
         ┌──────────┐
         │.NET API  │ (port 5091)
         │ Backend  │
         └──────────┘
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific tests
pytest tests/test_tools.py -v
```

See [TESTING.md](TESTING.md) for detailed testing documentation.

### Debugging

#### VS Code (F5 Debugging)

1. **Agent Server Mode**:
   - Press `F5`
   - Select "Debug Agent HTTP Server"
   - Agent Inspector will open automatically
  - Set breakpoints in `server.py` or `tools.py`

2. **CLI Mode**:
   - Press `F5`
   - Select "Debug Agent CLI"
   - Interact in the integrated terminal

#### Agent Inspector

The AI Toolkit extension provides an Agent Inspector for testing:

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run "AI Studio: Open Agent Inspector"
3. Connect to `http://localhost:8087`
4. Test agent conversations with debugging

### Project Structure

```
src/agent/
├── main.py              # Agent CLI entrypoint (+ server delegator)
├── server.py            # Authoritative HTTP runtime (threads/messages)
├── tools.py             # API integration tools (4 tools)
├── analysis.py          # Financial analysis functions
├── requirements.txt     # Python dependencies
├── pytest.ini           # Test configuration
├── .env                 # Environment configuration (not committed)
├── .env.example         # Environment template
├── README.md            # This file
├── TESTING.md           # Testing documentation
└── tests/
    ├── conftest.py      # Test fixtures
    ├── test_tools.py    # Tools unit tests
    ├── test_analysis.py # Analysis unit tests
    └── test_integration.py  # Integration tests
```

## 🔧 Tools Overview

The agent has 4 tools that integrate with the .NET backend:

### 1. `get_account_balances()`
Retrieves current balances for all user accounts with masked account numbers.

### 2. `get_transactions(account_id?: string)`
Fetches transaction history, optionally filtered by account. Returns last 20 transactions.

### 3. `execute_transfer(from_account_id, to_account_id, amount, description)`
Executes a money transfer between accounts. **Requires explicit user confirmation.**

### 4. `get_spending_insights()`
Provides comprehensive financial analysis:
- Spending by category with percentages
- Top 5 largest transactions
- Income vs expenses with savings rate

## 🔒 Safety & Confirmation Flow

The agent implements a strict confirmation flow for transfers:

1. User requests a transfer
2. Agent validates inputs and presents summary
3. Agent explicitly asks for confirmation
4. Agent waits for affirmative response ("yes", "confirm", "proceed")
5. Only then does the agent execute the transfer
6. Provides confirmation with transaction details

Users can cancel anytime by saying "no", "cancel", or "stop".

## 📊 System Prompt

The agent uses a comprehensive system prompt that:
- Defines capabilities and limitations
- Enforces transfer confirmation requirements
- Specifies formatting standards (currency, account masking)
- Provides error handling guidelines
- Sets conversational tone and style

See `main.py` for the full prompt.

## 🐛 Troubleshooting

### Agent won't start

**Error**: `Missing configuration!`
- **Fix**: Ensure `.env` file exists with all required variables

**Error**: `'ChatAgent' object can't be awaited`
- **Fix**: Updated to use context managers properly (fixed in latest version)

### API connection errors

**Error**: `Connection refused` or `Connection timeout`
- **Fix**: Ensure backend API is running on port 5091
```bash
cd src/api
dotnet run
```

### Model/Foundry issues

**Error**: `Unauthorized` or `Invalid API key`
- **Fix**: Verify API key in `.env` is correct and not expired

**Error**: `Model not found`
- **Fix**: Confirm model deployment name matches your Foundry project

### Tool errors

**Error**: Tools return "Error: ..."
- **Fix**: Check backend API logs for issues
- **Fix**: Verify backend API URL is correct in `.env`

## 📝 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FOUNDRY_PROJECT_ENDPOINT` | Yes | Azure Foundry endpoint URL | `https://xxx.openai.azure.com/anthropic/v1/messages` |
| `FOUNDRY_MODEL_DEPLOYMENT_NAME` | Yes | Deployed model name | `claude-sonnet-4-5` |
| `FOUNDRY_API_KEY` | Yes | Foundry API key | `3SAUx81E4...` |
| `BACKEND_API_URL` | No | Backend API base URL | `http://localhost:5091` (default) |
| `AGENT_PORT` | No | Agent server port | `8087` (default) |
| `LOG_LEVEL` | No | Logging verbosity | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## 🔄 CI/CD Integration

### Running in Production

1. Set environment variables appropriately
2. Use production Foundry endpoint
3. Configure logging to file/monitoring system
4. Run in server mode with process manager (PM2, systemd)

```bash
# Example with systemd
[Unit]
Description=Home Banking Agent
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/app/src/agent
Environment="FOUNDRY_API_KEY=xxx"
ExecStart=/usr/bin/python3 main.py --server --port 8087
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📚 Additional Resources

- [Microsoft Agent Framework Docs](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry Portal](https://ai.azure.com)
- [Claude API Documentation](https://docs.anthropic.com)

## 🤝 Contributing

When contributing:
1. Write tests for new features
2. Ensure all tests pass (`pytest tests/`)
3. Update documentation
4. Follow existing code style

## 📜 License

This project is part of the Home Banking application.

## 🆘 Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review test files for usage examples
3. Check backend API logs
4. Verify Foundry model deployment status

---

**Built with** ❤️ **using Microsoft Agent Framework and Azure AI Foundry**
