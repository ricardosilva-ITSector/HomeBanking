"""Contract tests for FastAPI server thread/message endpoints."""

from fastapi.testclient import TestClient

import server


class MockRuntime:
    def __init__(self):
        self.threads_created = 0
        self.last_thread_id = None

    async def create_thread(self) -> str:
        self.threads_created += 1
        thread_id = f"thread-{self.threads_created}"
        self.last_thread_id = thread_id
        return thread_id

    async def get_or_create_thread(self, thread_id):
        if thread_id:
            self.last_thread_id = thread_id
            return thread_id
        return await self.create_thread()

    async def stream_message(self, thread_id: str, user_input: str):
        yield f"echo:{thread_id}:{user_input}"


def test_health_degraded_when_runtime_not_initialized(monkeypatch):
    monkeypatch.setattr(server, "runtime", None)
    monkeypatch.setattr(server, "runtime_mode", "unknown")
    monkeypatch.setattr(server, "runtime_error", None)

    client = TestClient(server.app)
    response = client.get("/agent/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["agent_ready"] is False


def test_create_thread_uses_runtime(monkeypatch):
    mock_runtime = MockRuntime()
    monkeypatch.setattr(server, "runtime", mock_runtime)
    monkeypatch.setattr(server, "runtime_mode", "MockRuntime")
    monkeypatch.setattr(server, "runtime_error", None)

    client = TestClient(server.app)
    response = client.post("/agent/threads")

    assert response.status_code == 200
    payload = response.json()
    assert payload["thread_id"] == "thread-1"
    assert mock_runtime.threads_created == 1


def test_messages_endpoint_reuses_supplied_thread_id(monkeypatch):
    mock_runtime = MockRuntime()
    monkeypatch.setattr(server, "runtime", mock_runtime)
    monkeypatch.setattr(server, "runtime_mode", "MockRuntime")
    monkeypatch.setattr(server, "runtime_error", None)

    client = TestClient(server.app)
    response = client.post(
        "/agent/messages",
        json={"thread_id": "thread-existing", "input": "hello"},
    )

    assert response.status_code == 200
    body = response.text
    assert '"type": "thread", "thread_id": "thread-existing"' in body
    assert '"type": "text"' in body
    assert "echo:thread-existing:hello" in body
    assert mock_runtime.threads_created == 0


def test_messages_endpoint_creates_thread_when_missing(monkeypatch):
    mock_runtime = MockRuntime()
    monkeypatch.setattr(server, "runtime", mock_runtime)
    monkeypatch.setattr(server, "runtime_mode", "MockRuntime")
    monkeypatch.setattr(server, "runtime_error", None)

    client = TestClient(server.app)
    response = client.post(
        "/agent/messages",
        json={"input": "new thread please"},
    )

    assert response.status_code == 200
    body = response.text
    assert '"type": "thread", "thread_id": "thread-1"' in body
    assert "echo:thread-1:new thread please" in body
    assert mock_runtime.threads_created == 1
