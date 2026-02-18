"""
HomeBanking Agent Service - Main Entry Point

This service hosts a conversational transfer copilot using
Microsoft Agent Framework + Azure AI Foundry Agent Service.
"""
import asyncio
import structlog
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from agent_framework import WorkflowBuilder, WorkflowContext, handler
from agent_framework import ChatMessage, Role
from azure.ai.agentserver.agentframework import from_agent_framework

from config import AgentConfig
from tools import HomeBankingTools

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger(__name__)


async def create_agent(config: AgentConfig):
    """
    Create and configure the HomeBanking transfer copilot agent.
    
    Args:
        config: Agent configuration
    
    Returns:
        Configured agent ready to serve requests
    """
    logger.info("Initializing HomeBanking agent", model=config.foundry_model_deployment_name)
    
    # Initialize Foundry project client
    project_client = AIProjectClient(
        endpoint=config.foundry_project_endpoint,
        credential=DefaultAzureCredential()
    )
    
    # Initialize HomeBanking API tools
    tools = HomeBankingTools(
        api_base_url=config.homebanking_api_base_url,
        api_key=config.homebanking_api_key
    )
    
    # Agent instructions for safe transfer behavior
    agent_instructions = """
You are a helpful banking assistant for HomeBanking application.

Your primary role is to help users transfer money between their accounts safely and accurately.

CRITICAL RULES:
1. NEVER execute a transfer without EXPLICIT user confirmation.
2. Before requesting confirmation, ALWAYS display a clear summary showing:
   - Source account name and current balance
   - Destination account name
   - Transfer amount
   - Optional description
3. ONLY call create_transfer AFTER the user has explicitly confirmed (e.g., "yes", "confirm", "proceed").
4. If validation fails or transfer fails, explain the error clearly to the user.
5. You can use list_accounts and list_transactions to help users understand their accounts.

TRANSFER WORKFLOW:
1. Gather: Ask for missing information (from account, to account, amount, description).
2. Summarize: Show a clear transfer preview with account details and balances.
3. Confirm: Ask "Please confirm this transfer by typing 'yes' or 'confirm'."
4. Execute: ONLY if confirmed, call create_transfer.
5. Report: Share the result (success with transaction IDs, or error message).

NEVER fabricate transfer completion.
NEVER assume confirmation unless explicitly stated.
""".strip()
    
    # For MVP, we'll create a simple agent workflow
    # In future iterations, this will expand to multi-step orchestration
    
    # TODO: Implement proper workflow with FunctionTool registration
    # For now, this is a placeholder showing the structure
    
    logger.info("Agent created successfully")
    
    # Note: Full implementation of WorkflowBuilder with FunctionTool
    # will be added in A004-A005 tasks
    
    return None  # Placeholder until full implementation


async def main():
    """Main entry point for the agent service."""
    try:
        # Load configuration
        logger.info("Loading configuration")
        config = AgentConfig.from_env()
        config.validate()
        logger.info(
            "Configuration loaded",
            foundry_endpoint=config.foundry_project_endpoint,
            model=config.foundry_model_deployment_name,
            api_base=config.homebanking_api_base_url
        )
        
        # Create agent
        agent = await create_agent(config)
        
        # TODO: Implement agent-as-server pattern
        # This will be completed in A003 after Foundry prerequisites are ready
        
        logger.info(
            "Agent service ready",
            host=config.server_host,
            port=config.server_port
        )
        
        # For MVP setup verification, just log success
        logger.info("✓ Agent sidecar initialized successfully")
        logger.info("Next: Configure Foundry project and deploy model (see README.md)")
        
    except Exception as e:
        logger.error("Failed to start agent service", error=str(e), exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
