using HomeBanking.Api.Models;
using HomeBanking.Api.Services;
using Microsoft.AspNetCore.Mvc;

namespace HomeBanking.Api.Controllers;

/// <summary>
/// Request DTO for creating a transfer between accounts.
/// </summary>
public class TransferRequest
{
    /// <summary>
    /// Gets or sets the source account identifier.
    /// </summary>
    public required Guid FromAccountId { get; set; }

    /// <summary>
    /// Gets or sets the destination account identifier.
    /// </summary>
    public required Guid ToAccountId { get; set; }

    /// <summary>
    /// Gets or sets the amount to transfer.
    /// </summary>
    public required decimal Amount { get; set; }

    /// <summary>
    /// Gets or sets an optional description for the transfer.
    /// </summary>
    public string? Description { get; set; }
}

/// <summary>
/// Response DTO for a successful transfer operation.
/// </summary>
public class TransferResponse
{
    /// <summary>
    /// Gets or sets the identifier of the debit transaction (from source account).
    /// </summary>
    public required Guid DebitTransactionId { get; set; }

    /// <summary>
    /// Gets or sets the identifier of the credit transaction (to destination account).
    /// </summary>
    public required Guid CreditTransactionId { get; set; }

    /// <summary>
    /// Gets or sets the timestamp when the transfer was executed.
    /// </summary>
    public required DateTime Timestamp { get; set; }
}

/// <summary>
/// Response DTO for transfer validation errors.
/// </summary>
public class TransferErrorResponse
{
    /// <summary>
    /// Gets or sets the error message describing why the transfer failed.
    /// </summary>
    public required string Error { get; set; }
}

/// <summary>
/// Controller for managing money transfers between accounts.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class TransfersController : ControllerBase
{
    private readonly ITransferService _transferService;
    private readonly ILogger<TransfersController> _logger;

    /// <summary>
    /// Initializes a new instance of the <see cref="TransfersController"/> class.
    /// </summary>
    /// <param name="transferService">The transfer service.</param>
    /// <param name="logger">The logger instance.</param>
    public TransfersController(ITransferService transferService, ILogger<TransfersController> logger)
    {
        _transferService = transferService ?? throw new ArgumentNullException(nameof(transferService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    /// <summary>
    /// Creates a new transfer between two accounts.
    /// </summary>
    /// <param name="request">The transfer request containing source, destination, and amount details.</param>
    /// <returns>A transfer response with transaction identifiers on success, or error details on failure.</returns>
    /// <response code="201">Transfer completed successfully. Returns transaction identifiers.</response>
    /// <response code="400">Transfer validation failed. Returns error message.</response>
    /// <response code="500">An unexpected error occurred during transfer processing.</response>
    [HttpPost]
    [ProducesResponseType(typeof(TransferResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(TransferErrorResponse), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> CreateTransfer([FromBody] TransferRequest request)
    {
        try
        {
            _logger.LogInformation(
                "Processing transfer request from account {FromAccountId} to {ToAccountId} for amount {Amount}",
                request.FromAccountId,
                request.ToAccountId,
                request.Amount);

            var result = await _transferService.ExecuteTransferAsync(
                request.FromAccountId,
                request.ToAccountId,
                request.Amount,
                request.Description);

            if (result.Success)
            {
                _logger.LogInformation(
                    "Transfer successful. Debit transaction: {DebitId}, Credit transaction: {CreditId}",
                    result.DebitTransactionId,
                    result.CreditTransactionId);

                var response = new TransferResponse
                {
                    DebitTransactionId = result.DebitTransactionId!.Value,
                    CreditTransactionId = result.CreditTransactionId!.Value,
                    Timestamp = DateTime.UtcNow
                };

                return CreatedAtAction(nameof(CreateTransfer), response);
            }
            else
            {
                _logger.LogWarning(
                    "Transfer failed: {ErrorMessage}. Request: {@Request}",
                    result.ErrorMessage,
                    request);

                var errorResponse = new TransferErrorResponse
                {
                    Error = result.ErrorMessage!
                };

                return BadRequest(errorResponse);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(
                ex,
                "Unexpected error processing transfer from {FromAccountId} to {ToAccountId}",
                request.FromAccountId,
                request.ToAccountId);

            return StatusCode(
                StatusCodes.Status500InternalServerError,
                new TransferErrorResponse { Error = "An unexpected error occurred while processing the transfer." });
        }
    }
}
