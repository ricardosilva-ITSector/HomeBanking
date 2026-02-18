"""
Runtime backends for HomeBanking agent service.

Primary backend: Azure AI Foundry Agents SDK (hosted threads/runs).
Fallback backend: existing Agent Framework wrapper.
"""

import json
import inspect
from pathlib import Path
from typing import Any, Optional, AsyncGenerator

from agent_framework.azure import AzureAIClient
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential


class BaseRuntime:
    async def start(self) -> None:
        raise NotImplementedError

    async def stop(self) -> None:
        raise NotImplementedError

    async def create_thread(self) -> str:
        raise NotImplementedError

    async def get_or_create_thread(self, thread_id: Optional[str]) -> str:
        raise NotImplementedError

    async def stream_message(self, thread_id: str, user_input: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError


class AgentFrameworkRuntime(BaseRuntime):
    """Legacy fallback runtime using Agent Framework wrapper."""

    def __init__(
        self,
        project_endpoint: str,
        model_deployment_name: str,
        api_key: Optional[str],
        system_prompt: str,
        tools: list[Any],
    ):
        self.project_endpoint = project_endpoint
        self.model_deployment_name = model_deployment_name
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.tools = tools
        self._agent_cm: Optional[Any] = None
        self._agent: Optional[Any] = None
        self._threads: dict[str, Any] = {}
        self._credential_cm: Optional[Any] = None

    async def start(self) -> None:
        if self._agent is not None:
            return

        if self.api_key and "your-api-key" not in self.api_key.lower():
            client = AzureAIClient(
                project_endpoint=self.project_endpoint,
                model_deployment_name=self.model_deployment_name,
                credential=AzureKeyCredential(self.api_key),
            )
            self._agent_cm = client.create_agent(
                name="HomeBankingAgent",
                instructions=self.system_prompt,
                tools=self.tools,
            )
            self._agent = await self._agent_cm.__aenter__()
            return

        self._credential_cm = DefaultAzureCredential()
        credential = await self._credential_cm.__aenter__()
        client = AzureAIClient(
            project_endpoint=self.project_endpoint,
            model_deployment_name=self.model_deployment_name,
            credential=credential,
        )
        self._agent_cm = client.create_agent(
            name="HomeBankingAgent",
            instructions=self.system_prompt,
            tools=self.tools,
        )
        self._agent = await self._agent_cm.__aenter__()

    async def stop(self) -> None:
        self._threads.clear()

        if self._agent_cm is not None:
            await self._agent_cm.__aexit__(None, None, None)
            self._agent_cm = None

        if self._credential_cm is not None:
            await self._credential_cm.__aexit__(None, None, None)
            self._credential_cm = None

        self._agent = None

    def _ensure_agent(self) -> Any:
        if self._agent is None:
            raise RuntimeError("Agent runtime is not initialized")
        return self._agent

    async def create_thread(self) -> str:
        agent = self._ensure_agent()
        thread_id = f"local-{id(agent)}-{len(self._threads) + 1}"
        self._threads[thread_id] = agent.get_new_thread()
        return thread_id

    async def get_or_create_thread(self, thread_id: Optional[str]) -> str:
        if thread_id and thread_id in self._threads:
            return thread_id
        return await self.create_thread()

    async def stream_message(self, thread_id: str, user_input: str) -> AsyncGenerator[str, None]:
        agent = self._ensure_agent()
        thread = self._threads[thread_id]
        async for chunk in agent.run_stream(user_input, thread=thread):
            if chunk.text:
                yield chunk.text


class FoundryAgentsRuntime(BaseRuntime):
    """Primary runtime using Azure AI Foundry Agents SDK with hosted threads/runs."""

    def __init__(
        self,
        project_endpoint: str,
        model_deployment_name: str,
        api_key: Optional[str],
        system_prompt: str,
        tools: list[Any],
        agent_id: Optional[str] = None,
        state_file: Optional[str] = None,
    ):
        self.project_endpoint = project_endpoint
        self.model_deployment_name = model_deployment_name
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.tools = tools
        self.agent_id = agent_id
        self.state_file = state_file

        self._client_cm: Optional[Any] = None
        self._client: Optional[Any] = None
        self._credential_cm: Optional[Any] = None
        self._thread_ids: set[str] = set()
        self._toolset: Optional[Any] = None

    def _load_persisted_agent_id(self) -> Optional[str]:
        if not self.state_file:
            return None

        path = Path(self.state_file)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            persisted_agent_id = data.get("agent_id")
            return persisted_agent_id if isinstance(persisted_agent_id, str) and persisted_agent_id else None
        except Exception:
            return None

    def _save_persisted_agent_id(self) -> None:
        if not self.state_file or not self.agent_id:
            return

        path = Path(self.state_file)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(json.dumps({"agent_id": self.agent_id}), encoding="utf-8")

    async def start(self) -> None:
        if self._client is not None:
            return

        try:
            from azure.ai.agents.aio import AgentsClient
            from azure.ai.agents.models import AsyncFunctionTool, AsyncToolSet
        except ImportError as ex:
            raise RuntimeError(
                "Foundry Agents SDK imports failed. Ensure azure-ai-agents is installed."
            ) from ex

        if self.api_key and "your-api-key" not in self.api_key.lower():
            self._client_cm = AgentsClient(
                endpoint=self.project_endpoint,
                credential=AzureKeyCredential(self.api_key),
            )
            self._client = await self._client_cm.__aenter__()
        else:
            self._credential_cm = DefaultAzureCredential()
            credential = await self._credential_cm.__aenter__()
            self._client_cm = AgentsClient(
                endpoint=self.project_endpoint,
                credential=credential,
            )
            self._client = await self._client_cm.__aenter__()

        function_tool = AsyncFunctionTool(set(self.tools))
        toolset = AsyncToolSet()
        toolset.add(function_tool)
        self._client.enable_auto_function_calls(toolset)
        self._toolset = toolset

        if not self.agent_id:
            self.agent_id = self._load_persisted_agent_id()

        if self.agent_id:
            try:
                await self._client.get_agent(self.agent_id)
                self._save_persisted_agent_id()
                return
            except Exception:
                self.agent_id = None

        agent = await self._client.create_agent(
            model=self.model_deployment_name,
            name="HomeBankingAgent",
            instructions=self.system_prompt,
            toolset=self._toolset,
        )
        self.agent_id = agent.id
        self._save_persisted_agent_id()

    async def stop(self) -> None:
        self._thread_ids.clear()

        if self._client_cm is not None:
            await self._client_cm.__aexit__(None, None, None)
            self._client_cm = None

        if self._credential_cm is not None:
            await self._credential_cm.__aexit__(None, None, None)
            self._credential_cm = None

        self._client = None

    def _ensure_client(self) -> Any:
        if self._client is None:
            raise RuntimeError("Foundry Agents client is not initialized")
        return self._client

    def _ensure_agent_id(self) -> str:
        if not self.agent_id:
            raise RuntimeError("Foundry agent id is not initialized")
        return self.agent_id

    async def create_thread(self) -> str:
        client = self._ensure_client()
        thread = await client.threads.create()
        self._thread_ids.add(thread.id)
        return thread.id

    async def get_or_create_thread(self, thread_id: Optional[str]) -> str:
        client = self._ensure_client()

        if thread_id:
            if thread_id in self._thread_ids:
                return thread_id
            try:
                await client.threads.get(thread_id)
                self._thread_ids.add(thread_id)
                return thread_id
            except Exception:
                pass

        return await self.create_thread()

    def _is_meaningful_text(self, text: str) -> bool:
        normalized = text.strip()
        if not normalized:
            return False

        if normalized in {"[DONE]", "DONE"}:
            return False

        if normalized.startswith("[") and normalized.endswith("]") and len(normalized) <= 32:
            return False

        return True

    def _extract_text(self, event_data: Any) -> Optional[str]:
        direct_text = getattr(event_data, "text", None)
        if isinstance(direct_text, str) and self._is_meaningful_text(direct_text):
            return direct_text

        text_messages = getattr(event_data, "text_messages", None)
        if text_messages:
            segments: list[str] = []
            for message in text_messages:
                text_obj = getattr(message, "text", None)
                value = getattr(text_obj, "value", None)
                if isinstance(value, str) and self._is_meaningful_text(value):
                    segments.append(value)
            if segments:
                return "\n".join(segments)

        def collect_strings(value: Any, seen: set[int]) -> list[str]:
            if value is None:
                return []

            value_id = id(value)
            if value_id in seen:
                return []
            seen.add(value_id)

            if isinstance(value, str):
                stripped = value.strip()
                return [stripped] if stripped else []

            if isinstance(value, dict):
                results: list[str] = []

                text_field = value.get("text")
                if isinstance(text_field, str) and text_field.strip():
                    results.append(text_field.strip())
                elif isinstance(text_field, dict):
                    text_value = text_field.get("value")
                    if isinstance(text_value, str) and text_value.strip():
                        results.append(text_value.strip())

                value_field = value.get("value")
                value_type = value.get("type")
                if (
                    isinstance(value_field, str)
                    and value_field.strip()
                    and value_type in {"text", "output_text", "text_delta", "message_delta"}
                ):
                    results.append(value_field.strip())

                for nested_key in (
                    "delta",
                    "content",
                    "message",
                    "messages",
                    "text_messages",
                    "output",
                    "data",
                    "item",
                ):
                    if nested_key in value:
                        results.extend(collect_strings(value[nested_key], seen))

                for nested in value.values():
                    if isinstance(nested, (dict, list, tuple)):
                        results.extend(collect_strings(nested, seen))

                return results

            if isinstance(value, (list, tuple, set)):
                results: list[str] = []
                for item in value:
                    results.extend(collect_strings(item, seen))
                return results

            object_dict = getattr(value, "__dict__", None)
            if isinstance(object_dict, dict):
                return collect_strings(object_dict, seen)

            return []

        collected = collect_strings(event_data, set())
        if collected:
            unique: list[str] = []
            for item in collected:
                if self._is_meaningful_text(item) and item not in unique:
                    unique.append(item)
            if unique:
                return "\n".join(unique)

        return None

    async def _fetch_latest_assistant_text(self, client: Any, thread_id: str) -> Optional[str]:
        list_messages = getattr(client.messages, "list", None)
        if not callable(list_messages):
            return None

        try:
            messages_result = list_messages(thread_id=thread_id)
            if inspect.isawaitable(messages_result):
                messages_result = await messages_result
            messages: list[Any] = []

            if hasattr(messages_result, "__aiter__"):
                async for item in messages_result:
                    messages.append(item)
            elif hasattr(messages_result, "__iter__"):
                messages = list(messages_result)
            else:
                data = getattr(messages_result, "data", None)
                if isinstance(data, list):
                    messages = data

            for message in reversed(messages):
                role = getattr(message, "role", None)
                if role is None and isinstance(message, dict):
                    role = message.get("role")
                if role != "assistant":
                    continue

                text = self._extract_text(message)
                if text:
                    return text
        except Exception:
            return None

        return None

    async def _fetch_latest_run_error(self, client: Any, thread_id: str) -> Optional[str]:
        list_runs = getattr(client.runs, "list", None)
        if not callable(list_runs):
            return None

        try:
            runs_result = list_runs(thread_id=thread_id)
            if inspect.isawaitable(runs_result):
                runs_result = await runs_result

            runs: list[Any] = []
            if hasattr(runs_result, "__aiter__"):
                async for run in runs_result:
                    runs.append(run)
            elif hasattr(runs_result, "__iter__"):
                runs = list(runs_result)
            else:
                data = getattr(runs_result, "data", None)
                if isinstance(data, list):
                    runs = data

            if not runs:
                return None

            latest_run = runs[0]
            run_status = getattr(latest_run, "status", None) or (
                latest_run.get("status") if isinstance(latest_run, dict) else None
            )
            last_error = getattr(latest_run, "last_error", None)
            if last_error is None and isinstance(latest_run, dict):
                last_error = latest_run.get("last_error")

            if isinstance(last_error, dict):
                code = last_error.get("code")
                message = last_error.get("message")
                if code and message:
                    return f"status={run_status}, code={code}, message={message}"
                if message:
                    return f"status={run_status}, message={message}"

            error_code = getattr(last_error, "code", None)
            error_message = getattr(last_error, "message", None)
            if error_message:
                if error_code:
                    return f"status={run_status}, code={error_code}, message={error_message}"
                return f"status={run_status}, message={error_message}"

            if run_status:
                return f"status={run_status}"
        except Exception:
            return None

        return None

    def _extract_run_failure_details(self, event_data: Any) -> Optional[str]:
        if event_data is None:
            return None

        if isinstance(event_data, dict):
            last_error = event_data.get("last_error")
            status = event_data.get("status")
            if isinstance(last_error, dict):
                code = last_error.get("code")
                message = last_error.get("message")
                if code and message:
                    return f"status={status}, code={code}, message={message}"
                if message:
                    return f"status={status}, message={message}"

        last_error = getattr(event_data, "last_error", None)
        status = getattr(event_data, "status", None)
        if last_error is not None:
            code = getattr(last_error, "code", None)
            message = getattr(last_error, "message", None)
            if code and message:
                return f"status={status}, code={code}, message={message}"
            if message:
                return f"status={status}, message={message}"

        return None

    async def stream_message(self, thread_id: str, user_input: str) -> AsyncGenerator[str, None]:
        client = self._ensure_client()
        agent_id = self._ensure_agent_id()

        await client.messages.create(thread_id=thread_id, role="user", content=user_input)

        emitted_any = False
        last_emitted: Optional[str] = None
        seen_event_types: list[str] = []
        stream_context = await client.runs.stream(thread_id=thread_id, agent_id=agent_id)
        async with stream_context as stream:
            async for event_type, event_data, _ in stream:
                event_name = str(event_type)
                seen_event_types.append(event_name)
                if "DONE" in event_name:
                    break
                if "ERROR" in event_name:
                    raise RuntimeError(f"Foundry streaming error: {event_data}")
                if "FAILED" in event_name.upper() or event_name.endswith(".failed"):
                    details = self._extract_run_failure_details(event_data)
                    if details:
                        raise RuntimeError(f"Foundry run failed: {details}")
                    raise RuntimeError("Foundry run failed")

                text = self._extract_text(event_data)
                if text:
                    if text != last_emitted:
                        emitted_any = True
                        last_emitted = text
                        yield text

        if not emitted_any:
            fallback_text = await self._fetch_latest_assistant_text(client=client, thread_id=thread_id)
            if fallback_text:
                yield fallback_text
            else:
                event_summary = ", ".join(seen_event_types[-8:]) if seen_event_types else "none"
                latest_run_error = await self._fetch_latest_run_error(client=client, thread_id=thread_id)
                if latest_run_error:
                    raise RuntimeError(
                        "Foundry run completed without assistant text output. "
                        f"Event types: {event_summary}. Latest run: {latest_run_error}"
                    )
                raise RuntimeError(
                    f"Foundry run completed without assistant text output. Event types: {event_summary}"
                )


async def build_runtime(
    project_endpoint: str,
    model_deployment_name: str,
    api_key: Optional[str],
    system_prompt: str,
    tools: list[Any],
    preferred_backend: str,
    foundry_agent_id: Optional[str],
    foundry_state_file: Optional[str],
) -> BaseRuntime:
    if preferred_backend.lower() == "agent-framework":
        runtime = AgentFrameworkRuntime(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment_name,
            api_key=api_key,
            system_prompt=system_prompt,
            tools=tools,
        )
        await runtime.start()
        return runtime

    try:
        runtime = FoundryAgentsRuntime(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment_name,
            api_key=api_key,
            system_prompt=system_prompt,
            tools=tools,
            agent_id=foundry_agent_id,
            state_file=foundry_state_file,
        )
        await runtime.start()
        return runtime
    except Exception:
        fallback = AgentFrameworkRuntime(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment_name,
            api_key=api_key,
            system_prompt=system_prompt,
            tools=tools,
        )
        await fallback.start()
        return fallback
