# Home Banking AI Agent - Technical Specification

**Version**: 1.0  
**Last Updated**: February 18, 2026  
**Status**: Draft

---

## 1. Overview

An intelligent conversational AI agent for the Home Banking application, built using Microsoft Agent Framework with Azure Foundry Agent Service. The agent provides a natural language interface for account inquiries, transaction analysis, financial insights, and guided transfer operations with user confirmation.

---

## 2. Functional Requirements

### 2.1 Core Capabilities

#### FR-A001: Account Information Assistant
- **Description**: Answer natural language questions about user accounts
- **Details**:
  - Retrieve and present account balances
  - Explain account types (checking, savings)
  - Show account numbers (masked appropriately)
  - Compare balances across accounts
  - Track balance changes over time

#### FR-A002: Transaction Analysis
- **Description**: Provide insights into transaction history and spending patterns
- **Details**:
  - Search transactions by date, amount, category, or description
  - Summarize transactions by category or time period
  - Identify largest/smallest transactions
  - Calculate average spending per category
  - Track income vs. expenses
  - Generate spending trends and patterns

#### FR-A003: Transfer Assistant (Suggestion Mode)
- **Description**: Guide users through transfer operations with explicit confirmation
- **Details**:
  - Accept transfer intent via natural language ("Transfer $100 from checking to savings")
  - Validate transfer parameters (accounts exist, sufficient balance)
  - Present transfer details for user confirmation
  - Execute transfer ONLY after explicit user approval
  - Provide confirmation with transaction IDs
  - Handle transfer errors gracefully

#### FR-A004: Financial Insights & Advice
- **Description**: Provide spending insights, budgeting advice, and categorization suggestions
- **Details**:
  - Identify unusual spending patterns
  - Suggest budget allocations based on historical spending
  - Recommend savings opportunities
  - Explain transaction categories
  - Provide general financial literacy guidance (not personalized financial advice)

#### FR-A005: Conversational Context Management
- **Description**: Maintain conversation context across multiple turns
- **Details**:
  - Remember previous questions and answers within a session
  - Support follow-up questions ("What about last month?")
  - Reference previous entities (accounts, transactions, amounts)
  - Clear context on session end or user request

### 2.2 Agent Tools & Capabilities

#### Tool T-001: Get Account Balances
**Purpose**: Retrieve current balances for all user accounts  
**Integration**: `GET /api/accounts`  
**Returns**: List of accounts with ID, name, type, balance  

#### Tool T-002: Get Transaction History
**Purpose**: Retrieve transaction history with optional filtering  
**Integration**: `GET /api/transactions?accountId={id}`  
**Parameters**:
- `accountId` (optional): Filter by specific account
- Date range (future enhancement)
- Category filter (future enhancement)  
**Returns**: List of transactions with date, amount, category, description, balance after

#### Tool T-003: Execute Transfer (with Confirmation)
**Purpose**: Create a transfer between accounts after user confirmation  
**Integration**: `POST /api/transfers`  
**Parameters**:
- `fromAccountId`: Source account GUID
- `toAccountId`: Destination account GUID
- `amount`: Transfer amount (decimal)
- `description`: Optional transfer description  
**Returns**: Transfer confirmation with transaction IDs  
**Safety**: Requires explicit user confirmation before execution

#### Tool T-004: Analyze Spending Patterns
**Purpose**: Calculate spending statistics and patterns  
**Implementation**: Python function (client-side analysis of transaction data)  
**Capabilities**:
- Sum by category
- Calculate averages
- Identify trends
- Find outliers

---

## 3. Technical Architecture

### 3.1 System Components

```
┌─────────────────┐
│   React Web App │
│  (src/web)      │
│  ┌───────────┐  │
│  │ Chat      │  │
│  │ Widget    │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │ HTTP (Chat Messages)
         ▼
┌─────────────────┐
│  AI Agent       │
│  Service        │
│  (src/agent)    │
│                 │
│  ┌───────────┐  │
│  │ Agent     │  │──────┐
│  │ Framework │  │      │
│  └───────────┘  │      │
│                 │      │ Foundry
│  ┌───────────┐  │      │ LLM
│  │ Tools     │  │      │
│  │ - Accounts│  │      │
│  │ - Transfer│  │      │
│  │ - Analysis│  │      │
│  └─────┬─────┘  │      │
└────────┼────────┘      │
         │               │
         │ HTTP API      │
         ▼               ▼
┌─────────────────────────┐
│  .NET API Backend       │
│  (src/api)              │
│                         │
│  ┌──────────────────┐   │
│  │ Controllers      │   │
│  │ - Accounts       │   │
│  │ - Transactions   │   │
│  │ - Transfers      │   │
│  └────────┬─────────┘   │
│           ▼             │
│  ┌──────────────────┐   │
│  │ DbContext        │   │
│  └──────────────────┘   │
└─────────────────────────┘
```

### 3.2 Technology Stack

#### Agent Service (Python)
- **Framework**: Microsoft Agent Framework (agent-framework-azure-ai==1.0.0b260107)
- **Server**: Azure AI Agent Server (azure-ai-agentserver-agentframework==1.0.0b10)
- **Runtime**: Python 3.10+
- **Environment**: Virtual environment (.venv)
- **Dependencies**:
  - `agent-framework-core==1.0.0b260107`
  - `agent-framework-azure-ai==1.0.0b260107`
  - `azure-ai-agentserver-core==1.0.0b10`
  - `azure-ai-agentserver-agentframework==1.0.0b10`
  - `azure-identity`
  - `python-dotenv`
  - `httpx` or `requests` (for API calls)

#### AI Model (Azure Foundry)
- **Primary Recommendation**: `gpt-5.1` or `claude-sonnet-4-5`
  - Excellent for conversational AI with tool calling
  - Strong reasoning for financial analysis
  - Context-aware across multiple turns
- **Budget Alternative**: `gpt-4.1` or `gpt-4.1-mini`
  - Cost-effective for production
  - Good instruction following
- **Deployment**: Via Azure Foundry Agent Service
- **Authentication**: DefaultAzureCredential (Azure AD)

#### Web UI Integration (React/TypeScript)
- **Component**: Embedded chat widget
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: React hooks (useState, useEffect)
- **API Client**: Fetch API or axios
- **Real-time**: HTTP streaming for chunk-based responses (optional)

### 3.3 Integration Points

#### 3.3.1 Agent ↔ Backend API
- **Protocol**: HTTP/HTTPS
- **Base URL**: `http://localhost:5000` (dev), configurable via .env
- **Authentication**: None (same-origin, future: JWT tokens)
- **Headers**: `Content-Type: application/json`

#### 3.3.2 Web App ↔ Agent Service
- **Protocol**: HTTP/HTTPS
- **Endpoint**: `http://localhost:8087/agent/run` (dev)
- **Request Format**: 
  ```json
  {
    "messages": [
      {"role": "user", "content": "What's my checking account balance?"}
    ],
    "threadId": "optional-session-id"
  }
  ```
- **Response Format**: 
  ```json
  {
    "messages": [
      {"role": "assistant", "content": "Your checking account balance is $5,234.50"}
    ],
    "threadId": "session-id"
  }
  ```
- **Streaming**: Optional SSE (Server-Sent Events) for progressive responses

---

## 4. Non-Functional Requirements

### 4.1 Performance

#### NFR-A001: Agent Response Time
- **Target**: 95th percentile < 3s for simple queries (account balance)
- **Target**: 95th percentile < 5s for complex queries (transaction analysis)
- **LLM Latency**: First token within 1s (streaming)
- **API Calls**: Tool calls complete within 200ms each

#### NFR-A002: Concurrent Sessions
- **Target**: Support 10 concurrent chat sessions (demo scenario)
- **Thread Management**: In-memory thread storage for development
- **Future**: Persistent thread storage (Redis, CosmosDB)

#### NFR-A003: Context Window
- **Maximum**: 10 message pairs (20 total messages) per thread
- **Token Budget**: ~4,000 tokens per request (incl. system prompt + tools)
- **Context Trimming**: Sliding window strategy for long conversations

### 4.2 Security & Privacy

#### NFR-A004: API Security
- **Validation**: All agent-to-API calls validated by backend
- **Error Handling**: Never expose internal errors or stack traces to user
- **Injection Prevention**: Sanitize all inputs before API calls
- **GUID Validation**: Validate account IDs format before API calls

#### NFR-A005: User Confirmation for Sensitive Operations
- **Transfers**: ALWAYS require explicit user confirmation
- **Confirmation Flow**:
  1. Agent presents transfer details
  2. User explicitly approves ("yes", "confirm", "proceed")
  3. Agent executes transfer
  4. Agent confirms completion
- **Rejection Handling**: Gracefully cancel on "no", "cancel", "stop"

#### NFR-A006: Data Privacy
- **No PII Storage**: Agent does not persist user data beyond session
- **Thread Isolation**: Each session isolated (no cross-user data leakage)
- **Logging**: Sanitize logs (no account numbers, amounts in plain text)

### 4.3 Reliability

#### NFR-A007: Error Handling
- **API Failures**: Gracefully handle API timeouts and errors
- **LLM Failures**: Retry transient errors, fallback to error message
- **Tool Failures**: Explain failure to user, suggest alternatives
- **Validation Errors**: Provide clear error messages and guidance

#### NFR-A008: Model Fallback
- **Primary Model Unavailable**: Fallback to secondary model (gpt-4.1-mini)
- **Configuration**: Secondary model configured in .env
- **Transparent**: User not aware of model switch

### 4.4 Observability

#### NFR-A009: Logging & Tracing
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Traced Events**:
  - User message received
  - Tool call initiated
  - Tool call completed
  - LLM request/response
  - Errors and exceptions
- **Format**: Structured JSON logs
- **Destination**: Console (dev), Azure Application Insights (prod)

#### NFR-A010: Debugging Support
- **Local Debugging**: VS Code launch configuration
- **Agent Inspector**: AI Toolkit Agent Inspector integration
- **Breakpoints**: Support for Python debugger (debugpy)

---

## 5. User Experience

### 5.1 Conversation Examples

#### Example 1: Account Balance Inquiry
```
User: What's my checking account balance?
Agent: Your Checking account (ending in 1001) has a balance of $5,234.50.

User: And my savings?
Agent: Your Savings account (ending in 1002) has a balance of $12,800.75.
```

#### Example 2: Transaction Analysis
```
User: How much did I spend on groceries last month?
Agent: In January 2026, you spent $487.23 on groceries across 12 transactions. 
       The average grocery purchase was $40.60.

User: What was my largest grocery purchase?
Agent: Your largest grocery purchase was $89.45 at Whole Foods on January 15, 2026.
```

#### Example 3: Transfer with Confirmation
```
User: Transfer $500 from checking to savings
Agent: I can help you with that transfer. Here are the details:
       
       From: Checking (ending in 1001) - Current balance: $5,234.50
       To: Savings (ending in 1002) - Current balance: $12,800.75
       Amount: $500.00
       
       After this transfer:
       - Checking balance will be $4,734.50
       - Savings balance will be $13,300.75
       
       Would you like me to proceed with this transfer?

User: Yes, go ahead
Agent: ✓ Transfer complete! 
       
       Your $500.00 transfer from Checking to Savings was successful.
       Transaction IDs: #abc123 (debit), #def456 (credit)
       
       Updated balances:
       - Checking: $4,734.50
       - Savings: $13,300.75
```

#### Example 4: Financial Insights
```
User: What are my spending trends?
Agent: Based on your transaction history, here's what I found:
       
       Top spending categories:
       1. Groceries: $487.23 (28%)
       2. Utilities: $325.00 (19%)
       3. Entertainment: $280.50 (16%)
       4. Transport: $245.00 (14%)
       5. Shopping: $210.00 (12%)
       
       Your total expenses were $1,732.73, while your income was $3,500.00,
       giving you a savings rate of 50.5% - excellent work! 💰
```

### 5.2 Error Handling Examples

#### Example 5: Insufficient Balance
```
User: Transfer $10,000 from checking to savings
Agent: I'm unable to complete this transfer. Your Checking account has a balance 
       of $5,234.50, which is not sufficient for a $10,000 transfer.
       
       Would you like to transfer a smaller amount?
```

#### Example 6: Invalid Account
```
User: Transfer $100 from my credit card to savings
Agent: I couldn't find a credit card account in your profile. You currently have:
       - Checking (ending in 1001)
       - Savings (ending in 1002)
       
       Would you like to transfer from one of these accounts?
```

---

## 6. Agent System Prompt

```
You are a helpful banking assistant for a home banking application. You help users 
manage their accounts, understand their transactions, and make informed financial decisions.

Your capabilities:
- Answer questions about account balances and transaction history
- Analyze spending patterns and provide financial insights
- Guide users through money transfers between their accounts
- Provide general financial literacy guidance

Important guidelines:
1. ALWAYS require explicit user confirmation before executing transfers
2. Present transfer details clearly before asking for confirmation
3. Use clear, conversational language - avoid banking jargon
4. Format currency as USD with 2 decimal places (e.g., $1,234.56)
5. Mask account numbers (show last 4 digits only)
6. If you're unsure, ask clarifying questions
7. If an operation fails, explain why and suggest alternatives
8. Never fabricate data - only use information from the tools
9. Keep responses concise but informative
10. Be friendly and helpful, but professional

When analyzing transactions or spending:
- Provide context and insights, not just raw numbers
- Use percentages and comparisons to make data meaningful
- Highlight unusual patterns or opportunities

When handling transfers:
1. Validate inputs (accounts exist, sufficient balance)
2. Present clear transfer summary
3. Ask for explicit confirmation
4. Execute only after "yes", "confirm", "proceed", or similar affirmative response
5. Provide confirmation with transaction details

Remember: You are an assistant, not a licensed financial advisor. Provide general 
guidance and insights, but do not give personalized investment or financial advice.
```

---

## 7. Development & Testing

### 7.1 Development Environment

#### Local Setup
- **Agent Service**: `http://localhost:8087`
- **Backend API**: `http://localhost:5000`
- **Web App**: `http://localhost:5173`
- **Agent Inspector**: AI Toolkit integration via VS Code

#### Environment Variables (.env)
```bash
# Azure Foundry Configuration
FOUNDRY_PROJECT_ENDPOINT=https://your-project.eastus.api.azureml.ms
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-5-1-deployment

# Backend API Configuration
BACKEND_API_URL=http://localhost:5000

# Agent Server Configuration
AGENT_PORT=8087

# Logging
LOG_LEVEL=DEBUG
```

### 7.2 Testing Strategy

#### Unit Tests (pytest)
- **Tool Functions**: Test each tool in isolation
- **Analysis Functions**: Test spending calculations
- **Validation Logic**: Test input validation
- **Coverage Target**: 80%+

#### Integration Tests
- **Agent + API**: Test tool calls against live API
- **End-to-End Flows**: Test complete conversation scenarios
- **Error Scenarios**: Test API failures, timeouts, validation errors

#### User Acceptance Testing
- **Conversation Quality**: Test natural language understanding
- **Confirmation Flow**: Verify transfer confirmation works correctly
- **Error Handling**: Test user experience for common errors
- **Multi-turn Conversations**: Test context retention

---

## 8. Deployment Considerations

### 8.1 Production Deployment (Future)

#### Azure Foundry Agent Service
- **Runtime**: Azure Container Apps or Azure App Service
- **Scaling**: Auto-scale based on request volume
- **Monitoring**: Azure Application Insights integration
- **Authentication**: Azure AD for Foundry, JWT for API

#### Configuration Management
- **Secrets**: Azure Key Vault for credentials
- **Feature Flags**: Azure App Configuration
- **Environment-specific**: Separate configs for dev/staging/prod

### 8.2 Cost Estimation

#### LLM Costs (Azure Foundry)
- **Model**: gpt-5.1 ($3.44/1M tokens)
- **Average Request**: ~2,000 tokens (input + output)
- **Cost per Request**: ~$0.007
- **Monthly (1,000 users, 10 queries/user)**: ~$70

#### Infrastructure Costs
- **Agent Service**: ~$30/month (Basic App Service)
- **API Service**: Existing infrastructure
- **Storage**: Minimal (thread storage)
- **Total Estimated**: ~$100/month (small scale)

---

## 9. Open Questions & Future Enhancements

### 9.1 Open Questions
1. **Authentication**: Should agent service require user authentication?
2. **Session Storage**: In-memory vs. persistent thread storage?
3. **Multi-user**: How to handle multiple user contexts?
4. **Rate Limiting**: Should we implement rate limits per user?

### 9.2 Future Enhancements
- **Multi-modal**: Support for uploading transaction receipts
- **Scheduled Reports**: "Email me my monthly spending report"
- **Proactive Insights**: "You're spending more on dining out this month"
- **Budget Management**: Set and track budgets by category
- **Bill Reminders**: "Your utility bill is due in 3 days"
- **Voice Interface**: Voice-to-text for hands-free banking
- **Multi-language**: Support for Spanish, French, etc.
- **Advanced Analytics**: Predictive spending forecasts

---

## 10. Success Metrics

### 10.1 Technical Metrics
- **Response Time**: P95 < 5s
- **Error Rate**: < 5% of requests
- **API Success Rate**: > 95%
- **Uptime**: > 99% (during business hours)

### 10.2 User Experience Metrics
- **Task Completion Rate**: > 80% (users complete intended action)
- **Conversation Length**: Average 3-5 turns per task
- **User Satisfaction**: > 4/5 rating (if surveyed)
- **Error Recovery**: > 70% recover after error without abandoning

### 10.3 Business Metrics
- **Adoption Rate**: % of active users engaging with agent
- **Feature Usage**: Most common agent tasks
- **Cost per Conversation**: < $0.01 (LLM costs)

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Unauthorized transfers | High | Explicit confirmation flow, audit logging |
| API rate limiting | Medium | Caching, request throttling |
| LLM hallucinations | Medium | Tool-based design, validate all data from API |
| High LLM costs | Low | Token budgets, shorter contexts, caching |
| Poor user experience | Medium | User testing, iteration, clear error messages |
| Model unavailability | Low | Fallback model configuration |

---

## 12. References

- [Microsoft Agent Framework Documentation](https://github.com/microsoft/agent-framework)
- [Azure Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Agent Framework Python SDK](https://pypi.org/project/agent-framework-core/)
- [AI Toolkit for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio)

---

**Document Status**: Ready for Review  
**Next Steps**: Create implementation plan (plan-agent.md)
