"""
Home Banking AI Agent - HTTP Server

This module provides a FastAPI server that exposes the agent as an HTTP endpoint.
"""

import asyncio
import json
import os
import uuid
from typing import Optional

from agent_framework.azure import AzureAIClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Load environment variables
load_dotenv(override=True)

# Import tools
from tools import (
    execute_transfer,
    get_account_balances,
    get_spending_insights,
    get_transactions,
)

# Test tool - simple function to verify tools work
async def test_simple_tool() -> str:
    """A simple test tool that returns a message. Call this to verify the agent can execute tools."""
    print("🧪 TEST_SIMPLE_TOOL CALLED!")
    return "✅ This is a test message from test_simple_tool(). Tools are working!"

# System prompt for the banking assistant
SYSTEM_PROMPT = """You are a helpful banking assistant for a home banking application. You help users 
manage their accounts, understand their transactions, and make informed financial decisions.

Your capabilities:
- Answer questions about account balances and transaction history
- Analyze spending patterns and provide financial insights
- Guide users through money transfers between their accounts
- Provide general financial literacy guidance

Important behavioral rules:
1. ALWAYS call get_account_balances first to understand the user's accounts
2. For transfer requests, ALWAYS confirm with the user before calling execute_transfer
3. Present information clearly with proper formatting (use markdown tables for account lists)
4. Be proactive - if you see unusual spending patterns, mention them
5. Be conversational and friendly, but professional
6. Never make assumptions about account IDs - always get fresh data first

Example interaction:
User: "Transfer $50 from checking to savings"
You: [Call get_account_balances to get account IDs]
     "I can help with that! I'll transfer $50.00 from your Checking Account 
     (ending in XXXX) to your Savings Account (ending in YYYY). 
     Should I proceed with this transfer?"
User: "Yes"
You: [Call execute_transfer]
     "✅ Transfer complete! $50.00 has been moved from Checking to Savings."
"""

# FastAPI app
app = FastAPI(
    title="Home Banking AI Agent",
    description="AI-powered banking assistant API",
    version="1.0.0"
)

# Enable CORS for web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class AgentRequest(BaseModel):
    """Request model for agent interaction"""
    input: str
    thread_id: Optional[str] = None

class AgentResponse(BaseModel):
    """Response model for agent interaction"""
    thread_id: str
    output: str

#Configuration
SYSTEM_PROMPT_CONFIG = SYSTEM_PROMPT  # Save for reuse


async def run_agent_conversation(user_input: str):
    """
    Run a conversation with the agent (creates agent fresh each time).
    Returns (thread_id, output_text).
    """
    # Load configuration
    project_endpoint = os.getenv('FOUNDRY_PROJECT_ENDPOINT')
    model_deployment_name = os.getenv('FOUNDRY_MODEL_DEPLOYMENT_NAME')
    
    if not project_endpoint or not model_deployment_name:
        raise HTTPException(
            status_code=500,
            detail="Missing configuration: FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT_NAME required"
        )
    
    # Import tools
    tools = [test_simple_tool, get_account_balances, get_transactions, execute_transfer, get_spending_insights]
    
    # Generate thread ID
    thread_id = str(uuid.uuid4())
    output = ""
    
    # Use Azure AD authentication (DefaultAzureCredential)
    async with (
        DefaultAzureCredential() as credential,
        AzureAIClient(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment_name,
            credential=credential,
        ).create_agent(
            name="HomeBankingAgent",
            instructions=SYSTEM_PROMPT_CONFIG,
            tools=tools,
        ) as agent,
    ):
        thread = agent.get_new_thread()
        async for chunk in agent.run_stream(user_input, thread=thread):
            if chunk.text:
                output += chunk.text
    
    return thread_id, output


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Just check if environment is configured
        project_endpoint = os.getenv('FOUNDRY_PROJECT_ENDPOINT')
        model_deployment_name = os.getenv('FOUNDRY_MODEL_DEPLOYMENT_NAME')
        
        if project_endpoint and model_deployment_name:
            return {"status": "healthy", "agent_ready": True}
        else:
            return {"status": "degraded", "error": "Missing configuration"}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


@app.get("/test")
async def test_agent_init():
    """Test endpoint to diagnose agent initialization"""
    try:
        project_endpoint = os.getenv('FOUNDRY_PROJECT_ENDPOINT')
        model_deployment_name = os.getenv('FOUNDRY_MODEL_DEPLOYMENT_NAME')
        
        tools = [test_simple_tool, get_account_balances, get_transactions, execute_transfer, get_spending_insights]
        
        # Use Azure AD authentication
        async with (
            DefaultAzureCredential() as credential,
            AzureAIClient(
                project_endpoint=project_endpoint,
                model_deployment_name=model_deployment_name,
                credential=credential,
            ).create_agent(
                name="TestAgent",
                instructions="You are a test agent.",
                tools=tools,
            ) as agent,
        ):
            thread = agent.get_new_thread()
            
            # Try to run the agent
            output = ""
            async for chunk in agent.run_stream("Hello", thread=thread):
                if chunk.text:
                    output += chunk.text
            
            return {"status": "success", "message": "Agent ran successfully", "output": output}
            
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}


@app.post("/agent/chat")
async def chat(request: AgentRequest):
    """
    Chat with the banking agent (non-streaming).
    
    Args:
        request: AgentRequest with input message and optional thread_id
        
    Returns:
        AgentResponse with thread_id and output message
    """
    try:
        thread_id, output = await run_agent_conversation(request.input)
        
        return AgentResponse(
            thread_id=thread_id,
            output=output
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.post("/agent/stream")
async def stream_chat(request: AgentRequest):
    """
    Chat with the banking agent (streaming response).
    
    Args:
        request: AgentRequest with input message and optional thread_id
        
    Returns:
        StreamingResponse with server-sent events
    """
    # Load configuration
    project_endpoint = os.getenv('FOUNDRY_PROJECT_ENDPOINT')
    model_deployment_name = os.getenv('FOUNDRY_MODEL_DEPLOYMENT_NAME')
    
    if not project_endpoint or not model_deployment_name:
        raise HTTPException(
            status_code=500,
            detail="Missing configuration"
        )
    
    tools = [test_simple_tool, get_account_balances, get_transactions, execute_transfer, get_spending_insights]
    thread_id = str(uuid.uuid4())
    
    async def event_generator():
        """Generate server-sent events"""
        try:
            # Send thread ID first
            yield f"data: {json.dumps({'type': 'thread_id', 'thread_id': thread_id})}\n\n"
            
            #Use Azure AD authentication
            async with (
                DefaultAzureCredential() as credential,
                AzureAIClient(
                    project_endpoint=project_endpoint,
                    model_deployment_name=model_deployment_name,
                    credential=credential,
                ).create_agent(
                    name="HomeBankingAgent",
                    instructions=SYSTEM_PROMPT_CONFIG,
                    tools=tools,
                ) as agent,
            ):
                thread = agent.get_new_thread()
                async for chunk in agent.run_stream(request.input, thread=thread):
                    if chunk.text:
                        # Send text chunk
                        yield f"data: {json.dumps({'type': 'text', 'text': chunk.text})}\n\n"
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            error_msg = str(e)
            yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('AGENT_PORT', '8087'))
    
    print("=" * 50)
    print("🏦 Home Banking AI Agent Server")
    print("=" * 50)
    print(f"🚀 Starting server on http://127.0.0.1:{port}")
    print(f"📡 Endpoints:")
    print(f"   - POST /agent/chat      (non-streaming)")
    print(f"   - POST /agent/stream    (streaming)")
    print(f"   - GET  /health          (health check)")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=port)
