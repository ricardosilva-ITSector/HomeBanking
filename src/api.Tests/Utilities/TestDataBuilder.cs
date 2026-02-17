using HomeBanking.Api.Models;

namespace HomeBanking.Api.Tests.Utilities;

/// <summary>
/// Builder class for creating test data.
/// </summary>
public static class TestDataBuilder
{
    /// <summary>
    /// Creates a collection of sample accounts for testing.
    /// </summary>
    /// <returns>A list of Account entities with test data.</returns>
    public static List<Account> CreateSampleAccounts()
    {
        return new List<Account>
        {
            new Account
            {
                Id = Guid.Parse("11111111-1111-1111-1111-111111111111"),
                AccountNumber = "ACC-001",
                AccountName = "Primary Checking",
                Type = AccountType.Checking,
                Balance = 5000.00m,
                Currency = "USD",
                CreatedAt = DateTime.UtcNow.AddMonths(-12),
                Transactions = new List<Transaction>()
            },
            new Account
            {
                Id = Guid.Parse("22222222-2222-2222-2222-222222222222"),
                AccountNumber = "ACC-002",
                AccountName = "Savings Account",
                Type = AccountType.Savings,
                Balance = 10000.00m,
                Currency = "USD",
                CreatedAt = DateTime.UtcNow.AddMonths(-6),
                Transactions = new List<Transaction>()
            },
            new Account
            {
                Id = Guid.Parse("33333333-3333-3333-3333-333333333333"),
                AccountNumber = "ACC-003",
                AccountName = "Emergency Fund",
                Type = AccountType.Savings,
                Balance = 100.00m,
                Currency = "USD",
                CreatedAt = DateTime.UtcNow.AddMonths(-3),
                Transactions = new List<Transaction>()
            }
        };
    }

    /// <summary>
    /// Creates a single account with specified balance.
    /// </summary>
    /// <param name="balance">The initial balance for the account.</param>
    /// <returns>An Account entity with the specified balance.</returns>
    public static Account CreateAccount(decimal balance = 1000.00m)
    {
        return new Account
        {
            Id = Guid.NewGuid(),
            AccountNumber = $"ACC-{Guid.NewGuid().ToString().Substring(0, 8)}",
            AccountName = "Test Account",
            Type = AccountType.Checking,
            Balance = balance,
            Currency = "USD",
            CreatedAt = DateTime.UtcNow,
            Transactions = new List<Transaction>()
        };
    }

    /// <summary>
    /// Creates a sample transaction.
    /// </summary>
    /// <param name="accountId">The account ID for the transaction.</param>
    /// <param name="amount">The transaction amount.</param>
    /// <param name="type">The transaction type.</param>
    /// <returns>A Transaction entity with test data.</returns>
    public static Transaction CreateTransaction(
        Guid accountId,
        decimal amount,
        TransactionType type = TransactionType.Debit)
    {
        return new Transaction
        {
            Id = Guid.NewGuid(),
            AccountId = accountId,
            Date = DateTime.UtcNow,
            Description = "Test Transaction",
            Amount = amount,
            Type = type,
            Category = type == TransactionType.Debit ? "Transfer" : "Income",
            BalanceAfter = 0m // Will be calculated in actual scenarios
        };
    }

    /// <summary>
    /// Creates a collection of sample transactions for testing.
    /// </summary>
    /// <param name="accountId">The account ID for the transactions.</param>
    /// <param name="count">Number of transactions to create.</param>
    /// <returns>A list of Transaction entities with test data.</returns>
    public static List<Transaction> CreateSampleTransactions(Guid accountId, int count = 5)
    {
        var transactions = new List<Transaction>();
        var baseDate = DateTime.UtcNow.AddDays(-count);

        for (int i = 0; i < count; i++)
        {
            transactions.Add(new Transaction
            {
                Id = Guid.NewGuid(),
                AccountId = accountId,
                Date = baseDate.AddDays(i),
                Description = $"Test Transaction {i + 1}",
                Amount = (i + 1) * 10.00m,
                Type = i % 2 == 0 ? TransactionType.Debit : TransactionType.Credit,
                Category = i % 2 == 0 ? "Transfer" : "Income",
                BalanceAfter = 1000.00m + ((i + 1) * 10.00m)
            });
        }

        return transactions;
    }
}
