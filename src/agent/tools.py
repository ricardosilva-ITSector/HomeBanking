"""
API Integration Tools

This module provides tools for the banking agent to interact with the .NET backend API.
"""

import httpx
import os
from typing import Annotated, Optional
import logging
import re

logger = logging.getLogger(__name__)

# Get backend API URL from environment
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:5091")

# Configure httpx timeout (30 seconds)
TIMEOUT = httpx.Timeout(30.0)


GUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def _requires_resolution(identifier: str) -> bool:
    value = identifier.strip().lower()
    if GUID_PATTERN.match(value):
        return False

    if value in {"checking", "savings", "checking account", "savings account"}:
        return True

    if "ending in" in value:
        return True

    if value.isdigit() and len(value) <= 4:
        return True

    if "account" in value and any(c.isalpha() for c in value):
        return True

    return False


def _resolve_account_id(identifier: str, accounts: list[dict]) -> str:
    value = identifier.strip()
    value_lower = value.lower()

    if GUID_PATTERN.match(value):
        return value

    for account in accounts:
        account_id = account.get("id")
        if account_id and str(account_id).lower() == value_lower:
            return str(account_id)

    if "checking" in value_lower:
        for account in accounts:
            account_type = account.get("type")
            if account_type == 0:
                return str(account.get("id"))

    if "savings" in value_lower:
        for account in accounts:
            account_type = account.get("type")
            if account_type == 1:
                return str(account.get("id"))

    digits = "".join(ch for ch in value if ch.isdigit())
    if digits:
        suffix = digits[-4:]
        for account in accounts:
            account_number = str(account.get("accountNumber", ""))
            if account_number.endswith(suffix):
                return str(account.get("id"))

    for account in accounts:
        account_name = str(account.get("accountName", "")).lower()
        if account_name and account_name in value_lower:
            return str(account.get("id"))

    raise ValueError(f"Could not resolve account reference '{identifier}' to a valid account id")


def _normalize_amount(value: float | str) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    raw = str(value).strip()
    cleaned = re.sub(r"[^0-9.\-]", "", raw)
    if cleaned.count(".") > 1:
        first_dot = cleaned.find(".")
        cleaned = cleaned[: first_dot + 1] + cleaned[first_dot + 1 :].replace(".", "")

    if cleaned in {"", ".", "-", "-."}:
        raise ValueError(f"Invalid amount value: {value}")

    return float(cleaned)


async def get_account_balances() -> str:
    """Get current balances for all user accounts.
    
    Returns:
        Formatted string with account balances, or error message if API call fails.
    """
    print("🔧 get_account_balances() CALLED!")
    logger.info("get_account_balances() called")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BACKEND_URL}/api/accounts")
            response.raise_for_status()
            accounts = response.json()
            
            # Handle both list and dict responses
            if isinstance(accounts, dict):
                accounts = accounts.get('value', [])
            
            if not accounts:
                return "No accounts found."
            
            # Map account type enum values
            account_types = {0: "Checking", 1: "Savings"}
            
            result = "Account Balances:\n"
            for acc in accounts:
                # Mask account number (show last 4 digits)
                acc_num_masked = acc['accountNumber'][-4:] if len(acc['accountNumber']) >= 4 else acc['accountNumber']
                acc_name = acc.get('accountName', 'Unknown Account')
                acc_type = account_types.get(acc.get('type', 0), 'Unknown')
                result += f"- {acc_name} (ending in {acc_num_masked}): ${acc['balance']:,.2f}\n"
                result += f"  Type: {acc_type}\n"
            
            return result.strip()
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching accounts: {e}")
        return f"Error fetching account balances: API returned status {e.response.status_code}"
    except httpx.TimeoutException:
        logger.error("Timeout fetching accounts")
        return "Error fetching account balances: Request timed out. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error fetching accounts: {e}")
        return f"Error fetching account balances: {str(e)}"


async def get_transactions(
    account_id: Annotated[Optional[str], "Optional account ID (GUID) to filter transactions"] = None
) -> str:
    """Get transaction history, optionally filtered by account.
    
    Args:
        account_id: Optional GUID of account to filter transactions by.
    
    Returns:
        Formatted string with transaction history, or error message if API call fails.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            url = f"{BACKEND_URL}/api/transactions"
            params = {}
            if account_id:
                params["accountId"] = account_id
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Handle both dict and list responses
            if isinstance(data, dict):
                transactions = data.get('transactions', [])
                total_count = data.get('totalCount', len(transactions))
            else:
                transactions = data
                total_count = len(transactions)
            
            if not transactions:
                return "No transactions found."
            
            # Sort by date (newest first)
            transactions_sorted = sorted(
                transactions,
                key=lambda x: x.get('date', ''),
                reverse=True
            )
            
            # Limit to most recent 20 transactions for brevity
            limit = 20
            recent_txns = transactions_sorted[:limit]
            
            result = f"Transaction History ({total_count} total transactions"
            if account_id:
                result += f", filtered by account"
            result += f", showing {len(recent_txns)} most recent):\n\n"
            
            # Map transaction type enum values
            txn_types = {0: "Debit", 1: "Credit"}
            
            for txn in recent_txns:
                date = txn.get('date', 'N/A')
                desc = txn.get('description', 'No description')
                amount = txn.get('amount', 0)
                category = txn.get('category', 'Uncategorized')
                txn_type = txn_types.get(txn.get('type', 0), 'Unknown')
                balance_after = txn.get('balanceAfter', 0)
                
                # Format amount with + or - sign
                amount_str = f"+${abs(amount):,.2f}" if amount >= 0 else f"-${abs(amount):,.2f}"
                
                result += f"• {date[:10]}: {desc}\n"
                result += f"  Amount: {amount_str} | Category: {category} | Type: {txn_type}\n"
                result += f"  Balance after: ${balance_after:,.2f}\n\n"
            
            if total_count > limit:
                result += f"... and {total_count - limit} more transactions\n"
            
            return result.strip()
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching transactions: {e}")
        return f"Error fetching transactions: API returned status {e.response.status_code}"
    except httpx.TimeoutException:
        logger.error("Timeout fetching transactions")
        return "Error fetching transactions: Request timed out. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error fetching transactions: {e}")
        return f"Error fetching transactions: {str(e)}"


async def execute_transfer(
    from_account_id: Annotated[str, "Source account reference (GUID, account name, type, or last 4 digits)"],
    to_account_id: Annotated[str, "Destination account reference (GUID, account name, type, or last 4 digits)"],
    amount: Annotated[float | str, "Transfer amount in dollars (numeric value, e.g., 25 or '$25')"],
    description: Annotated[str, "Transfer description"] = "Transfer via AI Agent"
) -> str:
    """Execute a transfer between accounts.
    
    IMPORTANT: This tool should ONLY be called after explicit user confirmation.
    The agent MUST present transfer details and ask for confirmation before calling this tool.
    
    Args:
        from_account_id: GUID of source account
        to_account_id: GUID of destination account  
        amount: Amount to transfer (positive number)
        description: Optional description for the transfer
    
    Returns:
        Success message with transaction IDs, or error message if transfer fails.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resolved_from_account_id = from_account_id
            resolved_to_account_id = to_account_id
            normalized_amount = _normalize_amount(amount)

            if _requires_resolution(from_account_id) or _requires_resolution(to_account_id):
                accounts_response = await client.get(f"{BACKEND_URL}/api/accounts")
                accounts_response.raise_for_status()
                accounts_data = accounts_response.json()
                accounts = accounts_data.get("value", []) if isinstance(accounts_data, dict) else accounts_data

                resolved_from_account_id = _resolve_account_id(from_account_id, accounts)
                resolved_to_account_id = _resolve_account_id(to_account_id, accounts)

            payload = {
                "fromAccountId": resolved_from_account_id,
                "toAccountId": resolved_to_account_id,
                "amount": normalized_amount,
                "description": description
            }
            
            logger.info(
                f"Executing transfer: ${normalized_amount} from {resolved_from_account_id[:8]}... to {resolved_to_account_id[:8]}..."
            )
            
            response = await client.post(
                f"{BACKEND_URL}/api/transfers",
                json=payload
            )
            
            if response.is_success:
                result = response.json()
                debit_id = result.get('debitTransactionId', 'N/A')
                credit_id = result.get('creditTransactionId', 'N/A')
                
                return (
                    f"✅ Transfer successful!\n\n"
                    f"Amount: ${normalized_amount:,.2f}\n"
                    f"Description: {description}\n"
                    f"Transaction IDs:\n"
                    f"  - Debit: {debit_id[:8]}...\n"
                    f"  - Credit: {credit_id[:8]}...\n"
                )
            else:
                # Parse error response
                try:
                    error = response.json()
                    error_msg = error.get('title', 'Unknown error')
                    details = error.get('detail', '') or str(error)
                    return f"❌ Transfer failed: {error_msg}\n{details}"
                except:
                    return f"❌ Transfer failed: API returned status {response.status_code}"
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error executing transfer: {e}")
        return f"❌ Transfer failed: API returned status {e.response.status_code}"
    except httpx.TimeoutException:
        logger.error("Timeout executing transfer")
        return "❌ Transfer failed: Request timed out. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error executing transfer: {e}")
        return f"❌ Transfer failed: {str(e)}"


async def get_spending_insights() -> str:
    """Get spending insights and analysis based on transaction history.
    
    Returns:
        Formatted analysis of spending patterns, or error message if analysis fails.
    """
    try:
        # First, get all transactions
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BACKEND_URL}/api/transactions")
            response.raise_for_status()
            data = response.json()
            
            # Handle both dict and list responses
            if isinstance(data, dict):
                transactions = data.get('transactions', [])
            else:
                transactions = data
        
        if not transactions:
            return "No transactions available for analysis."
        
        # Import analysis module
        try:
            from analysis import analyze_spending_by_category, find_largest_transactions, calculate_income_vs_expenses
            
            # Run analysis
            category_analysis = analyze_spending_by_category(transactions)
            largest_txns = find_largest_transactions(transactions, count=5)
            income_expenses = calculate_income_vs_expenses(transactions)
            
            result = "📊 Spending Insights:\n\n"
            result += category_analysis + "\n\n"
            result += income_expenses + "\n\n"
            result += largest_txns
            
            return result
        
        except ImportError:
            # Fallback: simple analysis without analysis module
            expenses = [t for t in transactions if t.get('amount', 0) < 0]
            income = [t for t in transactions if t.get('amount', 0) > 0]
            
            total_expenses = sum(abs(t.get('amount', 0)) for t in expenses)
            total_income = sum(t.get('amount', 0) for t in income)
            
            result = "📊 Basic Spending Insights:\n\n"
            result += f"Total Expenses: ${total_expenses:,.2f} ({len(expenses)} transactions)\n"
            result += f"Total Income: ${total_income:,.2f} ({len(income)} transactions)\n"
            result += f"Net: ${total_income - total_expenses:,.2f}"
            
            return result
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching transactions for insights: {e}")
        return f"Error generating insights: API returned status {e.response.status_code}"
    except httpx.TimeoutException:
        logger.error("Timeout fetching transactions for insights")
        return "Error generating insights: Request timed out. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error generating insights: {e}")
        return f"Error generating insights: {str(e)}"
