"""
Configuration management for HomeBanking Agent Service.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (override=True for deployed environments)
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file, override=True)


@dataclass
class AgentConfig:
    """Agent service configuration."""
    
    # Foundry configuration
    foundry_project_endpoint: str
    foundry_model_deployment_name: str
    
    # HomeBanking API configuration
    homebanking_api_base_url: str
    homebanking_api_key: str | None
    
    # Server configuration
    server_host: str
    server_port: int
    
    # Logging
    log_level: str
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        
        # Required variables
        foundry_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
        model_deployment = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME")
        api_base_url = os.getenv("HOMEBANKING_API_BASE_URL")
        
        if not foundry_endpoint:
            raise ValueError("FOUNDRY_PROJECT_ENDPOINT environment variable is required")
        if not model_deployment:
            raise ValueError("FOUNDRY_MODEL_DEPLOYMENT_NAME environment variable is required")
        if not api_base_url:
            raise ValueError("HOMEBANKING_API_BASE_URL environment variable is required")
        
        # Optional variables with defaults
        api_key = os.getenv("HOMEBANKING_API_KEY")
        server_host = os.getenv("AGENT_SERVER_HOST", "127.0.0.1")
        server_port = int(os.getenv("AGENT_SERVER_PORT", "8087"))
        log_level = os.getenv("LOG_LEVEL", "INFO")
        
        return cls(
            foundry_project_endpoint=foundry_endpoint,
            foundry_model_deployment_name=model_deployment,
            homebanking_api_base_url=api_base_url,
            homebanking_api_key=api_key,
            server_host=server_host,
            server_port=server_port,
            log_level=log_level,
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not self.foundry_project_endpoint.startswith("https://"):
            raise ValueError("FOUNDRY_PROJECT_ENDPOINT must be an HTTPS URL")
        
        if self.server_port < 1 or self.server_port > 65535:
            raise ValueError("AGENT_SERVER_PORT must be between 1 and 65535")
