namespace HomeBanking.Api.Models;

/// <summary>
/// Represents a bank account in the home banking system.
/// </summary>
public class Account
{
    /// <summary>
    /// Gets or sets the unique identifier for the account.
    /// </summary>
    public Guid Id { get; set; }

    /// <summary>
    /// Gets or sets the account number.
    /// </summary>
    public required string AccountNumber { get; set; }

    /// <summary>
    /// Gets or sets the friendly name of the account.
    /// </summary>
    public required string AccountName { get; set; }

    /// <summary>
    /// Gets or sets the type of account (Checking or Savings).
    /// </summary>
    public AccountType Type { get; set; }

    /// <summary>
    /// Gets or sets the current balance of the account.
    /// </summary>
    public decimal Balance { get; set; }

    /// <summary>
    /// Gets or sets the currency code for the account (e.g., "USD").
    /// </summary>
    public required string Currency { get; set; }

    /// <summary>
    /// Gets or sets the date and time when the account was created.
    /// </summary>
    public DateTime CreatedAt { get; set; }

    /// <summary>
    /// Gets or sets the collection of transactions associated with this account.
    /// </summary>
    public ICollection<Transaction> Transactions { get; set; } = new List<Transaction>();
}
