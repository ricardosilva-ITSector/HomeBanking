namespace HomeBanking.Api.Services;

/// <summary>
/// Interface for transfer operations between accounts.
/// </summary>
public interface ITransferService
{
    /// <summary>
    /// Executes a transfer between two accounts.
    /// </summary>
    /// <param name="fromAccountId">The source account identifier.</param>
    /// <param name="toAccountId">The destination account identifier.</param>
    /// <param name="amount">The amount to transfer.</param>
    /// <param name="description">Optional description of the transfer.</param>
    /// <returns>A transfer result indicating success or failure with details.</returns>
    Task<TransferResult> ExecuteTransferAsync(Guid fromAccountId, Guid toAccountId, decimal amount, string? description = null);
}
