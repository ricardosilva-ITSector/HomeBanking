"""
Home Banking AI Agent - HTTP Server

Authoritative runtime surface for web integration.
Contract:
- POST /agent/threads
- POST /agent/messages (SSE)
- GET  /agent/health
"""

import json
import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from foundry_runtime import BaseRuntime, build_runtime
from tools import (
    execute_transfer,
    get_account_balances,
    get_spending_insights,
    get_transactions,
)

load_dotenv(override=True)

SYSTEM_PROMPT = """You are a helpful banking assistant for a home banking application.

CRITICAL: You MUST use your tools to get real data. DO NOT respond without calling the appropriate tool first.

WHEN TO USE TOOLS:
- User asks about balances/accounts → IMMEDIATELY call get_account_balances()
- User asks about transactions/history → IMMEDIATELY call get_transactions()
- User asks for spending analysis/insights → IMMEDIATELY call get_spending_insights()
- User wants to transfer money → First call get_account_balances(), then ask for confirmation, then call execute_transfer()

YOUR WORKFLOW:
1. Identify what the user needs
2. Call the appropriate tool IMMEDIATELY (don't say you will, just do it)
3. Present the results clearly
4. For transfers: get accounts → confirm → execute

IMPORTANT RULES:
- NEVER say "I'll check" or "Let me verify" without IMMEDIATELY calling the tool
- ALWAYS use tools to get real data - NEVER make up information
- For transfers, ALWAYS confirm before calling execute_transfer
- Present data clearly with tables when appropriate
"""

@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        global runtime
        if runtime is not None:
            await runtime.stop()
            runtime = None


app = FastAPI(
    title="Home Banking AI Agent",
    description="AI-powered banking assistant API",
    version="1.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateThreadResponse(BaseModel):
    thread_id: str


class AgentMessageRequest(BaseModel):
    input: str
    thread_id: Optional[str] = None


runtime: Optional[BaseRuntime] = None
runtime_mode: str = "unknown"
runtime_error: Optional[str] = None


def _get_foundry_config() -> tuple[str, str, Optional[str], str, Optional[str], str]:
    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model_deployment_name = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME")
    api_key = os.getenv("FOUNDRY_API_KEY")
    backend = os.getenv("AGENT_RUNTIME_BACKEND", "foundry")
    foundry_agent_id = os.getenv("FOUNDRY_AGENT_ID")
    foundry_state_file = os.getenv("FOUNDRY_AGENT_STATE_FILE", ".foundry-agent-state.json")

    if not project_endpoint or not model_deployment_name:
        raise HTTPException(
            status_code=500,
            detail="Missing configuration: FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT_NAME required",
        )

    return (
        project_endpoint,
        model_deployment_name,
        api_key,
        backend,
        foundry_agent_id,
        foundry_state_file,
    )


def _get_tools():
    return [
        get_account_balances,
        get_transactions,
        execute_transfer,
        get_spending_insights,
    ]


async def _ensure_runtime() -> BaseRuntime:
    global runtime, runtime_mode, runtime_error

    if runtime is not None:
        return runtime

    (
        project_endpoint,
        model_deployment_name,
        api_key,
        backend,
        foundry_agent_id,
        foundry_state_file,
    ) = _get_foundry_config()

    runtime = await build_runtime(
        project_endpoint=project_endpoint,
        model_deployment_name=model_deployment_name,
        api_key=api_key,
        system_prompt=SYSTEM_PROMPT,
        tools=_get_tools(),
        preferred_backend=backend,
        foundry_agent_id=foundry_agent_id,
        foundry_state_file=foundry_state_file,
    )
    runtime_mode = runtime.__class__.__name__
    runtime_error = None
    return runtime


@app.get("/agent/health")
async def agent_health():
    try:
        _, _, _, backend, _, _ = _get_foundry_config()
        active_agent_id = getattr(runtime, "agent_id", None) if runtime is not None else None
        return {
            "status": "healthy" if runtime is not None else "degraded",
            "agent_ready": runtime is not None,
            "runtime_mode": runtime_mode if runtime is not None else f"not-initialized ({backend})",
            "backend_preference": backend,
            "active_agent_id": active_agent_id,
            "runtime_error": runtime_error,
        }
    except HTTPException as ex:
        return {
            "status": "degraded",
            "agent_ready": False,
            "runtime_mode": runtime_mode,
            "backend_preference": "unknown",
            "error": ex.detail,
            "runtime_error": runtime_error,
        }
    except Exception as ex:
        return {
            "status": "degraded",
            "agent_ready": False,
            "runtime_mode": runtime_mode,
            "backend_preference": "unknown",
            "error": str(ex),
            "runtime_error": runtime_error,
        }


@app.post("/agent/threads", response_model=CreateThreadResponse)
async def create_thread():
    try:
        active_runtime = await _ensure_runtime()
    except Exception as ex:
        raise HTTPException(status_code=503, detail=f"Agent runtime unavailable: {str(ex)}")

    thread_id = await active_runtime.create_thread()
    return CreateThreadResponse(thread_id=thread_id)


@app.post("/agent/messages")
async def post_message(request: AgentMessageRequest):
    try:
        active_runtime = await _ensure_runtime()
    except Exception as ex:
        raise HTTPException(status_code=503, detail=f"Agent runtime unavailable: {str(ex)}")

    thread_id = await active_runtime.get_or_create_thread(request.thread_id)

    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'thread', 'thread_id': thread_id})}\n\n"

            async for text in active_runtime.stream_message(thread_id=thread_id, user_input=request.input):
                yield f"data: {json.dumps({'type': 'text', 'text': text})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as ex:
            yield f"data: {json.dumps({'type': 'error', 'error': str(ex)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("AGENT_PORT", "8087"))

    print("=" * 50)
    print("🏦 Home Banking AI Agent Server")
    print("=" * 50)
    print(f"🚀 Starting server on http://127.0.0.1:{port}")
    print("📡 Endpoints:")
    print("   - POST /agent/threads     (create session thread id)")
    print("   - POST /agent/messages    (streaming SSE)")
    print("   - GET  /agent/health      (health check)")
    print("=" * 50)

    uvicorn.run(app, host="127.0.0.1", port=port)
