using FluentAssertions;
using HomeBanking.Api.Controllers;
using HomeBanking.Api.Data;
using HomeBanking.Api.Models;
using HomeBanking.Api.Tests.Utilities;
using Microsoft.AspNetCore.Mvc;
using Xunit;

namespace HomeBanking.Api.Tests.Controllers;

/// <summary>
/// Unit tests for TransactionsController.
/// </summary>
public class TransactionsControllerTests : IDisposable
{
    private readonly HomeBankingDbContext _context;
    private readonly TransactionsController _controller;
    private readonly Guid _accountId1 = Guid.NewGuid();
    private readonly Guid _accountId2 = Guid.NewGuid();

    public TransactionsControllerTests()
    {
        _context = InMemoryDbContextFactory.Create();
        _controller = new TransactionsController(_context);
        SeedTestTransactions();
    }

    private void SeedTestTransactions()
    {
        // Create 10 transactions for account 1
        var transactions1 = TestDataBuilder.CreateSampleTransactions(_accountId1, 10);
        _context.Transactions.AddRange(transactions1);

        // Create 5 transactions for account 2
        var transactions2 = TestDataBuilder.CreateSampleTransactions(_accountId2, 5);
        _context.Transactions.AddRange(transactions2);

        _context.SaveChanges();
    }

    [Fact]
    public async Task GetTransactions_WithDefaultParameters_ShouldReturnAllTransactionsWithPagination()
    {
        // Act
        var result = await _controller.GetTransactions();

        // Assert
        result.Should().NotBeNull();
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var response = okResult.Value.Should().BeOfType<PaginatedTransactionsResponse>().Subject;
        
        response.TotalCount.Should().Be(15); // 10 + 5 transactions
        response.Transactions.Should().HaveCount(15);
    }

    [Fact]
    public async Task GetTransactions_WithLimit_ShouldReturnLimitedResults()
    {
        // Act
        var result = await _controller.GetTransactions(limit: 5);

        // Assert
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var response = okResult.Value.Should().BeOfType<PaginatedTransactionsResponse>().Subject;
        
        response.TotalCount.Should().Be(15); // Total count should still be 15
        response.Transactions.Should().HaveCount(5); // But only 5 returned
    }

    [Fact]
    public async Task GetTransactions_WithOffset_ShouldSkipTransactions()
    {
        // Act
        var result = await _controller.GetTransactions(offset: 10);

        // Assert
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var response = okResult.Value.Should().BeOfType<PaginatedTransactionsResponse>().Subject;
        
        response.TotalCount.Should().Be(15);
        response.Transactions.Should().HaveCount(5); // 15 - 10 = 5 remaining
    }

    [Fact]
    public async Task GetTransactions_WithLimitAndOffset_ShouldApplyBothCorrectly()
    {
        // Act
        var result = await _controller.GetTransactions(limit: 3, offset: 5);

        // Assert
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var response = okResult.Value.Should().BeOfType<PaginatedTransactionsResponse>().Subject;
        
        response.TotalCount.Should().Be(15);
        response.Transactions.Should().HaveCount(3);
    }

    [Fact]
    public async Task GetTransactions_WithAccountIdFilter_ShouldReturnOnlyAccountTransactions()
    {
        // Act
        var result = await _controller.GetTransactions(accountId: _accountId1);

        // Assert
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var response = okResult.Value.Should().BeOfType<PaginatedTransactionsResponse>().Subject;
        
        response.TotalCount.Should().Be(10);
        response.Transactions.Should().HaveCount(10);
        response.Transactions.Should().OnlyContain(t => t.AccountId == _accountId1);
    }

    [Fact]
    public async Task GetTransactions_WithMaxLimitExceeded_ShouldEnforceMaxLimit()
    {
        // Act - requesting 1000 but max is 500
        var result = await _controller.GetTransactions(limit: 1000);

        // Assert
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var response = okResult.Value.Should().BeOfType<PaginatedTransactionsResponse>().Subject;
        
        // Even though we have only 15 transactions, the controller should cap at 500
        response.Transactions.Should().HaveCountLessThanOrEqualTo(500);
        response.Transactions.Should().HaveCount(15); // In this case, we have less than the max
    }

    [Fact]
    public async Task GetTransactions_WithNegativeOffset_ShouldTreatAsZero()
    {
        // Act
        var result = await _controller.GetTransactions(offset: -5);

        // Assert
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var response = okResult.Value.Should().BeOfType<PaginatedTransactionsResponse>().Subject;
        
        response.Transactions.Should().HaveCount(15); // Should return all as if offset was 0
    }

    [Fact]
    public async Task GetTransactions_ShouldOrderByDateDescending()
    {
        // Act
        var result = await _controller.GetTransactions();

        // Assert
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var response = okResult.Value.Should().BeOfType<PaginatedTransactionsResponse>().Subject;
        
        var transactions = response.Transactions;
        for (int i = 0; i < transactions.Count - 1; i++)
        {
            transactions[i].Date.Should().BeOnOrAfter(transactions[i + 1].Date);
        }
    }

    [Fact]
    public async Task GetTransactions_WithNonExistentAccount_ShouldReturnEmptyList()
    {
        // Act
        var result = await _controller.GetTransactions(accountId: Guid.NewGuid());

        // Assert
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var response = okResult.Value.Should().BeOfType<PaginatedTransactionsResponse>().Subject;
        
        response.TotalCount.Should().Be(0);
        response.Transactions.Should().BeEmpty();
    }

    [Fact]
    public async Task GetTransactions_WithAccountIdAndPagination_ShouldApplyBothFilters()
    {
        // Act
        var result = await _controller.GetTransactions(accountId: _accountId1, limit: 3, offset: 2);

        // Assert
        var okResult = result.Result.Should().BeOfType<OkObjectResult>().Subject;
        var response = okResult.Value.Should().BeOfType<PaginatedTransactionsResponse>().Subject;
        
        response.TotalCount.Should().Be(10); // Total for account 1
        response.Transactions.Should().HaveCount(3); // Limited to 3
        response.Transactions.Should().OnlyContain(t => t.AccountId == _accountId1);
    }

    public void Dispose()
    {
        _context.Database.EnsureDeleted();
        _context.Dispose();
    }
}
