"""
Unit tests for analysis functions.
"""

import pytest
from analysis import (
    analyze_spending_by_category,
    find_largest_transactions,
    calculate_income_vs_expenses,
)


def test_analyze_spending_by_category():
    """Test spending analysis by category."""
    transactions = [
        {"amount": -100.00, "type": "Debit", "category": "Food & Dining"},
        {"amount": -50.00, "type": "Debit", "category": "Food & Dining"},
        {"amount": -200.00, "type": "Debit", "category": "Shopping"},
        {"amount": 1000.00, "type": "Credit", "category": "Income"},
    ]
    
    result = analyze_spending_by_category(transactions)
    
    # Verify categories are present
    assert "Food & Dining" in result
    assert "Shopping" in result
    assert "$150.00" in result  # Food & Dining total
    assert "$200.00" in result  # Shopping total
    
    # Verify percentages
    assert "42.9%" in result or "43%" in result  # Food & Dining percentage
    assert "57.1%" in result or "57%" in result  # Shopping percentage


def test_analyze_spending_no_debits():
    """Test spending analysis with no debit transactions."""
    transactions = [
        {"amount": 1000.00, "type": "Credit", "category": "Income"},
        {"amount": 500.00, "type": "Credit", "category": "Income"},
    ]
    
    result = analyze_spending_by_category(transactions)
    
    assert "No expenses" in result or "no debit" in result.lower()


def test_find_largest_transactions():
    """Test finding largest transactions."""
    transactions = [
        {"amount": -100.00, "description": "Grocery Store", "date": "2024-02-15"},
        {"amount": -500.00, "description": "Rent", "date": "2024-02-01"},
        {"amount": -50.00, "description": "Gas", "date": "2024-02-10"},
        {"amount": -200.00, "description": "Shopping", "date": "2024-02-12"},
        {"amount": -25.00, "description": "Coffee", "date": "2024-02-14"},
    ]
    
    result = find_largest_transactions(transactions, count=3)
    
    # Verify top 3 transactions are included
    assert "Rent" in result
    assert "$500.00" in result
    assert "Shopping" in result
    assert "$200.00" in result
    assert "Grocery Store" in result
    assert "$100.00" in result
    
    # Verify smaller transactions are not included
    assert "Coffee" not in result
    assert "$25.00" not in result


def test_find_largest_transactions_empty():
    """Test finding largest transactions with no transactions."""
    transactions = []
    
    result = find_largest_transactions(transactions, count=5)
    
    assert "No transactions" in result or "no data" in result.lower()


def test_calculate_income_vs_expenses():
    """Test income vs expenses calculation."""
    transactions = [
        {"amount": 3000.00, "type": "Credit", "category": "Salary"},
        {"amount": 500.00, "type": "Credit", "category": "Bonus"},
        {"amount": -1200.00, "type": "Debit", "category": "Rent"},
        {"amount": -300.00, "type": "Debit", "category": "Groceries"},
        {"amount": -200.00, "type": "Debit", "category": "Utilities"},
    ]
    
    result = calculate_income_vs_expenses(transactions)
    
    # Verify income and expenses are calculated correctly
    assert "$3,500.00" in result  # Total income
    assert "$1,700.00" in result  # Total expenses
    assert "$1,800.00" in result  # Net (income - expenses)
    
    # Verify savings rate
    assert "51.4%" in result or "51%" in result  # Savings rate
    
    # Verify emoji feedback for good savings
    assert "💰" in result or "Great" in result


def test_calculate_income_vs_expenses_negative():
    """Test income vs expenses with more expenses than income."""
    transactions = [
        {"amount": 1000.00, "type": "Credit", "category": "Salary"},
        {"amount": -1500.00, "type": "Debit", "category": "Shopping"},
    ]
    
    result = calculate_income_vs_expenses(transactions)
    
    # Verify negative net is shown (formatted as $-500.00)
    assert "$-500.00" in result or "-$500.00" in result
    
    # Verify warning emoji
    assert "⚠️" in result or "spending more" in result.lower()


def test_calculate_income_vs_expenses_no_transactions():
    """Test income vs expenses with no transactions."""
    transactions = []
    
    result = calculate_income_vs_expenses(transactions)
    
    assert "$0.00" in result
