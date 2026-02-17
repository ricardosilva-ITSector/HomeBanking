namespace HomeBanking.Api.Models;

/// <summary>
/// Represents a financial transaction in the home banking system.
/// </summary>
public class Transaction
{
    /// <summary>
    /// Gets or sets the unique identifier for the transaction.
    /// </summary>
    public Guid Id { get; set; }

    /// <summary>
    /// Gets or sets the account identifier this transaction belongs to.
    /// </summary>
    public Guid AccountId { get; set; }

    /// <summary>
    /// Gets or sets the date and time when the transaction occurred.
    /// </summary>
    public DateTime Date { get; set; }

    /// <summary>
    /// Gets or sets the description of the transaction.
    /// </summary>
    public required string Description { get; set; }

    /// <summary>
    /// Gets or sets the transaction amount.
    /// </summary>
    public decimal Amount { get; set; }

    /// <summary>
    /// Gets or sets the type of transaction (Debit or Credit).
    /// </summary>
    public TransactionType Type { get; set; }

    /// <summary>
    /// Gets or sets the category of the transaction (e.g., "Groceries", "Salary").
    /// </summary>
    public required string Category { get; set; }

    /// <summary>
    /// Gets or sets the account balance after this transaction was processed.
    /// </summary>
    public decimal BalanceAfter { get; set; }

    /// <summary>
    /// Gets or sets the account this transaction belongs to.
    /// </summary>
    public Account? Account { get; set; }
}
