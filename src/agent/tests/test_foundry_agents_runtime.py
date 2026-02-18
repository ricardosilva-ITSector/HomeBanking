"""Tests for FoundryAgentsRuntime behavior with mocked agents client."""

from types import SimpleNamespace

import pytest

from foundry_runtime import FoundryAgentsRuntime


class MockThreads:
    def __init__(self):
        self.created = 0
        self.get_calls: list[str] = []

    async def create(self):
        self.created += 1
        return SimpleNamespace(id=f"foundry-thread-{self.created}")

    async def get(self, thread_id: str):
        self.get_calls.append(thread_id)
        return SimpleNamespace(id=thread_id)


class MockMessages:
    def __init__(self, listed_messages=None, async_list: bool = False):
        self.calls = []
        self.listed_messages = listed_messages or []
        self.async_list = async_list

    async def create(self, thread_id: str, role: str, content: str):
        self.calls.append(
            {
                "thread_id": thread_id,
                "role": role,
                "content": content,
            }
        )

    def list(self, thread_id: str):
        if self.async_list:
            async def _resolve():
                return self.listed_messages

            return _resolve()
        return self.listed_messages


class MockStream:
    def __init__(self, events):
        self.events = events

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    def __aiter__(self):
        self._iter = iter(self.events)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration as ex:
            raise StopAsyncIteration from ex


class MockRuns:
    def __init__(self, events):
        self.events = events
        self.calls = []

    async def stream(self, thread_id: str, agent_id: str):
        self.calls.append({"thread_id": thread_id, "agent_id": agent_id})
        return MockStream(self.events)


class MockAgentsClient:
    def __init__(self, events, listed_messages=None, async_list: bool = False):
        self.threads = MockThreads()
        self.messages = MockMessages(listed_messages=listed_messages, async_list=async_list)
        self.runs = MockRuns(events)


@pytest.mark.asyncio
async def test_foundry_runtime_get_or_create_thread_reuses_existing_thread_id():
    runtime = FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test",
        model_deployment_name="test-model",
        api_key="test-key",
        system_prompt="test",
        tools=[],
        agent_id="agent-1",
    )

    runtime._client = MockAgentsClient(events=[])
    thread_id = await runtime.get_or_create_thread("thread-existing")

    assert thread_id == "thread-existing"
    assert runtime._client.threads.get_calls == ["thread-existing"]


@pytest.mark.asyncio
async def test_foundry_runtime_get_or_create_thread_creates_when_missing():
    runtime = FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test",
        model_deployment_name="test-model",
        api_key="test-key",
        system_prompt="test",
        tools=[],
        agent_id="agent-1",
    )

    runtime._client = MockAgentsClient(events=[])
    thread_id = await runtime.get_or_create_thread(None)

    assert thread_id == "foundry-thread-1"
    assert runtime._client.threads.created == 1


@pytest.mark.asyncio
async def test_foundry_runtime_stream_message_yields_text_and_deduplicates():
    events = [
        ("MESSAGE_DELTA", SimpleNamespace(text="Hello"), None),
        ("MESSAGE_DELTA", SimpleNamespace(text="Hello"), None),
        ("MESSAGE_DELTA", SimpleNamespace(text="World"), None),
        ("DONE", None, None),
    ]

    runtime = FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test",
        model_deployment_name="test-model",
        api_key="test-key",
        system_prompt="test",
        tools=[],
        agent_id="agent-123",
    )

    runtime._client = MockAgentsClient(events=events)

    chunks = []
    async for chunk in runtime.stream_message("thread-abc", "ping"):
        chunks.append(chunk)

    assert chunks == ["Hello", "World"]
    assert runtime._client.messages.calls == [
        {"thread_id": "thread-abc", "role": "user", "content": "ping"}
    ]
    assert runtime._client.runs.calls == [
        {"thread_id": "thread-abc", "agent_id": "agent-123"}
    ]


@pytest.mark.asyncio
async def test_foundry_runtime_stream_message_raises_on_error_event():
    events = [
        ("ERROR", "boom", None),
    ]

    runtime = FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test",
        model_deployment_name="test-model",
        api_key="test-key",
        system_prompt="test",
        tools=[],
        agent_id="agent-123",
    )

    runtime._client = MockAgentsClient(events=events)

    with pytest.raises(RuntimeError, match="Foundry streaming error"):
        async for _ in runtime.stream_message("thread-abc", "ping"):
            pass


@pytest.mark.asyncio
async def test_foundry_runtime_stream_message_raises_on_failed_run_event_with_details():
    events = [
        (
            "thread.run.failed",
            SimpleNamespace(
                status="failed",
                last_error=SimpleNamespace(code="tool_error", message="Backend API unavailable"),
            ),
            None,
        ),
        ("DONE", None, None),
    ]

    runtime = FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test",
        model_deployment_name="test-model",
        api_key="test-key",
        system_prompt="test",
        tools=[],
        agent_id="agent-123",
    )

    runtime._client = MockAgentsClient(events=events)

    with pytest.raises(RuntimeError, match="Foundry run failed"):
        async for _ in runtime.stream_message("thread-abc", "ping"):
            pass


@pytest.mark.asyncio
async def test_foundry_runtime_stream_message_extracts_nested_delta_text():
    events = [
        (
            "MESSAGE_DELTA",
            SimpleNamespace(
                delta={
                    "content": [
                        {"type": "output_text", "text": {"value": "Balance for checking is €1250"}}
                    ]
                }
            ),
            None,
        ),
        ("DONE", None, None),
    ]

    runtime = FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test",
        model_deployment_name="test-model",
        api_key="test-key",
        system_prompt="test",
        tools=[],
        agent_id="agent-123",
    )

    runtime._client = MockAgentsClient(events=events)

    chunks = []
    async for chunk in runtime.stream_message("thread-abc", "ping"):
        chunks.append(chunk)

    assert chunks == ["Balance for checking is €1250"]


@pytest.mark.asyncio
async def test_foundry_runtime_stream_message_falls_back_to_latest_assistant_message():
    events = [
        ("RUN_STARTED", SimpleNamespace(), None),
        ("DONE", None, None),
    ]

    listed_messages = [
        SimpleNamespace(role="assistant", text_messages=[SimpleNamespace(text=SimpleNamespace(value="Your balance is €1250"))])
    ]

    runtime = FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test",
        model_deployment_name="test-model",
        api_key="test-key",
        system_prompt="test",
        tools=[],
        agent_id="agent-123",
    )

    runtime._client = MockAgentsClient(events=events, listed_messages=listed_messages)

    chunks = []
    async for chunk in runtime.stream_message("thread-abc", "ping"):
        chunks.append(chunk)

    assert chunks == ["Your balance is €1250"]


@pytest.mark.asyncio
async def test_foundry_runtime_ignores_done_sentinel_and_uses_fallback_message():
    events = [
        ("MESSAGE_DELTA", SimpleNamespace(text="[DONE]"), None),
        ("DONE", None, None),
    ]

    listed_messages = [
        SimpleNamespace(role="assistant", text_messages=[SimpleNamespace(text=SimpleNamespace(value="Final assistant reply"))])
    ]

    runtime = FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test",
        model_deployment_name="test-model",
        api_key="test-key",
        system_prompt="test",
        tools=[],
        agent_id="agent-123",
    )

    runtime._client = MockAgentsClient(events=events, listed_messages=listed_messages)

    chunks = []
    async for chunk in runtime.stream_message("thread-abc", "ping"):
        chunks.append(chunk)

    assert chunks == ["Final assistant reply"]


@pytest.mark.asyncio
async def test_foundry_runtime_raises_when_no_text_output_is_available():
    events = [
        ("DONE", None, None),
    ]

    runtime = FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test",
        model_deployment_name="test-model",
        api_key="test-key",
        system_prompt="test",
        tools=[],
        agent_id="agent-123",
    )

    runtime._client = MockAgentsClient(events=events, listed_messages=[])

    with pytest.raises(RuntimeError, match="without assistant text output"):
        async for _ in runtime.stream_message("thread-abc", "ping"):
            pass


@pytest.mark.asyncio
async def test_foundry_runtime_fallback_supports_async_message_listing():
    events = [
        ("RUN_STARTED", SimpleNamespace(), None),
        ("DONE", None, None),
    ]

    listed_messages = [
        SimpleNamespace(role="assistant", text_messages=[SimpleNamespace(text=SimpleNamespace(value="Async list fallback reply"))])
    ]

    runtime = FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test",
        model_deployment_name="test-model",
        api_key="test-key",
        system_prompt="test",
        tools=[],
        agent_id="agent-123",
    )

    runtime._client = MockAgentsClient(events=events, listed_messages=listed_messages, async_list=True)

    chunks = []
    async for chunk in runtime.stream_message("thread-abc", "ping"):
        chunks.append(chunk)

    assert chunks == ["Async list fallback reply"]
