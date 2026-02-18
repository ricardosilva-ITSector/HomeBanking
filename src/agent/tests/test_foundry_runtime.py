"""Unit tests for Foundry runtime persistence helpers."""

from pathlib import Path

from foundry_runtime import FoundryAgentsRuntime


def _build_runtime(state_file: Path, agent_id: str | None = None) -> FoundryAgentsRuntime:
    return FoundryAgentsRuntime(
        project_endpoint="https://example.services.ai.azure.com/api/projects/test-project",
        model_deployment_name="test-model",
        api_key="test-api-key",
        system_prompt="test",
        tools=[],
        agent_id=agent_id,
        state_file=str(state_file),
    )


def test_load_persisted_agent_id_returns_none_when_file_missing(tmp_path):
    state_file = tmp_path / "state.json"
    runtime = _build_runtime(state_file)

    assert runtime._load_persisted_agent_id() is None


def test_save_and_load_persisted_agent_id_roundtrip(tmp_path):
    state_file = tmp_path / "state.json"
    runtime = _build_runtime(state_file, agent_id="agent-123")

    runtime._save_persisted_agent_id()

    reloaded = _build_runtime(state_file)
    assert reloaded._load_persisted_agent_id() == "agent-123"


def test_load_persisted_agent_id_returns_none_for_invalid_json(tmp_path):
    state_file = tmp_path / "state.json"
    state_file.write_text("not-json", encoding="utf-8")

    runtime = _build_runtime(state_file)
    assert runtime._load_persisted_agent_id() is None


def test_save_persisted_agent_id_creates_parent_directory(tmp_path):
    nested_dir = tmp_path / "nested" / "runtime"
    state_file = nested_dir / "agent-state.json"

    runtime = _build_runtime(state_file, agent_id="agent-xyz")
    runtime._save_persisted_agent_id()

    assert state_file.exists()
    assert "agent-xyz" in state_file.read_text(encoding="utf-8")
