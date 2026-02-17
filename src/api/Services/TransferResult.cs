namespace HomeBanking.Api.Services;

/// <summary>
/// Represents the result of a transfer operation.
/// </summary>
public class TransferResult
{
    /// <summary>
    /// Gets or sets a value indicating whether the transfer was successful.
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Gets or sets the error message if the transfer failed.
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Gets or sets the identifier of the debit transaction created (from source account).
    /// </summary>
    public Guid? DebitTransactionId { get; set; }

    /// <summary>
    /// Gets or sets the identifier of the credit transaction created (to destination account).
    /// </summary>
    public Guid? CreditTransactionId { get; set; }

    /// <summary>
    /// Creates a successful transfer result.
    /// </summary>
    /// <param name="debitTransactionId">The identifier of the debit transaction.</param>
    /// <param name="creditTransactionId">The identifier of the credit transaction.</param>
    /// <returns>A successful transfer result.</returns>
    public static TransferResult CreateSuccess(Guid debitTransactionId, Guid creditTransactionId)
    {
        return new TransferResult
        {
            Success = true,
            DebitTransactionId = debitTransactionId,
            CreditTransactionId = creditTransactionId
        };
    }

    /// <summary>
    /// Creates a failed transfer result.
    /// </summary>
    /// <param name="errorMessage">The error message describing the failure.</param>
    /// <returns>A failed transfer result.</returns>
    public static TransferResult CreateFailure(string errorMessage)
    {
        return new TransferResult
        {
            Success = false,
            ErrorMessage = errorMessage
        };
    }
}
