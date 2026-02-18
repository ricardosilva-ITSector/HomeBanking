"""
Spending Analysis Functions

This module provides client-side analysis of transaction data for generating
financial insights.
"""

from typing import Dict, List, Any
from collections import defaultdict


def analyze_spending_by_category(transactions: List[Dict[str, Any]]) -> str:
    """Analyze spending grouped by category.
    
    Args:
        transactions: List of transaction dictionaries from API
        
    Returns:
        Formatted string with spending breakdown by category
    """
    category_totals = defaultdict(float)
    total_spending = 0
    
    # Group expenses by category
    for txn in transactions:
        amount = txn.get('amount', 0)
        if amount < 0:  # Expense (negative amount)
            category = txn.get('category', 'Uncategorized')
            category_totals[category] += abs(amount)
            total_spending += abs(amount)
    
    if total_spending == 0:
        return "No expenses found in transaction history."
    
    # Sort categories by amount (descending)
    sorted_categories = sorted(
        category_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    result = "Spending by Category:\n"
    for category, amount in sorted_categories:
        percentage = (amount / total_spending) * 100
        result += f"  • {category}: ${amount:,.2f} ({percentage:.1f}%)\n"
    
    result += f"\nTotal Expenses: ${total_spending:,.2f}"
    
    return result


def find_largest_transactions(transactions: List[Dict[str, Any]], count: int = 5) -> str:
    """Find the largest transactions by absolute amount.
    
    Args:
        transactions: List of transaction dictionaries from API
        count: Number of largest transactions to return (default: 5)
        
    Returns:
        Formatted string with largest transactions
    """
    # Sort by absolute amount (descending)
    sorted_txns = sorted(
        transactions,
        key=lambda x: abs(x.get('amount', 0)),
        reverse=True
    )[:count]
    
    if not sorted_txns:
        return "No transactions found."
    
    result = f"Top {count} Largest Transactions:\n"
    for i, txn in enumerate(sorted_txns, 1):
        date = txn.get('date', 'N/A')[:10]  # Just the date part
        desc = txn.get('description', 'No description')
        amount = txn.get('amount', 0)
        category = txn.get('category', 'Uncategorized')
        
        # Format amount with sign
        amount_str = f"+${abs(amount):,.2f}" if amount >= 0 else f"-${abs(amount):,.2f}"
        
        result += f"  {i}. {date}: {desc} - {amount_str} ({category})\n"
    
    return result.strip()


def calculate_income_vs_expenses(transactions: List[Dict[str, Any]]) -> str:
    """Calculate total income vs expenses and savings rate.
    
    Args:
        transactions: List of transaction dictionaries from API
        
    Returns:
        Formatted string with income/expense analysis
    """
    total_income = 0
    total_expenses = 0
    
    for txn in transactions:
        amount = txn.get('amount', 0)
        if amount > 0:
            total_income += amount
        else:
            total_expenses += abs(amount)
    
    net = total_income - total_expenses
    
    result = "Income vs. Expenses:\n"
    result += f"  • Total Income: ${total_income:,.2f}\n"
    result += f"  • Total Expenses: ${total_expenses:,.2f}\n"
    result += f"  • Net: ${net:,.2f}"
    
    if total_income > 0:
        savings_rate = (net / total_income) * 100
        result += f"\n  • Savings Rate: {savings_rate:.1f}%"
        
        if savings_rate > 50:
            result += " (Excellent! 💰)"
        elif savings_rate > 20:
            result += " (Good work! 👍)"
        elif savings_rate > 0:
            result += " (Room for improvement)"
        else:
            result += " (Spending more than earning ⚠️)"
    
    return result


def find_transactions_by_category(
    transactions: List[Dict[str, Any]],
    category: str
) -> List[Dict[str, Any]]:
    """Filter transactions by category.
    
    Args:
        transactions: List of transaction dictionaries from API
        category: Category name to filter by
        
    Returns:
        List of transactions matching the category
    """
    return [
        txn for txn in transactions
        if txn.get('category', '').lower() == category.lower()
    ]


def calculate_average_transaction_amount(transactions: List[Dict[str, Any]]) -> float:
    """Calculate average transaction amount (expenses only).
    
    Args:
        transactions: List of transaction dictionaries from API
        
    Returns:
        Average amount as float
    """
    expenses = [abs(txn.get('amount', 0)) for txn in transactions if txn.get('amount', 0) < 0]
    
    if not expenses:
        return 0.0
    
    return sum(expenses) / len(expenses)
