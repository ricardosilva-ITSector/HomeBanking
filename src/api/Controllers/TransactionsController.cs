using HomeBanking.Api.Data;
using HomeBanking.Api.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace HomeBanking.Api.Controllers;

/// <summary>
/// Response DTO for paginated transaction results.
/// </summary>
public class PaginatedTransactionsResponse
{
    /// <summary>
    /// Gets or sets the total count of transactions (before pagination).
    /// </summary>
    public int TotalCount { get; set; }

    /// <summary>
    /// Gets or sets the list of transactions (paginated).
    /// </summary>
    public required List<Transaction> Transactions { get; set; }
}

/// <summary>
/// Controller for managing transactions.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class TransactionsController : ControllerBase
{
    private readonly HomeBankingDbContext _context;

    /// <summary>
    /// Initializes a new instance of the <see cref="TransactionsController"/> class.
    /// </summary>
    /// <param name="context">The database context.</param>
    public TransactionsController(HomeBankingDbContext context)
    {
        _context = context;
    }

    /// <summary>
    /// Retrieves transactions with optional filtering and pagination.
    /// </summary>
    /// <param name="accountId">Optional account ID to filter transactions.</param>
    /// <param name="limit">Maximum number of results to return (default: 100, max: 500).</param>
    /// <param name="offset">Number of transactions to skip (default: 0).</param>
    /// <returns>A paginated list of transactions with total count.</returns>
    /// <response code="200">Returns the paginated list of transactions.</response>
    [HttpGet]
    [ProducesResponseType(typeof(PaginatedTransactionsResponse), StatusCodes.Status200OK)]
    public async Task<ActionResult<PaginatedTransactionsResponse>> GetTransactions(
        [FromQuery] Guid? accountId = null,
        [FromQuery] int? limit = 100,
        [FromQuery] int? offset = 0)
    {
        // Apply limit constraints (default: 100, max: 500)
        var effectiveLimit = Math.Min(limit ?? 100, 500);
        var effectiveOffset = Math.Max(offset ?? 0, 0);

        // Build query with optional filtering
        var query = _context.Transactions.AsQueryable();

        if (accountId.HasValue)
        {
            query = query.Where(t => t.AccountId == accountId.Value);
        }

        // Get total count before pagination
        var totalCount = await query.CountAsync();

        // Apply ordering and pagination
        var transactions = await query
            .OrderByDescending(t => t.Date)
            .Skip(effectiveOffset)
            .Take(effectiveLimit)
            .ToListAsync();

        var response = new PaginatedTransactionsResponse
        {
            TotalCount = totalCount,
            Transactions = transactions
        };

        return Ok(response);
    }
}
