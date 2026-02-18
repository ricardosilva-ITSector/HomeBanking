"""
Home Banking AI Agent - Main Entry Point

This module implements an intelligent banking assistant using Microsoft Agent Framework
and Azure Foundry Agent Service.
"""

import argparse
import asyncio
import os
import sys
from typing import Optional

from agent_framework.azure import AzureAIClient
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables (override=True ensures it works in deployed environments)
load_dotenv(override=True)

# System prompt for the banking assistant
SYSTEM_PROMPT = """You are a helpful banking assistant for a home banking application. You help users 
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
2. Present clear transfer summary with "From", "To", "Amount"
3. Show balances before and after transfer
4. Ask for EXPLICIT confirmation: "Would you like me to proceed with this transfer?"
5. Wait for affirmative response: "yes", "confirm", "proceed", "go ahead", or similar
6. Execute only after confirmation
7. If user says "no", "cancel", "stop", or similar, acknowledge and do not execute
8. Provide confirmation with transaction details after successful transfer

Remember: You are an assistant, not a licensed financial advisor. Provide general 
guidance and insights, but do not give personalized investment or financial advice."""


async def run_cli_mode():
    """Run the agent in CLI mode for testing and development."""
    print("🏦 Home Banking Assistant - CLI Mode")
    print("=" * 50)
    print("Initializing agent...")
    
    # Get configuration from environment
    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model_deployment_name = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME")
    api_key = os.getenv("FOUNDRY_API_KEY")
    
    if not project_endpoint or not model_deployment_name:
        print("❌ Error: Missing configuration!")
        print("Please set FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT_NAME in .env file")
        print("See .env.example for reference")
        return
    
    # Check if using placeholder values
    if "placeholder" in project_endpoint.lower() or (api_key and "your-api-key" in api_key.lower()):
        print("⚠️  Warning: Using placeholder configuration!")
        print("Please configure actual Azure Foundry credentials in .env file")
        print("To continue anyway, follow setup instructions in README.md")
        return
    
    try:
        # Import tools dynamically (after they're created)
        try:
            from tools import get_account_balances, get_transactions, execute_transfer, get_spending_insights
            tools = [get_account_balances, get_transactions, execute_transfer, get_spending_insights]
        except ImportError:
            print("⚠️  Warning: Tools module not found. Running with basic agent (no API integration)")
            tools = []
        
        # Use API key if provided, otherwise use DefaultAzureCredential
        if api_key:
            print("🔑 Using API key authentication")
            client = AzureAIClient(
                project_endpoint=project_endpoint,
                model_deployment_name=model_deployment_name,
                credential=AzureKeyCredential(api_key),
            )
            async with client.create_agent(
                name="HomeBankingAgent",
                instructions=SYSTEM_PROMPT,
                tools=tools,
            ) as agent:
                await _run_cli_conversation(agent)
        else:
            print("🔐 Using Azure credential authentication")
            async with (
                DefaultAzureCredential() as credential,
                AzureAIClient(
                    project_endpoint=project_endpoint,
                    model_deployment_name=model_deployment_name,
                    credential=credential,
                ).create_agent(
                    name="HomeBankingAgent",
                    instructions=SYSTEM_PROMPT,
                    tools=tools,
                ) as agent,
            ):
                await _run_cli_conversation(agent)
    
    except Exception as e:
        print(f"❌ Fatal error initializing agent: {str(e)}")
        print("Please check your Azure credentials and configuration")
        import traceback
        traceback.print_exc()
        return


async def _run_cli_conversation(agent):
    """Run the CLI conversation loop with the agent."""
    try:
        # Create a new thread for conversation continuity
        thread = agent.get_new_thread()
        
        print("✅ Agent ready! Type 'exit', 'quit', or 'bye' to quit.")
        print("=" * 50)
        print()
        
        # Main conversation loop
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Thank you for using Home Banking Assistant. Goodbye!")
                    break
                
                print("Agent: ", end="", flush=True)
                
                # Stream the response
                async for chunk in agent.run_stream(user_input, thread=thread):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                
                print("\n")  # New line after response
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
                continue
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Error running conversation: {str(e)}")
        import traceback
        traceback.print_exc()


async def run_server_mode(port: int = 8087):
    """Run the agent as an HTTP server for web app integration."""
    print("🏦 Home Banking Assistant - Server Mode")
    print("=" * 50)
    print(f"Starting server on http://127.0.0.1:{port}")
    print("Initializing agent...")
    
    # Get configuration from environment
    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model_deployment_name = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME")
    api_key = os.getenv("FOUNDRY_API_KEY")
    
    if not project_endpoint or not model_deployment_name:
        print("❌ Error: Missing configuration!")
        print("Please set FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT_NAME in .env file")
        return
    
    if "placeholder" in project_endpoint.lower() or (api_key and "your-api-key" in api_key.lower()):
        print("⚠️  Warning: Using placeholder configuration!")
        print("Server will start but agent calls will fail until you configure real credentials")
    
    try:
        from azure.ai.agentserver.agentframework import from_agent_framework
        
        # Import tools
        try:
            from tools import get_account_balances, get_transactions, execute_transfer, get_spending_insights
            tools = [get_account_balances, get_transactions, execute_transfer, get_spending_insights]
            print(f"✅ Loaded {len(tools)} tools")
        except ImportError as e:
            print(f"⚠️  Warning: Could not load tools: {e}")
            print("Running with basic agent (no API integration)")
            tools = []
        
        # Use API key if provided, otherwise use DefaultAzureCredential
        if api_key:
            print("🔑 Using API key authentication")
            client = AzureAIClient(
                project_endpoint=project_endpoint,
                model_deployment_name=model_deployment_name,
                credential=AzureKeyCredential(api_key),
            )
            async with client.create_agent(
                name="HomeBankingAgent",
                instructions=SYSTEM_PROMPT,
                tools=tools,
            ) as agent:
                print("✅ Agent initialized successfully")
                print(f"🚀 Server running at http://127.0.0.1:{port}")
                print("Press Ctrl+C to stop")
                print("=" * 50)
                
                # Start the HTTP server
                await from_agent_framework(agent).run_async(port=port)
        else:
            print("🔐 Using Azure credential authentication")
            async with DefaultAzureCredential() as credential:
                client = AzureAIClient(
                    project_endpoint=project_endpoint,
                    model_deployment_name=model_deployment_name,
                    credential=credential,
                )
                async with client.create_agent(
                    name="HomeBankingAgent",
                    instructions=SYSTEM_PROMPT,
                    tools=tools,
                ) as agent:
                    print("✅ Agent initialized successfully")
                    print(f"🚀 Server running at http://127.0.0.1:{port}")
                    print("Press Ctrl+C to stop")
                    print("=" * 50)
                    
                    # Start the HTTP server
                    await from_agent_framework(agent).run_async(port=port)
    
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Home Banking AI Agent - Powered by Microsoft Agent Framework"
    )
    parser.add_argument(
        '--server',
        action='store_true',
        help='Run in server mode (HTTP endpoint for web app)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv('AGENT_PORT', '8087')),
        help='Port for server mode (default: 8087, or from AGENT_PORT env var)'
    )
    
    args = parser.parse_args()
    
    if args.server:
        await run_server_mode(args.port)
    else:
        await run_cli_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
