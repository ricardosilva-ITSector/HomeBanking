"""
Tests for HomeBanking Agent configuration.
"""
import os
import pytest
from unittest.mock import patch
from config import AgentConfig


@pytest.fixture(autouse=True)
def reset_env():
    """Reset environment variables before each test."""
    # Store original values
    original_env = os.environ.copy()
    
    # Clear agent-related env vars
    for key in list(os.environ.keys()):
        if key.startswith(("FOUNDRY_", "HOMEBANKING_", "AGENT_", "LOG_")):
            os.environ.pop(key, None)
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


def test_config_validation_requires_endpoint():
    """Test that configuration validation requires Foundry endpoint."""
    os.environ.pop("FOUNDRY_PROJECT_ENDPOINT", None)
    os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"] = "test-model"
    os.environ["HOMEBANKING_API_BASE_URL"] = "http://localhost:5091"
    
    with pytest.raises(ValueError, match="FOUNDRY_PROJECT_ENDPOINT"):
        AgentConfig.from_env()


def test_config_validation_requires_model():
    """Test that configuration validation requires model deployment name."""
    os.environ["FOUNDRY_PROJECT_ENDPOINT"] = "https://test.ai.azure.com"
    os.environ.pop("FOUNDRY_MODEL_DEPLOYMENT_NAME", None)
    os.environ["HOMEBANKING_API_BASE_URL"] = "http://localhost:5091"
    
    with pytest.raises(ValueError, match="FOUNDRY_MODEL_DEPLOYMENT_NAME"):
        AgentConfig.from_env()


def test_config_validation_requires_api_url():
    """Test that configuration validation requires API base URL."""
    os.environ["FOUNDRY_PROJECT_ENDPOINT"] = "https://test.ai.azure.com"
    os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"] = "test-model"
    os.environ.pop("HOMEBANKING_API_BASE_URL", None)
    
    with pytest.raises(ValueError, match="HOMEBANKING_API_BASE_URL"):
        AgentConfig.from_env()


def test_config_validation_https_endpoint():
    """Test that configuration validates HTTPS endpoint."""
    config = AgentConfig(
        foundry_project_endpoint="http://test.ai.azure.com",  # HTTP not HTTPS
        foundry_model_deployment_name="test-model",
        homebanking_api_base_url="http://localhost:5091",
        homebanking_api_key=None,
        server_host="127.0.0.1",
        server_port=8087,
        log_level="INFO"
    )
    
    with pytest.raises(ValueError, match="HTTPS"):
        config.validate()


def test_config_validation_port_range():
    """Test that configuration validates port range."""
    config = AgentConfig(
        foundry_project_endpoint="https://test.ai.azure.com",
        foundry_model_deployment_name="test-model",
        homebanking_api_base_url="http://localhost:5091",
        homebanking_api_key=None,
        server_host="127.0.0.1",
        server_port=99999,  # Invalid port
        log_level="INFO"
    )
    
    with pytest.raises(ValueError, match="between 1 and 65535"):
        config.validate()


def test_config_from_env_with_defaults():
    """Test configuration loading with default values."""
    os.environ["FOUNDRY_PROJECT_ENDPOINT"] = "https://test.ai.azure.com"
    os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"] = "gpt-4o"
    os.environ["HOMEBANKING_API_BASE_URL"] = "http://localhost:5091"
    os.environ.pop("HOMEBANKING_API_KEY", None)
    os.environ.pop("AGENT_SERVER_HOST", None)
    os.environ.pop("AGENT_SERVER_PORT", None)
    
    config = AgentConfig.from_env()
    
    assert config.foundry_project_endpoint == "https://test.ai.azure.com"
    assert config.foundry_model_deployment_name == "gpt-4o"
    assert config.homebanking_api_base_url == "http://localhost:5091"
    assert config.homebanking_api_key is None
    assert config.server_host == "127.0.0.1"
    assert config.server_port == 8087
    assert config.log_level == "INFO"


def test_config_from_env_with_custom_values():
    """Test configuration loading with custom values."""
    os.environ["FOUNDRY_PROJECT_ENDPOINT"] = "https://custom.ai.azure.com"
    os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"] = "gpt-4.1"
    os.environ["HOMEBANKING_API_BASE_URL"] = "https://api.example.com"
    # Note: API key is optional, testing without it for MVP
    # os.environ["HOMEBANKING_API_KEY"] = "secret-key-123"
    os.environ["AGENT_SERVER_HOST"] = "0.0.0.0"
    os.environ["AGENT_SERVER_PORT"] = "9000"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    config = AgentConfig.from_env()
    
    assert config.foundry_project_endpoint == "https://custom.ai.azure.com"
    assert config.foundry_model_deployment_name == "gpt-4.1"
    assert config.homebanking_api_base_url == "https://api.example.com"
    assert config.homebanking_api_key is None  # Optional for MVP
    assert config.server_host == "0.0.0.0"
    assert config.server_port == 9000
    assert config.log_level == "DEBUG"
