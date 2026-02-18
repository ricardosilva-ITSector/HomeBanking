"""
Unit tests for agent tools (API integration functions).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from httpx import Response, Request


@pytest.mark.asyncio
async def test_get_account_balances_success(sample_accounts):
    """Test successful account balance retrieval."""
    from tools import get_account_balances
    
    # Create mock response
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = sample_accounts
    mock_response.raise_for_status = MagicMock()
    
    # Mock httpx.AsyncClient
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = await get_account_balances()
        
        # Verify the result
        assert "Main Checking" in result
        assert "Savings Account" in result
        assert "$5,000.00" in result
        assert "$12,000.00" in result
        assert "1234" in result  # Last 4 digits
        assert "5678" in result  # Last 4 digits


@pytest.mark.asyncio
async def test_get_account_balances_api_error():
    """Test error handling when API returns error."""
    from tools import get_account_balances
    
    # Mock httpx.AsyncClient to raise an exception
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.HTTPStatusError(
            "500 Server Error",
            request=MagicMock(spec=Request),
            response=MagicMock(spec=Response, status_code=500)
        ))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = await get_account_balances()
        
        # Verify error is returned as string
        assert "Error" in result or "Failed" in result


@pytest.mark.asyncio
async def test_get_transactions_success(sample_transactions):
    """Test successful transaction retrieval."""
    from tools import get_transactions
    
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = sample_transactions  # Return list directly
    mock_response.raise_for_status = MagicMock()
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = await get_transactions()
        
        # Verify the result contains transaction details
        assert "Grocery Store" in result
        assert "Salary Deposit" in result
        assert "85.50" in result
        assert "3,000.00" in result


@pytest.mark.asyncio
async def test_get_transactions_with_account_id(sample_transactions):
    """Test transaction retrieval filtered by account ID."""
    from tools import get_transactions
    
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"transactions": sample_transactions, "totalCount": 3}
    mock_response.raise_for_status = MagicMock()
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = await get_transactions(account_id="acc-001")
        
        # Verify API was called with correct parameter
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "acc-001" in str(call_args)


@pytest.mark.asyncio
async def test_execute_transfer_success(sample_transfer_response):
    """Test successful transfer execution."""
    from tools import execute_transfer
    
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = sample_transfer_response
    mock_response.raise_for_status = MagicMock()
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = await execute_transfer(
            from_account_id="acc-001",
            to_account_id="acc-002",
            amount=500.00,
            description="Test transfer"
        )
        
        # Verify successful transfer message
        assert "success" in result.lower() or "completed" in result.lower()
        assert "500" in result


@pytest.mark.asyncio
async def test_execute_transfer_resolves_checking_and_savings_references(sample_transfer_response):
    """Test transfer resolves account type references to GUIDs."""
    from tools import execute_transfer

    sample_accounts = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "accountNumber": "123456",
            "accountName": "My Checking Account",
            "type": 0,
            "balance": 337.66,
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "accountNumber": "789012",
            "accountName": "My Savings Account",
            "type": 1,
            "balance": 16883.25,
        },
    ]

    mock_accounts_response = MagicMock(spec=Response)
    mock_accounts_response.status_code = 200
    mock_accounts_response.json.return_value = sample_accounts
    mock_accounts_response.raise_for_status = MagicMock()

    mock_transfer_response = MagicMock(spec=Response)
    mock_transfer_response.status_code = 200
    mock_transfer_response.json.return_value = sample_transfer_response
    mock_transfer_response.raise_for_status = MagicMock()

    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_accounts_response)
        mock_client.post = AsyncMock(return_value=mock_transfer_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await execute_transfer(
            from_account_id="checking account",
            to_account_id="savings account",
            amount=25.00,
            description="Reference-based transfer"
        )

        assert "success" in result.lower() or "completed" in result.lower()
        sent_payload = mock_client.post.call_args.kwargs["json"]
        assert sent_payload["fromAccountId"] == "11111111-1111-1111-1111-111111111111"
        assert sent_payload["toAccountId"] == "22222222-2222-2222-2222-222222222222"


@pytest.mark.asyncio
async def test_execute_transfer_resolves_last4_references(sample_transfer_response):
    """Test transfer resolves account last-4 references to GUIDs."""
    from tools import execute_transfer

    sample_accounts = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "accountNumber": "123456",
            "accountName": "My Checking Account",
            "type": 0,
            "balance": 337.66,
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "accountNumber": "789012",
            "accountName": "My Savings Account",
            "type": 1,
            "balance": 16883.25,
        },
    ]

    mock_accounts_response = MagicMock(spec=Response)
    mock_accounts_response.status_code = 200
    mock_accounts_response.json.return_value = sample_accounts
    mock_accounts_response.raise_for_status = MagicMock()

    mock_transfer_response = MagicMock(spec=Response)
    mock_transfer_response.status_code = 200
    mock_transfer_response.json.return_value = sample_transfer_response
    mock_transfer_response.raise_for_status = MagicMock()

    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_accounts_response)
        mock_client.post = AsyncMock(return_value=mock_transfer_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await execute_transfer(
            from_account_id="3456",
            to_account_id="9012",
            amount=25.00,
            description="Last4 transfer"
        )

        assert "success" in result.lower() or "completed" in result.lower()
        sent_payload = mock_client.post.call_args.kwargs["json"]
        assert sent_payload["fromAccountId"] == "11111111-1111-1111-1111-111111111111"
        assert sent_payload["toAccountId"] == "22222222-2222-2222-2222-222222222222"


@pytest.mark.asyncio
async def test_execute_transfer_normalizes_currency_amount_string(sample_transfer_response):
    """Test transfer accepts currency-formatted amount strings."""
    from tools import execute_transfer

    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = sample_transfer_response
    mock_response.raise_for_status = MagicMock()

    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await execute_transfer(
            from_account_id="9faa48b6-a3ca-4473-9804-64e9c52c5791",
            to_account_id="ec647d6c-bb99-4d32-9c37-f1dacf11fc78",
            amount="$25.00",
            description="Currency formatted amount"
        )

        assert "success" in result.lower() or "completed" in result.lower()
        sent_payload = mock_client.post.call_args.kwargs["json"]
        assert sent_payload["amount"] == 25.0


@pytest.mark.asyncio
async def test_execute_transfer_insufficient_funds():
    """Test transfer with insufficient funds error."""
    from tools import execute_transfer
    
    error_response = {
        "error": "Insufficient funds",
        "details": "Account balance is too low"
    }
    
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 400
    mock_response.json.return_value = error_response
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.HTTPStatusError(
            "400 Bad Request",
            request=MagicMock(spec=Request),
            response=mock_response
        ))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = await execute_transfer(
            from_account_id="acc-001",
            to_account_id="acc-002",
            amount=10000.00,
            description="Too much money"
        )
        
        # Verify error message is returned (contains ❌ emoji and "failed")
        assert "failed" in result.lower() or "error" in result.lower()


@pytest.mark.asyncio
async def test_get_spending_insights_success(sample_transactions):
    """Test spending insights generation."""
    from tools import get_spending_insights
    
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = sample_transactions  # Return list directly
    mock_response.raise_for_status = MagicMock()
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = await get_spending_insights()
        
        # Verify insights contain expected information
        assert "Food & Dining" in result or "category" in result.lower()


@pytest.mark.asyncio
async def test_timeout_handling():
    """Test timeout error handling."""
    from tools import get_account_balances
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = await get_account_balances()
        
        # Verify timeout error is handled gracefully
        assert "timeout" in result.lower() or "error" in result.lower()


@pytest.mark.asyncio
async def test_network_error_handling():
    """Test network error handling."""
    from tools import get_account_balances
    
    with patch('tools.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = await get_account_balances()
        
        # Verify network error is handled gracefully
        assert "error" in result.lower() or "failed" in result.lower()
