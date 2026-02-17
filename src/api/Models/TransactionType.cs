namespace HomeBanking.Api.Models;

/// <summary>
/// Represents the type of transaction.
/// </summary>
public enum TransactionType
{
    /// <summary>
    /// A debit transaction that decreases the account balance.
    /// </summary>
    Debit,

    /// <summary>
    /// A credit transaction that increases the account balance.
    /// </summary>
    Credit
}
