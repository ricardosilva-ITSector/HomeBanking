using HomeBanking.Api.Data;
using HomeBanking.Api.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace HomeBanking.Api.Controllers;

/// <summary>
/// Controller for managing bank accounts.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class AccountsController : ControllerBase
{
    private readonly HomeBankingDbContext _context;

    /// <summary>
    /// Initializes a new instance of the <see cref="AccountsController"/> class.
    /// </summary>
    /// <param name="context">The database context.</param>
    public AccountsController(HomeBankingDbContext context)
    {
        _context = context;
    }

    /// <summary>
    /// Retrieves all bank accounts.
    /// </summary>
    /// <returns>A list of all accounts.</returns>
    /// <response code="200">Returns the list of accounts.</response>
    [HttpGet]
    [ProducesResponseType(typeof(List<Account>), StatusCodes.Status200OK)]
    public async Task<ActionResult<List<Account>>> GetAccounts()
    {
        var accounts = await _context.Accounts.ToListAsync();
        return Ok(accounts);
    }
}
