using HomeBanking.Api.Data;
using HomeBanking.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace HomeBanking.Api.Services;

/// <summary>
/// Service for handling money transfers between accounts.
/// </summary>
public class TransferService : ITransferService
{
    private readonly HomeBankingDbContext _context;
    private const decimal MinTransferAmount = 0.01m;
    private const decimal MaxTransferAmount = 10000.00m;
    private const int MaxDescriptionLength = 200;

    /// <summary>
    /// Initializes a new instance of the <see cref="TransferService"/> class.
    /// </summary>
    /// <param name="context">The database context.</param>
    public TransferService(HomeBankingDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    /// <summary>
    /// Executes a transfer between two accounts.
    /// </summary>
    /// <param name="fromAccountId">The source account identifier.</param>
    /// <param name="toAccountId">The destination account identifier.</param>
    /// <param name="amount">The amount to transfer.</param>
    /// <param name="description">Optional description of the transfer.</param>
    /// <returns>A transfer result indicating success or failure with details.</returns>
    public async Task<TransferResult> ExecuteTransferAsync(
        Guid fromAccountId,
        Guid toAccountId,
        decimal amount,
        string? description = null)
    {
        // VR-003: Prevent self-transfer
        if (fromAccountId == toAccountId)
        {
            return TransferResult.CreateFailure("Cannot transfer to the same account.");
        }

        // VR-001: Validate amount within limits
        if (amount < MinTransferAmount)
        {
            return TransferResult.CreateFailure($"Transfer amount must be at least ${MinTransferAmount:F2}.");
        }

        if (amount > MaxTransferAmount)
        {
            return TransferResult.CreateFailure($"Transfer amount cannot exceed ${MaxTransferAmount:F2}.");
        }

        // VR-001: Validate amount has max 2 decimal places
        if (decimal.Round(amount, 2) != amount)
        {
            return TransferResult.CreateFailure("Transfer amount cannot have more than 2 decimal places.");
        }

        // VR-004: Validate description length
        if (description != null && description.Length > MaxDescriptionLength)
        {
            return TransferResult.CreateFailure($"Description cannot exceed {MaxDescriptionLength} characters.");
        }

        // VR-003: Validate both accounts exist
        var fromAccount = await _context.Accounts.FindAsync(fromAccountId);
        if (fromAccount == null)
        {
            return TransferResult.CreateFailure("Source account not found.");
        }

        var toAccount = await _context.Accounts.FindAsync(toAccountId);
        if (toAccount == null)
        {
            return TransferResult.CreateFailure("Destination account not found.");
        }

        // VR-002: Validate sufficient balance
        if (fromAccount.Balance < amount)
        {
            return TransferResult.CreateFailure("Insufficient funds in source account.");
        }

        // Execute transfer atomically
        var transferDescription = string.IsNullOrWhiteSpace(description) ? "Internal Transfer" : description;

        var transactionDate = DateTime.UtcNow;

        // Deduct from source account
        fromAccount.Balance -= amount;
        var debitTransaction = new Transaction
        {
            Id = Guid.NewGuid(),
            AccountId = fromAccountId,
            Date = transactionDate,
            Description = transferDescription,
            Amount = -amount,
            Type = TransactionType.Debit,
            Category = "Internal Transfer",
            BalanceAfter = fromAccount.Balance
        };
        _context.Transactions.Add(debitTransaction);

        // Add to destination account
        toAccount.Balance += amount;
        var creditTransaction = new Transaction
        {
            Id = Guid.NewGuid(),
            AccountId = toAccountId,
            Date = transactionDate,
            Description = transferDescription,
            Amount = amount,
            Type = TransactionType.Credit,
            Category = "Internal Transfer",
            BalanceAfter = toAccount.Balance
        };
        _context.Transactions.Add(creditTransaction);

        // Save changes (atomic operation with in-memory database)
        await _context.SaveChangesAsync();

        return TransferResult.CreateSuccess(debitTransaction.Id, creditTransaction.Id);
    }
}
