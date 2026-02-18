"""
Integration tests for the agent system.
These tests verify end-to-end functionality with mocked external services.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx


@pytest.mark.asyncio
async def test_agent_workflow_account_inquiry(sample_accounts):
    """Test complete workflow: user asks for account balances."""
    from tools import get_account_balances
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_accounts
    mock_response.raise_for_status = MagicMock()
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        # Simulate user asking for account balances
        result = await get_account_balances()
        
        # Verify the agent can provide useful information
        assert result is not None
        assert len(result) > 0
        assert "Checking" in result or "Savings" in result


@pytest.mark.asyncio
async def test_agent_workflow_spending_analysis(sample_transactions):
    """Test complete workflow: user asks for spending insights."""
    from tools import get_spending_insights
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_transactions  # Return list directly
    mock_response.raise_for_status = MagicMock()
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        # Simulate user asking for spending insights
        result = await get_spending_insights()
        
        # Verify insights are comprehensive
        assert result is not None
        assert len(result) > 50  # Should be a detailed response


@pytest.mark.asyncio
async def test_agent_workflow_transfer_execution(sample_transfer_response):
    """Test complete workflow: user requests a transfer."""
    from tools import execute_transfer
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_transfer_response
    mock_response.raise_for_status = MagicMock()
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        # Simulate user confirming a transfer
        result = await execute_transfer(
            from_account_id="acc-001",
            to_account_id="acc-002",
            amount=100.00,
            description="Test transfer"
        )
        
        # Verify transfer was processed
        assert "success" in result.lower() or "completed" in result.lower()


@pytest.mark.asyncio
async def test_error_recovery_sequence():
    """Test that agent can recover from API errors."""
    from tools import get_account_balances, get_transactions
    
    # First call fails
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result1 = await get_account_balances()
        assert "error" in result1.lower() or "failed" in result1.lower()
    
    # Second call succeeds
    sample_data = [{"id": "acc-001", "name": "Test", "accountType": "Checking", "balance": 1000, "accountNumber": "123456789"}]
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_data
    mock_response.raise_for_status = MagicMock()
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result2 = await get_account_balances()
        assert "Test" in result2


@pytest.mark.asyncio
async def test_concurrent_tool_calls(sample_accounts, sample_transactions):
    """Test that multiple tools can be called concurrently."""
    import asyncio
    from tools import get_account_balances, get_transactions
    
    # Mock accounts response
    mock_accounts_response = MagicMock()
    mock_accounts_response.status_code = 200
    mock_accounts_response.json.return_value = sample_accounts
    mock_accounts_response.raise_for_status = MagicMock()
    
    # Mock transactions response
    mock_transactions_response = MagicMock()
    mock_transactions_response.status_code = 200
    mock_transactions_response.json.return_value = sample_transactions  # Return list directly
    mock_transactions_response.raise_for_status = MagicMock()
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        
        # Setup different responses for different endpoints
        async def mock_get(url, **kwargs):
            if "accounts" in str(url):
                return mock_accounts_response
            else:
                return mock_transactions_response
        
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        #Call both tools concurrently
        results = await asyncio.gather(
            get_account_balances(),
            get_transactions()
        )
        
        # Verify both succeeded
        assert len(results) == 2
        assert "Checking" in results[0] or "Savings" in results[0]
        assert "Grocery" in results[1] or "transaction" in results[1].lower()


def test_environment_configuration(setup_test_environment):
    """Test that environment variables are properly configured."""
    import os
    
    assert os.getenv("BACKEND_API_URL") == "http://localhost:5091"
    assert os.getenv("FOUNDRY_PROJECT_ENDPOINT") is not None
    assert os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME") is not None
    assert os.getenv("AGENT_PORT") == "8087"


@pytest.mark.asyncio
async def test_api_error_messages_are_user_friendly():
    """Test that API errors are converted to user-friendly messages."""
    from tools import execute_transfer
    
    # Mock a 400 error with detailed message
    error_response = {
        "error": "ValidationError",
        "details": "Amount must be positive"
    }
    
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = error_response
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.HTTPStatusError(
            "400 Bad Request",
            request=MagicMock(),
            response=mock_response
        ))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = await execute_transfer(
            from_account_id="acc-001",
            to_account_id="acc-002",
            amount=-100.00,
            description="Invalid amount"
        )
        
        # Error message should be user-friendly (contains "failed" or status code)
        assert "failed" in result.lower() or "400" in result
