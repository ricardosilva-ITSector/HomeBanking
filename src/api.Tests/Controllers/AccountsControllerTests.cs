using FluentAssertions;
using HomeBanking.Api.Controllers;
using HomeBanking.Api.Data;
using HomeBanking.Api.Models;
using HomeBanking.Api.Tests.Utilities;
using Microsoft.AspNetCore.Mvc;
using Xunit;

namespace HomeBanking.Api.Tests.Controllers;

/// <summary>
/// Unit tests for AccountsController.
/// </summary>
public class AccountsControllerTests : IDisposable
{
    private readonly HomeBankingDbContext _context;
    private readonly AccountsController _controller;

    public AccountsControllerTests()
    {
        _context = InMemoryDbContextFactory.Create();
        _controller = new AccountsController(_context);
    }

    [Fact]
    public async Task GetAccounts_WithEmptyDatabase_ShouldReturnEmptyList()
    {
        // Act
        var result = await _controller.GetAccounts();

        // Assert
        result.Should().NotBeNull();
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var accounts = okResult.Value.Should().BeAssignableTo<List<Account>>().Subject;
        accounts.Should().BeEmpty();
    }

    [Fact]
    public async Task GetAccounts_WithSeededData_ShouldReturnAllAccounts()
    {
        // Arrange
        var seedAccounts = TestDataBuilder.CreateSampleAccounts();
        _context.Accounts.AddRange(seedAccounts);
        await _context.SaveChangesAsync();

        // Act
        var result = await _controller.GetAccounts();

        // Assert
        result.Should().NotBeNull();
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var accounts = okResult.Value.Should().BeAssignableTo<List<Account>>().Subject;
        accounts.Should().HaveCount(3);
        accounts.Should().Contain(a => a.AccountNumber == "ACC-001");
        accounts.Should().Contain(a => a.AccountNumber == "ACC-002");
        accounts.Should().Contain(a => a.AccountNumber == "ACC-003");
    }

    [Fact]
    public async Task GetAccounts_ShouldReturnCorrectAccountDetails()
    {
        // Arrange
        var account = new Account
        {
            Id = Guid.NewGuid(),
            AccountNumber = "TEST-001",
            AccountName = "Test Account",
            Type = AccountType.Checking,
            Balance = 1000.00m,
            Currency = "USD",
            CreatedAt = DateTime.UtcNow,
            Transactions = new List<Transaction>()
        };
        _context.Accounts.Add(account);
        await _context.SaveChangesAsync();

        // Act
        var result = await _controller.GetAccounts();

        // Assert
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var accounts = okResult.Value.Should().BeAssignableTo<List<Account>>().Subject;
        accounts.Should().HaveCount(1);
        
        var returnedAccount = accounts.First();
        returnedAccount.AccountNumber.Should().Be("TEST-001");
        returnedAccount.AccountName.Should().Be("Test Account");
        returnedAccount.Type.Should().Be(AccountType.Checking);
        returnedAccount.Balance.Should().Be(1000.00m);
        returnedAccount.Currency.Should().Be("USD");
    }

    public void Dispose()
    {
        _context.Database.EnsureDeleted();
        _context.Dispose();
    }
}
