"""
Pytest configuration and shared fixtures.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for testing tools without calling real API."""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


@pytest.fixture
def sample_accounts():
    """Sample account data for testing - matches actual API response format."""
    return [
        {
            "id": "acc-001",
            "accountNumber": "****1234",
            "name": "Main Checking",
            "accountType": "Checking",
            "balance": 5000.00,
            "currency": "USD",
            "createdAt": "2024-01-01T00:00:00Z"
        },
        {
            "id": "acc-002",
            "accountNumber": "****5678",
            "name": "Savings Account",
            "accountType": "Savings",
            "balance": 12000.00,
            "currency": "USD",
            "createdAt": "2024-01-01T00:00:00Z"
        }
    ]


@pytest.fixture
def sample_transactions():
    """Sample transaction data for testing - matches actual API response format."""
    return [
        {
            "id": "txn-001",
            "accountId": "acc-001",
            "timestamp": "2024-02-15T10:30:00Z",
            "description": "Grocery Store",
            "amount": -85.50,
            "transactionType": "Debit",
            "category": "Food & Dining",
            "balance": 4914.50
        },
        {
            "id": "txn-002",
            "accountId": "acc-001",
            "timestamp": "2024-02-14T14:20:00Z",
            "description": "Salary Deposit",
            "amount": 3000.00,
            "transactionType": "Credit",
            "category": "Income",
            "balance": 5000.00
        },
        {
            "id": "txn-003",
            "accountId": "acc-001",
            "timestamp": "2024-02-13T08:15:00Z",
            "description": "Coffee Shop",
            "amount": -12.50,
            "transactionType": "Debit",
            "category": "Food & Dining",
            "balance": 2000.00
        }
    ]


@pytest.fixture
def sample_transfer_request():
    """Sample transfer request data."""
    return {
        "fromAccountId": "acc-001",
        "toAccountId": "acc-002",
        "amount": 500.00,
        "description": "Transfer to savings"
    }


@pytest.fixture
def sample_transfer_response():
    """Sample transfer response data."""
    return {
        "success": True,
        "message": "Transfer completed successfully",
        "transactionId": "txn-transfer-001",
        "timestamp": "2024-02-18T12:00:00Z"
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("BACKEND_API_URL", "http://localhost:5091")
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://test-foundry.azure.com")
    monkeypatch.setenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "test-model")
    monkeypatch.setenv("FOUNDRY_API_KEY", "test-api-key")
    monkeypatch.setenv("AGENT_PORT", "8087")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
