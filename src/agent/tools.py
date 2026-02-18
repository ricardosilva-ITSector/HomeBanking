"""
Tool definitions for HomeBanking Agent.
These tools wrap existing HomeBanking API endpoints.
"""
import httpx
import structlog
from typing import Optional
from uuid import UUID

logger = structlog.get_logger(__name__)


class HomeBankingTools:
    """Tools that call the HomeBanking .NET API."""
    
    def __init__(self, api_base_url: str, api_key: Optional[str] = None):
        """
        Initialize HomeBanking tools.
        
        Args:
            api_base_url: Base URL for the HomeBanking API
            api_key: Optional API key for authentication
        """
        self.api_base_url = api_base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.api_base_url,
            timeout=10.0,
            headers=self._get_headers()
        )
    
    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def list_accounts(self) -> str:
        """
        Retrieves all user bank accounts with balances.
        
        Returns:
            JSON string with account information including account names, numbers, types, and balances.
        """
        try:
            logger.info("Calling list_accounts tool")
            response = await self.client.get("/api/accounts")
            response.raise_for_status()
            accounts = response.json()
            logger.info("Successfully retrieved accounts", count=len(accounts))
            return response.text
        except httpx.HTTPError as e:
            logger.error("Error calling list accounts API", error=str(e))
            return f'{{"error": "Failed to retrieve accounts: {str(e)}"}}'
    
    async def list_transactions(
        self, 
        account_id: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> str:
        """
        Retrieves transaction history with optional filtering and pagination.
        
        Args:
            account_id: Optional account ID (GUID) to filter transactions for a specific account.
            limit: Maximum number of transactions to return (default 100, max 500).
            offset: Number of transactions to skip for pagination (default 0).
        
        Returns:
            JSON string with transaction history including dates, amounts, categories, and balances.
        """
        try:
            logger.info(
                "Calling list_transactions tool", 
                account_id=account_id, 
                limit=limit, 
                offset=offset
            )
            
            params = {"limit": limit, "offset": offset}
            if account_id:
                # Validate GUID format
                try:
                    UUID(account_id)
                    params["accountId"] = account_id
                except ValueError:
                    return f'{{"error": "Invalid account ID format. Must be a valid GUID."}}'
            
            response = await self.client.get("/api/transactions", params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(
                "Successfully retrieved transactions", 
                total_count=data.get("totalCount", 0),
                returned=len(data.get("transactions", []))
            )
            return response.text
        except httpx.HTTPError as e:
            logger.error("Error calling list transactions API", error=str(e))
            return f'{{"error": "Failed to retrieve transactions: {str(e)}"}}'
    
    async def create_transfer(
        self, 
        from_account_id: str, 
        to_account_id: str, 
        amount: float, 
        description: Optional[str] = None
    ) -> str:
        """
        Creates a transfer between two accounts.
        WARNING: This function should ONLY be called after explicit user confirmation.
        
        Args:
            from_account_id: Source account ID (GUID).
            to_account_id: Destination account ID (GUID).
            amount: Amount to transfer (must be positive, max 2 decimal places).
            description: Optional description for the transfer.
        
        Returns:
            JSON string with transfer result including transaction IDs on success, or error message on failure.
        """
        try:
            # Validate GUIDs
            try:
                UUID(from_account_id)
                UUID(to_account_id)
            except ValueError:
                return f'{{"error": "Invalid account ID format. Must be valid GUIDs."}}'
            
            # Validate amount
            if amount <= 0:
                return f'{{"error": "Amount must be positive"}}'
            if amount > 10000:
                return f'{{"error": "Amount exceeds maximum transfer limit of $10,000"}}'
            
            logger.warning(
                "EXECUTING TRANSFER", 
                from_account=from_account_id, 
                to_account=to_account_id, 
                amount=amount
            )
            
            payload = {
                "fromAccountId": from_account_id,
                "toAccountId": to_account_id,
                "amount": amount,
                "description": description
            }
            
            response = await self.client.post("/api/transfers", json=payload)
            
            if response.status_code == 201:
                result = response.json()
                logger.info(
                    "Transfer successful", 
                    debit_tx_id=result.get("debitTransactionId"),
                    credit_tx_id=result.get("creditTransactionId")
                )
                return response.text
            elif response.status_code == 400:
                # Validation error from API
                error_data = response.json()
                logger.warning("Transfer validation failed", error=error_data.get("error"))
                return response.text
            else:
                response.raise_for_status()
                return response.text
                
        except httpx.HTTPError as e:
            logger.error("Error calling create transfer API", error=str(e))
            return f'{{"error": "Failed to execute transfer: {str(e)}"}}'
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Function definitions for the agent
# These will be registered with the agent to describe available tools

def get_user_functions():
    """
    Returns the set of user-defined functions that the agent can call.
    These must be instantiated with a HomeBankingTools instance.
    """
    # This will be populated in main.py after instantiating HomeBankingTools
    pass
