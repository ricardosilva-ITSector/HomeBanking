# Home Banking AI Agent - Implementation Plan

**Version**: 1.0  
**Last Updated**: February 18, 2026  
**Total Tasks**: 12 (TA-000 to TA-011)  
**Estimated Duration**: 5-7 days (single developer)

---

## Definition of Done (DoD) - MANDATORY GATE

**Purpose**: Every task must pass this gate before being marked complete. These criteria ensure quality, maintainability, and production readiness.

### Core Principles

1. **Incremental Progress**: Each task is independently testable and functional
2. **Known Good State**: Never leave the codebase in a broken state between tasks
3. **Documentation First**: Understand before implementing
4. **Test Early**: Verify functionality immediately after implementation

---

### MANDATORY CHECKLIST (All items required)

Every task MUST satisfy ALL of the following before marking as `completed`:

#### ✅ Build & Execution
- [ ] **Python code runs without errors** (if applicable)
  - No syntax errors
  - No import errors
  - All dependencies installed in virtual environment
  - Type hints respected
- [ ] **Backend API accessible** (if integration required)
  - API endpoints return expected data
  - No breaking changes to existing API
- [ ] **Frontend builds successfully** (if UI changes)
  - TypeScript compilation passes
  - React components render without errors
  - No console errors

#### ✅ Code Quality
- [ ] **Python code follows PEP 8**
  - Proper indentation (4 spaces)
  - Meaningful variable/function names
  - Type hints for function parameters and returns
- [ ] **No hardcoded values** (use .env or constants)
- [ ] **Error handling implemented**
  - Try/except blocks for external calls
  - Graceful degradation
  - User-friendly error messages

#### ✅ Testing
- [ ] **Manual testing completed**
  - Agent responds to test queries
  - Tools execute successfully
  - Error scenarios handled gracefully
- [ ] **Integration testing** (if applicable)
  - Agent successfully calls backend API
  - Data flows correctly end-to-end
  - Conversation context maintained
- [ ] **Unit tests** (for later tasks)
  - Tool functions tested in isolation
  - Edge cases covered

#### ✅ Documentation
- [ ] **Code comments updated**
  - Docstrings for functions and classes
  - Inline comments for complex logic
- [ ] **README updated** (if setup changes)
  - New dependencies documented
  - Setup steps current
  - Environment variables explained
- [ ] **.env.example updated** (if new env vars)

#### ✅ Version Control
- [ ] **Changes committed** with descriptive message
  - Format: `feat(agent): description` or `fix(agent): description`
  - Atomic commits (single logical change)
- [ ] **No secrets in code**
  - .env file in .gitignore
  - No API keys, tokens, or credentials
  - No personal information

#### ✅ Plan Maintenance
- [ ] **Task status updated** in plan-agent.md
  - Status changed to `completed`
  - Actual time spent recorded (if tracked)
  - Notes section updated with learnings/issues
- [ ] **Downstream impacts assessed**
  - Review remaining tasks
  - Update dependencies/blockers
  - Adjust estimates if needed

---

## Task Overview

| ID | Task | Priority | Estimated | Dependencies | Status |
|----|------|----------|-----------|--------------|--------|
| TA-000 | Project Setup & Environment | P0 | 0.5 days | None | not-started |
| TA-001 | Azure Foundry Model Deployment | P0 | 1 day | TA-000 | not-started |
| TA-002 | Basic Agent Implementation | P0 | 1 day | TA-001 | not-started |
| TA-003 | API Integration Tools | P0 | 1 day | TA-002 | not-started |
| TA-004 | Transfer Confirmation Flow | P0 | 0.5 days | TA-003 | not-started |
| TA-005 | Analysis & Insights Tools | P1 | 1 day | TA-003 | not-started |
| TA-006 | Agent Server & HTTP Endpoint | P0 | 0.5 days | TA-004 | not-started |
| TA-007 | Debugging & Development Setup | P1 | 0.5 days | TA-006 | not-started |
| TA-008 | React Chat Widget Component | P0 | 1 day | TA-006 | not-started |
| TA-009 | Agent-UI Integration | P0 | 0.5 days | TA-008 | not-started |
| TA-010 | Testing & Error Handling | P1 | 1 day | TA-009 | not-started |
| TA-011 | Documentation & Handoff | P2 | 0.5 days | TA-010 | not-started |

**Priority Legend**: P0 = Critical, P1 = High, P2 = Medium

---

## Task Details

### TA-000: Project Setup & Environment
**Priority**: P0  
**Estimated**: 0.5 days  
**Status**: not-started

#### Objective
Set up Python development environment, install dependencies, and configure Azure authentication.

#### Scope
1. Create Python virtual environment in `src/agent/.venv`
2. Install Microsoft Agent Framework SDK
3. Install Agent Server SDK
4. Install development tools (debugpy, agent-dev-cli)
5. Configure Azure authentication (DefaultAzureCredential)
6. Create .env file with placeholder values
7. Create .env.example for documentation
8. Update .gitignore to exclude .env and .venv

#### Deliverables
- [ ] Virtual environment created: `src/agent/.venv/`
- [ ] `requirements.txt` with pinned dependencies:
  ```
  agent-framework-core==1.0.0b260107
  agent-framework-azure-ai==1.0.0b260107
  azure-ai-agentserver-core==1.0.0b10
  azure-ai-agentserver-agentframework==1.0.0b10
  azure-identity
  python-dotenv
  httpx
  debugpy
  agent-dev-cli
  ```
- [ ] `.env` file created (not committed):
  ```
  FOUNDRY_PROJECT_ENDPOINT=<your-foundry-endpoint>
  FOUNDRY_MODEL_DEPLOYMENT_NAME=<your-model-deployment>
  BACKEND_API_URL=http://localhost:5000
  AGENT_PORT=8087
  LOG_LEVEL=DEBUG
  ```
- [ ] `.env.example` file created (committed)
- [ ] `.gitignore` updated to exclude `.env` and `__pycache__`

#### Acceptance Criteria
- [ ] Python 3.10+ installed and verified
- [ ] Virtual environment activates successfully
- [ ] All dependencies install without errors
- [ ] Azure authentication configured (can acquire token)
- [ ] .env file created with placeholders

#### Notes
- Use Python 3.10 or higher (3.14 detected in workspace)
- Pin SDK versions to avoid breaking changes
- .env should NOT be committed to version control

---

### TA-001: Azure Foundry Model Deployment
**Priority**: P0  
**Estimated**: 1 day  
**Status**: not-started  
**Dependencies**: TA-000

#### Objective
Deploy a suitable LLM model in Azure Foundry for the banking agent.

#### Scope
1. Open AI Toolkit Model Catalog (Foundry filter)
2. Select appropriate model for banking assistant
3. Deploy model to Azure Foundry project
4. Obtain project endpoint and deployment name
5. Update .env with actual values
6. Test model connection with basic agent code

#### Recommended Models (in priority order)
1. **gpt-5.1**: Best balance of quality, reasoning, and cost
   - Context: 200K input / 100K output
   - Cost: $3.4375 per 1M tokens
   - Quality: 0.903 (excellent for conversations)
2. **claude-sonnet-4-5**: Alternative with strong reasoning
   - Context: 200K input / 64K output
   - Cost: $6 per 1M tokens
   - Quality: 0.921 (best for complex agents)
3. **gpt-4.1**: Budget-friendly option
   - Context: 1M input / 33K output
   - Cost: $3.5 per 1M tokens
   - Quality: 0.844 (good for most tasks)

#### Deliverables
- [ ] Azure Foundry project created (or existing project identified)
- [ ] Model deployed (gpt-5.1 or equivalent)
- [ ] `.env` updated with:
  - `FOUNDRY_PROJECT_ENDPOINT`: Actual endpoint URL
  - `FOUNDRY_MODEL_DEPLOYMENT_NAME`: Actual deployment name
- [ ] Connection test successful (basic agent run)

#### Acceptance Criteria
- [ ] Model deployed and accessible via Foundry endpoint
- [ ] Credentials configured (DefaultAzureCredential works)
- [ ] Basic agent can connect and generate response
- [ ] No quota or permission errors

#### Notes
- Use AI Toolkit VS Code extension for easy deployment
- Command: `ai-mlstudio.triggerFoundryModelDeployment`
- If no Foundry project exists, create one via Azure portal or AI Toolkit
- Consider GitHub Models as free alternative for development/testing

---

### TA-002: Basic Agent Implementation
**Priority**: P0  
**Estimated**: 1 day  
**Status**: not-started  
**Dependencies**: TA-001

#### Objective
Create the core agent using Microsoft Agent Framework with system prompt and basic conversation flow.

#### Scope
1. Create `src/agent/main.py` as entry point
2. Implement AzureAIClient initialization with Foundry credentials
3. Create agent with banking assistant system prompt
4. Implement basic chat loop (CLI mode for testing)
5. Add thread management for conversation context
6. Implement proper error handling and logging
7. Test multi-turn conversations

#### Deliverables
- [ ] `src/agent/main.py`:
  ```python
  from agent_framework.azure import AzureAIClient
  from azure.identity.aio import DefaultAzureCredential
  from dotenv import load_dotenv
  import asyncio
  import os
  
  load_dotenv(override=True)
  
  SYSTEM_PROMPT = """You are a helpful banking assistant..."""
  
  async def main():
      async with (
          DefaultAzureCredential() as credential,
          AzureAIClient(
              project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
              model_deployment_name=os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME"),
              credential=credential,
          ).create_agent(
              name="HomeBankingAgent",
              instructions=SYSTEM_PROMPT,
          ) as agent,
      ):
          thread = agent.get_new_thread()
          
          print("Banking Agent ready. Type 'exit' to quit.")
          while True:
              user_input = input("\nYou: ")
              if user_input.lower() in ['exit', 'quit']:
                  break
              
              print("Agent: ", end="", flush=True)
              async for chunk in agent.run_stream(user_input, thread=thread):
                  if chunk.text:
                      print(chunk.text, end="", flush=True)
              print()
  
  if __name__ == "__main__":
      asyncio.run(main())
  ```
- [ ] System prompt in separate file or constant (from spec-agent.md Section 6)
- [ ] Logging configured (console output)

#### Acceptance Criteria
- [ ] Agent initializes successfully
- [ ] Agent responds to basic greetings and questions
- [ ] Multi-turn conversations maintain context
- [ ] Thread management works (follow-up questions answered correctly)
- [ ] Errors logged appropriately
- [ ] CLI mode functional for testing

#### Test Scenarios
```
User: Hello
Agent: Hello! How can I help you with your banking needs today?

User: What can you help me with?
Agent: I can help you with:
       - Checking your account balances
       - Reviewing your transaction history
       - Transferring money between accounts
       - Analyzing your spending patterns
       - Providing financial insights
       What would you like to do?
```

#### Notes
- Agent name must start/end with alphanumeric (no underscores or hyphens at edges)
- Use async/await throughout (required by Agent Framework)
- load_dotenv(override=True) ensures .env works in deployed env

---

### TA-003: API Integration Tools
**Priority**: P0  
**Estimated**: 1 day  
**Status**: not-started  
**Dependencies**: TA-002

#### Objective
Implement tool functions that call the .NET backend API for accounts and transactions.

#### Scope
1. Create `src/agent/tools.py` module
2. Implement `get_account_balances()` tool
3. Implement `get_transactions()` tool with optional filtering
4. Add error handling for API failures
5. Add tools to agent configuration
6. Test tool calling with natural language queries

#### Deliverables
- [ ] `src/agent/tools.py`:
  ```python
  import httpx
  import os
  from typing import Annotated, Optional
  
  BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:5000")
  
  async def get_account_balances() -> str:
      """Get current balances for all user accounts."""
      try:
          async with httpx.AsyncClient() as client:
              response = await client.get(f"{BACKEND_URL}/api/accounts")
              response.raise_for_status()
              accounts = response.json()
              
              result = "Account Balances:\n"
              for acc in accounts:
                  result += f"- {acc['name']} (ending in {acc['accountNumber'][-4:]}): ${acc['balance']:,.2f}\n"
              return result
      except Exception as e:
          return f"Error fetching account balances: {str(e)}"
  
  async def get_transactions(
      account_id: Annotated[Optional[str], "Optional account ID to filter transactions"] = None
  ) -> str:
      """Get transaction history, optionally filtered by account."""
      try:
          async with httpx.AsyncClient() as client:
              url = f"{BACKEND_URL}/api/transactions"
              if account_id:
                  url += f"?accountId={account_id}"
              
              response = await client.get(url)
              response.raise_for_status()
              transactions = response.json()
              
              if not transactions:
                  return "No transactions found."
              
              result = f"Transaction History ({len(transactions)} transactions):\n"
              for txn in transactions[:10]:  # Limit to recent 10
                  result += f"- {txn['date']}: {txn['description']} - ${abs(txn['amount']):,.2f} ({txn['category']})\n"
              
              if len(transactions) > 10:
                  result += f"... and {len(transactions) - 10} more transactions\n"
              
              return result
      except Exception as e:
          return f"Error fetching transactions: {str(e)}"
  ```
- [ ] Update `main.py` to import and add tools:
  ```python
  from tools import get_account_balances, get_transactions
  
  # In agent creation:
  ).create_agent(
      name="HomeBankingAgent",
      instructions=SYSTEM_PROMPT,
      tools=[get_account_balances, get_transactions],
  ) as agent,
  ```

#### Acceptance Criteria
- [ ] `get_account_balances()` successfully calls API and returns formatted data
- [ ] `get_transactions()` successfully calls API with/without filtering
- [ ] API errors handled gracefully (timeouts, 404, 500, etc.)
- [ ] Agent invokes tools automatically when user asks relevant questions
- [ ] Tool responses formatted clearly for LLM understanding

#### Test Scenarios
```
User: What's my checking account balance?
Agent: [Tool: get_account_balances called]
       Your Checking account (ending in 1001) has a balance of $5,234.50.

User: Show me my recent transactions
Agent: [Tool: get_transactions called]
       Here are your recent transactions:
       - Feb 17: Coffee Shop - $4.50 (Dining)
       - Feb 16: Grocery Store - $87.23 (Groceries)
       ...
```

#### Notes
- Use httpx for async HTTP calls (required with async agent)
- Include timeout handling (default 30s)
- Format currency consistently ($X,XXX.XX)
- Mask account numbers (show last 4 digits)

---

### TA-004: Transfer Confirmation Flow
**Priority**: P0  
**Estimated**: 0.5 days  
**Status**: not-started  
**Dependencies**: TA-003

#### Objective
Implement transfer tool with mandatory user confirmation before execution.

#### Scope
1. Add `execute_transfer()` tool to tools.py
2. Implement validation logic (accounts exist, sufficient balance)
3. Add confirmation prompt to system prompt
4. Implement two-step flow: present → confirm → execute
5. Handle confirmation responses (yes/no/cancel)
6. Test transfer scenarios including rejections

#### Deliverables
- [ ] Update `src/agent/tools.py`:
  ```python
  async def execute_transfer(
      from_account_id: Annotated[str, "Source account GUID"],
      to_account_id: Annotated[str, "Destination account GUID"],
      amount: Annotated[float, "Transfer amount in dollars"],
      description: Annotated[str, "Optional transfer description"] = "Transfer via AI Agent"
  ) -> str:
      """Execute a transfer between accounts. REQUIRES USER CONFIRMATION."""
      try:
          async with httpx.AsyncClient() as client:
              payload = {
                  "fromAccountId": from_account_id,
                  "toAccountId": to_account_id,
                  "amount": amount,
                  "description": description
              }
              
              response = await client.post(
                  f"{BACKEND_URL}/api/transfers",
                  json=payload,
                  timeout=30
              )
              
              if response.status_code == 200:
                  result = response.json()
                  return f"✓ Transfer successful! Transaction IDs: {result['debitTransactionId'][:8]}... (debit), {result['creditTransactionId'][:8]}... (credit)"
              else:
                  error = response.json()
                  return f"Transfer failed: {error.get('title', 'Unknown error')}"
      except Exception as e:
          return f"Error executing transfer: {str(e)}"
  ```
- [ ] Update system prompt to emphasize confirmation:
  ```
  When handling transfers:
  1. First, present the transfer details clearly
  2. Ask for EXPLICIT confirmation ("Would you like me to proceed?")
  3. Wait for affirmative response (yes, confirm, proceed, go ahead)
  4. Only then call execute_transfer tool
  5. If user says no/cancel/stop, acknowledge and do not execute
  ```
- [ ] Add tool to agent configuration

#### Acceptance Criteria
- [ ] Transfer tool calls API successfully when confirmed
- [ ] Agent always asks for confirmation before executing
- [ ] Agent presents clear transfer summary before asking
- [ ] Confirmation flow works for yes/no responses
- [ ] Transfer errors handled gracefully
- [ ] Transaction IDs returned on success

#### Test Scenarios
```
User: Transfer $100 from checking to savings
Agent: I can help with that. Here are the details:
       From: Checking (ending in 1001) - $5,234.50
       To: Savings (ending in 1002) - $12,800.75
       Amount: $100.00
       Would you like me to proceed?

User: Yes
Agent: [Tool: execute_transfer called]
       ✓ Transfer successful! Transaction IDs: abc12345... (debit), def67890... (credit)

---

User: Transfer $200 from savings to checking
Agent: Here are the details...
       Would you like me to proceed?

User: No, cancel that
Agent: No problem! I've cancelled the transfer. Is there anything else I can help with?
```

#### Notes
- Never execute transfer without explicit user confirmation
- Handle various confirmation phrases (yes, yep, sure, go ahead, proceed, confirm)
- Handle rejection phrases (no, cancel, stop, nevermind, abort)
- Log all transfer attempts (success and failure)

---

### TA-005: Analysis & Insights Tools
**Priority**: P1  
**Estimated**: 1 day  
**Status**: not-started  
**Dependencies**: TA-003

#### Objective
Implement spending analysis and financial insights capabilities using client-side Python functions.

#### Scope
1. Create `src/agent/analysis.py` module
2. Implement spending analysis functions:
   - Sum by category
   - Calculate averages
   - Find largest/smallest transactions
   - Identify trends
3. Add analysis tools to agent configuration
4. Test insight generation

#### Deliverables
- [ ] `src/agent/analysis.py`:
  ```python
  from typing import Dict, List, Any
  from collections import defaultdict
  
  def analyze_spending_by_category(transactions: List[Dict[str, Any]]) -> str:
      """Analyze spending grouped by category."""
      category_totals = defaultdict(float)
      total_spending = 0
      
      for txn in transactions:
          amount = txn.get('amount', 0)
          if amount < 0:  # Expense
              category = txn.get('category', 'Uncategorized')
              category_totals[category] += abs(amount)
              total_spending += abs(amount)
      
      if total_spending == 0:
          return "No expenses found in transactions."
      
      # Sort by amount (descending)
      sorted_categories = sorted(
          category_totals.items(),
          key=lambda x: x[1],
          reverse=True
      )
      
      result = "Spending by Category:\n"
      for category, amount in sorted_categories:
          percentage = (amount / total_spending) * 100
          result += f"- {category}: ${amount:,.2f} ({percentage:.1f}%)\n"
      
      result += f"\nTotal Expenses: ${total_spending:,.2f}"
      return result
  
  def find_largest_transactions(transactions: List[Dict[str, Any]], count: int = 5) -> str:
      """Find the largest transactions by amount."""
      sorted_txns = sorted(
          transactions,
          key=lambda x: abs(x.get('amount', 0)),
          reverse=True
      )[:count]
      
      result = f"Top {count} Largest Transactions:\n"
      for i, txn in enumerate(sorted_txns, 1):
          result += f"{i}. {txn['date']}: {txn['description']} - ${abs(txn['amount']):,.2f}\n"
      
      return result
  ```
- [ ] Update `tools.py` to integrate analysis:
  ```python
  from analysis import analyze_spending_by_category, find_largest_transactions
  
  async def get_spending_insights() -> str:
      """Get spending insights and analysis."""
      try:
          async with httpx.AsyncClient() as client:
              response = await client.get(f"{BACKEND_URL}/api/transactions")
              response.raise_for_status()
              transactions = response.json()
              
              # Run analysis
              insights = analyze_spending_by_category(transactions)
              largest = find_largest_transactions(transactions, 3)
              
              return f"{insights}\n\n{largest}"
      except Exception as e:
          return f"Error generating insights: {str(e)}"
  ```
- [ ] Add `get_spending_insights` to agent tools

#### Acceptance Criteria
- [ ] Spending analysis correctly sums by category
- [ ] Percentages calculated accurately
- [ ] Largest transactions identified correctly
- [ ] Agent provides meaningful insights when asked
- [ ] Analysis handles empty or invalid data gracefully

#### Test Scenarios
```
User: Give me my spending insights
Agent: [Tool: get_spending_insights called]
       Based on your transaction history:
       
       Spending by Category:
       - Groceries: $487.23 (28%)
       - Utilities: $325.00 (19%)
       - Entertainment: $280.50 (16%)
       ...

User: What was my largest purchase?
Agent: Your largest transaction was $287.45 at Electronics Store on Feb 10, 2026.
```

#### Notes
- Keep analysis client-side (no new API endpoints needed)
- Consider caching transaction data to avoid repeated API calls
- Future enhancement: Time-based filtering (last month, last 7 days)

---

### TA-006: Agent Server & HTTP Endpoint
**Priority**: P0  
**Estimated**: 0.5 days  
**Status**: not-started  
**Dependencies**: TA-004

#### Objective
Convert CLI agent to HTTP server mode for web app integration.

#### Scope
1. Refactor main.py to support both CLI and server modes
2. Integrate azure-ai-agentserver-agentframework for HTTP serving
3. Configure server port and CORS
4. Test HTTP endpoint with curl/Postman
5. Implement request/response format for web app

#### Deliverables
- [ ] Update `src/agent/main.py`:
  ```python
  import argparse
  from azure.ai.agentserver.agentframework import from_agent_framework
  
  async def create_agent():
      """Create and return the agent workflow."""
      credential = DefaultAzureCredential()
      client = AzureAIClient(
          project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
          model_deployment_name=os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME"),
          credential=credential,
      )
      
      agent = await client.create_agent(
          name="HomeBankingAgent",
          instructions=SYSTEM_PROMPT,
          tools=[get_account_balances, get_transactions, execute_transfer, get_spending_insights],
      )
      
      # Convert to agent for server use
      return agent.as_agent() if hasattr(agent, 'as_agent') else agent
  
  async def main():
      parser = argparse.ArgumentParser()
      parser.add_argument('--server', action='store_true', help='Run in server mode')
      parser.add_argument('--port', type=int, default=8087, help='Server port')
      args = parser.parse_args()
      
      if args.server:
          # Server mode
          agent = await create_agent()
          await from_agent_framework(agent).run_async(port=args.port)
      else:
          # CLI mode (existing implementation)
          # ... existing CLI code ...
  
  if __name__ == "__main__":
      asyncio.run(main())
  ```
- [ ] Test server startup:
  ```bash
  python main.py --server --port 8087
  ```
- [ ] Test HTTP endpoint:
  ```bash
  curl -X POST http://localhost:8087/agent/run \
    -H "Content-Type: application/json" \
    -d '{"messages": [{"role": "user", "content": "What is my checking balance?"}]}'
  ```

#### Acceptance Criteria
- [ ] Server mode starts without errors
- [ ] HTTP endpoint responds to POST requests
- [ ] Agent processes messages via HTTP
- [ ] Responses include agent messages
- [ ] Server logs requests and responses
- [ ] CLI mode still functional (for debugging)

#### Notes
- Default to server mode for production
- Keep CLI mode for local testing and debugging
- Pin azure-ai-agentserver packages to avoid breaking changes
- Consider adding health check endpoint

---

### TA-007: Debugging & Development Setup
**Priority**: P1  
**Estimated**: 0.5 days  
**Status**: not-started  
**Dependencies**: TA-006

#### Objective
Configure VS Code debugging with AI Toolkit Agent Inspector integration.

#### Scope
1. Create .vscode/tasks.json for agent server startup
2. Create .vscode/launch.json for debugger attachment
3. Install agent-dev-cli for Agent Inspector integration
4. Test F5 debugging experience
5. Verify Agent Inspector opens and works

#### Deliverables
- [ ] `.vscode/tasks.json`:
  ```json
  {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "Validate prerequisites",
        "type": "aitk",
        "command": "debug-check-prerequisites",
        "args": {
          "portOccupancy": [5679, 8087]
        }
      },
      {
        "label": "Run Agent HTTP Server",
        "type": "shell",
        "command": "${command:python.interpreterPath} -m debugpy --listen 127.0.0.1:5679 -m agentdev run main.py --verbose --port 8087 -- --server",
        "isBackground": true,
        "options": {
          "cwd": "${workspaceFolder}/src/agent"
        },
        "dependsOn": ["Validate prerequisites"],
        "problemMatcher": {
          "pattern": [{
            "regexp": "^.*$",
            "file": 0,
            "location": 1,
            "message": 2
          }],
          "background": {
            "activeOnStart": true,
            "beginsPattern": ".*",
            "endsPattern": "Application startup complete|running on|Started server process"
          }
        }
      },
      {
        "label": "Open Agent Inspector",
        "type": "shell",
        "command": "echo '${input:openAgentInspector}'",
        "presentation": {
          "reveal": "never"
        },
        "dependsOn": ["Run Agent HTTP Server"]
      },
      {
        "label": "Terminate All Tasks",
        "command": "echo ${input:terminate}",
        "type": "shell",
        "problemMatcher": []
      }
    ],
    "inputs": [
      {
        "id": "openAgentInspector",
        "type": "command",
        "command": "ai-mlstudio.openTestTool",
        "args": {"triggeredFrom": "tasks", "port": 8087}
      },
      {
        "id": "terminate",
        "type": "command",
        "command": "workbench.action.tasks.terminate",
        "args": "terminateAll"
      }
    ]
  }
  ```
- [ ] `.vscode/launch.json`:
  ```json
  {
    "version": "0.2.0",
    "configurations": [
      {
        "name": "Debug Agent HTTP Server",
        "type": "debugpy",
        "request": "attach",
        "connect": {
          "host": "localhost",
          "port": 5679
        },
        "preLaunchTask": "Open Agent Inspector",
        "internalConsoleOptions": "neverOpen",
        "postDebugTask": "Terminate All Tasks"
      }
    ]
  }
  ```
- [ ] Install agent-dev-cli:
  ```bash
  pip install agent-dev-cli --pre
  ```

#### Acceptance Criteria
- [ ] F5 starts agent server with debugging enabled
- [ ] Breakpoints work in agent code
- [ ] Agent Inspector opens automatically
- [ ] Can test agent via Inspector UI
- [ ] Stopping debugger terminates server cleanly

#### Test Scenarios
1. Press F5 in VS Code
2. Agent Inspector should open in browser/panel
3. Send test message "What's my balance?"
4. Verify agent responds
5. Check debug console for logs
6. Set breakpoint in tool function
7. Trigger tool call, verify breakpoint hits

#### Notes
- Requires AI Toolkit VS Code extension installed
- Ports 5679 (debugpy) and 8087 (agent server) must be free
- Agent Inspector provides better UX than curl for testing

---

### TA-008: React Chat Widget Component
**Priority**: P0  
**Estimated**: 1 day  
**Status**: not-started  
**Dependencies**: TA-006

#### Objective
Create a reusable React chat widget component with proper UI/UX.

#### Scope
1. Create chat widget component using shadcn/ui
2. Implement message list with user/agent messages
3. Add input field and send button
4. Handle loading states (typing indicators)
5. Style with Tailwind CSS (dark theme)
6. Make component responsive

#### Deliverables
- [ ] `src/web/src/components/ChatWidget.tsx`:
  ```typescript
  import React, { useState, useRef, useEffect } from 'react';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { Button } from '@/components/ui/button';
  import { Input } from '@/components/ui/input';
  import { ScrollArea } from '@/components/ui/scroll-area';
  
  interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
  }
  
  interface ChatWidgetProps {
    onSendMessage: (message: string) => Promise<string>;
  }
  
  export function ChatWidget({ onSendMessage }: ChatWidgetProps) {
    const [messages, setMessages] = useState<Message[]>([
      {
        role: 'assistant',
        content: 'Hello! I\'m your banking assistant. How can I help you today?',
        timestamp: new Date()
      }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
  
    const handleSend = async () => {
      if (!input.trim() || isLoading) return;
  
      const userMessage: Message = {
        role: 'user',
        content: input,
        timestamp: new Date()
      };
  
      setMessages(prev => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);
  
      try {
        const response = await onSendMessage(input);
        const assistantMessage: Message = {
          role: 'assistant',
          content: response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } catch (error) {
        const errorMessage: Message = {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    };
  
    useEffect(() => {
      scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);
  
    return (
      <Card className="w-full h-[600px] flex flex-col">
        <CardHeader>
          <CardTitle>💬 Banking Assistant</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col p-4 gap-4">
          <ScrollArea className="flex-1 pr-4">
            <div className="space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-100'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {msg.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-700 rounded-lg p-3">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={scrollRef} />
            </div>
          </ScrollArea>
  
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Ask about your accounts, transfers, or spending..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
              Send
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }
  ```
- [ ] Export from `src/web/src/components/index.ts`

#### Acceptance Criteria
- [ ] Chat widget renders correctly
- [ ] Messages display in chronological order
- [ ] User messages aligned right (blue)
- [ ] Agent messages aligned left (gray)
- [ ] Loading indicator shows during agent response
- [ ] Auto-scrolls to latest message
- [ ] Enter key sends message
- [ ] Input clears after sending
- [ ] Responsive design (mobile + desktop)

#### Notes
- Uses shadcn/ui components (already in project)
- Dark theme matches existing app
- Timestamps for message tracking
- Accessible (keyboard navigation supported)

---

### TA-009: Agent-UI Integration
**Priority**: P0  
**Estimated**: 0.5 days  
**Status**: not-started  
**Dependencies**: TA-008

#### Objective
Integrate chat widget with agent HTTP endpoint and add to main dashboard.

#### Scope
1. Create agent service client in web app
2. Implement sendMessage function with thread management
3. Add ChatWidget to dashboard page
4. Handle errors and edge cases
5. Test end-to-end flow

#### Deliverables
- [ ] `src/web/src/services/agentService.ts`:
  ```typescript
  const AGENT_URL = import.meta.env.VITE_AGENT_URL || 'http://localhost:8087';
  
  interface AgentMessage {
    role: 'user' | 'assistant';
    content: string;
  }
  
  interface AgentResponse {
    messages: AgentMessage[];
    threadId?: string;
  }
  
  let currentThreadId: string | null = null;
  
  export async function sendMessageToAgent(userMessage: string): Promise<string> {
    try {
      const response = await fetch(`${AGENT_URL}/agent/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: userMessage }],
          threadId: currentThreadId,
        }),
      });
  
      if (!response.ok) {
        throw new Error(`Agent request failed: ${response.statusText}`);
      }
  
      const data: AgentResponse = await response.json();
      
      // Update thread ID for conversation continuity
      if (data.threadId) {
        currentThreadId = data.threadId;
      }
  
      // Extract assistant's response
      const assistantMessage = data.messages.find(m => m.role === 'assistant');
      return assistantMessage?.content || 'Sorry, I did not understand that.';
    } catch (error) {
      console.error('Agent service error:', error);
      throw new Error('Failed to communicate with banking assistant. Please try again.');
    }
  }
  
  export function resetThread() {
    currentThreadId = null;
  }
  ```
- [ ] Update `src/web/src/App.tsx` to add ChatWidget:
  ```typescript
  import { ChatWidget } from '@/components/ChatWidget';
  import { sendMessageToAgent } from '@/services/agentService';
  
  // In the main dashboard layout, add a new section:
  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div className="lg:col-span-2">
      {/* Existing dashboard content */}
    </div>
    <div className="lg:col-span-1">
      <ChatWidget onSendMessage={sendMessageToAgent} />
    </div>
  </div>
  ```
- [ ] Add environment variable to `.env` (and `.env.example`):
  ```
  VITE_AGENT_URL=http://localhost:8087
  ```

#### Acceptance Criteria
- [ ] Chat widget appears on dashboard
- [ ] Sending message calls agent service
- [ ] Agent responses appear in chat
- [ ] Thread continuity maintained across messages
- [ ] Errors handled gracefully (network failures, timeouts)
- [ ] No CORS issues (agent server configured correctly)
- [ ] Loading states work (typing indicator during agent processing)

#### Test Scenarios
```
1. Open dashboard
2. Chat widget visible on right side
3. Type "What's my checking balance?"
4. Press Enter
5. See loading indicator
6. Agent response appears with balance
7. Ask follow-up: "And my savings?"
8. Agent responds with savings balance (context maintained)
```

#### Notes
- May need to configure CORS on agent server
- Thread ID persists across messages (session continuity)
- Future: Persist thread ID to localStorage for page refreshes

---

### TA-010: Testing & Error Handling
**Priority**: P1  
**Estimated**: 1 day  
**Status**: not-started  
**Dependencies**: TA-009

#### Objective
Comprehensive testing of agent functionality and robust error handling.

#### Scope
1. Unit tests for tool functions (pytest)
2. Integration tests (agent + API)
3. End-to-end UI tests (optional, if time permits)
4. Error scenario testing
5. Performance testing (response times)
6. Document known issues and limitations

#### Deliverables
- [ ] `src/agent/tests/test_tools.py`:
  ```python
  import pytest
  from unittest.mock import AsyncMock, patch
  from tools import get_account_balances, get_transactions, execute_transfer
  
  @pytest.mark.asyncio
  async def test_get_account_balances_success():
      mock_response = AsyncMock()
      mock_response.json.return_value = [
          {"name": "Checking", "accountNumber": "001", "balance": 1000.00},
          {"name": "Savings", "accountNumber": "002", "balance": 5000.00}
      ]
      mock_response.raise_for_status = AsyncMock()
      
      with patch('httpx.AsyncClient') as mock_client:
          mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
          result = await get_account_balances()
          
          assert "Checking" in result
          assert "1,000.00" in result
          assert "Savings" in result
  
  @pytest.mark.asyncio
  async def test_execute_transfer_validation():
      # Test insufficient balance scenario
      # ... test implementation ...
      pass
  ```
- [ ] `src/agent/tests/test_integration.py`:
  ```python
  @pytest.mark.asyncio
  async def test_agent_account_balance_query():
      """Test agent responds correctly to balance queries."""
      # Implementation depends on agent testing approach
      pass
  ```
- [ ] Error handling improvements in all modules
- [ ] Performance benchmarks documented

#### Test Cases
1. **Tool Testing**:
   - [ ] Account balances retrieval (success)
   - [ ] Account balances retrieval (API error)
   - [ ] Transactions retrieval (with/without filter)
   - [ ] Transfer execution (success)
   - [ ] Transfer execution (insufficient balance)
   - [ ] Transfer execution (invalid account)

2. **Agent Integration**:
   - [ ] Simple query response
   - [ ] Multi-turn conversation
   - [ ] Tool invocation
   - [ ] Transfer with confirmation
   - [ ] Transfer cancellation
   - [ ] Error recovery

3. **UI Integration**:
   - [ ] Send message
   - [ ] Receive response
   - [ ] Loading states
   - [ ] Error messages
   - [ ] Thread continuity

4. **Error Scenarios**:
   - [ ] API unavailable (backend down)
   - [ ] Agent service unavailable
   - [ ] Network timeout
   - [ ] Invalid user input
   - [ ] LLM error/rate limit

5. **Performance**:
   - [ ] Simple query response time < 3s
   - [ ] Complex query response time < 5s
   - [ ] Tool execution time < 500ms

#### Acceptance Criteria
- [ ] All unit tests passing
- [ ] Critical paths covered by integration tests
- [ ] Error scenarios tested and handled
- [ ] Performance targets met
- [ ] Test documentation complete

#### Notes
- Use pytest for Python testing
- Mock external dependencies (API, LLM)
- Test both happy paths and error cases
- Document any flaky tests or known issues

---

### TA-011: Documentation & Handoff
**Priority**: P2  
**Estimated**: 0.5 days  
**Status**: not-started  
**Dependencies**: TA-010

#### Objective
Create comprehensive documentation for using, debugging, and deploying the agent.

#### Scope
1. Create README.md for src/agent/
2. Update main README.md with agent section
3. Document environment setup
4. Document debugging workflow
5. Document deployment process (future)
6. Create troubleshooting guide

#### Deliverables
- [ ] `src/agent/README.md`:
  ```markdown
  # Home Banking AI Agent
  
  An intelligent conversational AI agent built with Microsoft Agent Framework.
  
  ## Features
  - Account balance queries
  - Transaction history and analysis
  - Guided money transfers with confirmation
  - Financial insights and spending patterns
  
  ## Setup
  
  ### Prerequisites
  - Python 3.10+
  - Azure account (for Foundry)
  - .NET API running on localhost:5000
  
  ### Installation
  1. Create virtual environment:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate  # Windows
     ```
  
  2. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
  
  3. Configure environment:
     ```bash
     cp .env.example .env
     # Edit .env with your Foundry credentials
     ```
  
  ### Running
  
  **Server mode** (for web app integration):
  ```bash
  python main.py --server --port 8087
  ```
  
  **CLI mode** (for testing):
  ```bash
  python main.py
  ```
  
  **Debug mode** (VS Code):
  - Press F5
  - Agent Inspector opens automatically
  
  ## Testing
  
  Run unit tests:
  ```bash
  pytest tests/
  ```
  
  ## Architecture
  
  - `main.py`: Entry point and agent initialization
  - `tools.py`: API integration tools
  - `analysis.py`: Spending analysis functions
  - `tests/`: Unit and integration tests
  
  ## Troubleshooting
  
  **Agent won't start**:
  - Check .env file has correct Foundry credentials
  - Verify Python 3.10+ installed
  - Check all dependencies installed
  
  **Tools not working**:
  - Ensure backend API is running (localhost:5000)
  - Check BACKEND_API_URL in .env
  - Verify network connectivity
  
  **LLM errors**:
  - Check Azure Foundry quota
  - Verify model deployment name
  - Check Azure authentication (az login)
  
  ## Deployment
  
  See main README.md for deployment instructions.
  ```
- [ ] Update `README.md` (main project):
  - Add "AI Agent" section
  - Document agent setup and usage
  - Link to spec-agent.md and plan-agent.md
  - Add agent to architecture diagram
- [ ] Create `TROUBLESHOOTING.md` for common issues

#### Acceptance Criteria
- [ ] Documentation clear and comprehensive
- [ ] Setup instructions tested on fresh environment
- [ ] All commands work as documented
- [ ] Troubleshooting guide covers common issues
- [ ] Code examples accurate

#### Notes
- Documentation should be beginner-friendly
- Include screenshots/GIFs if helpful
- Keep examples up-to-date with code
- Document any known limitations

---

## Plan Changes & Notes

### TA-000: Project Setup & Environment
**Status**: not-started  
**Notes**: 
- Existing .venv detected in workspace
- Python 3.14 available (confirmed in terminal history)
- May reuse existing virtual environment if compatible

### TA-001: Azure Foundry Model Deployment
**Status**: not-started  
**Notes**:
- No Foundry project currently configured (aitk-list_foundry_models returned empty)
- Will need to create Foundry project OR use GitHub Models as alternative
- Recommended: gpt-5.1 for best balance of cost/quality

### TA-002 - TA-011
**Status**: not-started  
**Dependencies**: Sequential from previous tasks

---

## Success Criteria

The agent implementation is considered complete when:

- [ ] Agent service runs successfully in server mode
- [ ] All tools (accounts, transactions, transfers, insights) functional
- [ ] Chat widget integrated in web app
- [ ] End-to-end flow tested (user question → agent response)
- [ ] Transfer confirmation flow works correctly
- [ ] Documentation complete and accurate
- [ ] Debugging setup functional (F5 + Agent Inspector)
- [ ] Known issues documented

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Azure Foundry setup delays | Medium | High | Use GitHub Models as temporary alternative |
| API integration issues | Low | Medium | Test tools incrementally, mock if needed |
| LLM hallucinations | Medium | Medium | Tool-based design, strict system prompt |
| Performance issues | Low | Medium | Streaming responses, caching, token limits |
| CORS problems | Medium | Low | Configure agent server CORS headers |
| Thread management complexity | Low | Low | Start with in-memory, document for future DB |

---

## Future Enhancements (Out of Scope)

- **Authentication**: User-specific agents (requires auth system)
- **Persistent Threads**: Store conversations in database
- **Streaming Responses**: SSE for real-time typing effect
- **Multi-modal**: Receipt upload and OCR
- **Proactive Insights**: Background analysis and notifications
- **Voice Interface**: Speech-to-text integration
- **Advanced Analytics**: Predictive modeling, anomaly detection
- **Production Deployment**: Azure Container Apps, CI/CD pipeline

---

## References

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure Foundry](https://learn.microsoft.com/azure/ai-foundry/)
- [AI Toolkit Extension](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio)
- [Agent Framework Python Docs](https://pypi.org/project/agent-framework-core/)
- [spec-agent.md](./spec-agent.md) - Technical specification

---

**Document Status**: Ready for Implementation  
**Next Steps**: Begin with TA-000 (Project Setup & Environment)
