using FluentAssertions;
using HomeBanking.Api.Data;
using HomeBanking.Api.Services;
using HomeBanking.Api.Tests.Utilities;
using Xunit;

namespace HomeBanking.Api.Tests.Services;

/// <summary>
/// Unit tests for TransferService.
/// </summary>
public class TransferServiceTests : IDisposable
{
    private readonly HomeBankingDbContext _context;
    private readonly TransferService _transferService;

    public TransferServiceTests()
    {
        _context = InMemoryDbContextFactory.CreateWithSeedData();
        _transferService = new TransferService(_context);
    }

    [Fact]
    public async Task ExecuteTransferAsync_WithSelfTransfer_ShouldReturnFailure()
    {
        // Arrange
        var accountId = Guid.Parse("11111111-1111-1111-1111-111111111111");
        var amount = 100.00m;

        // Act
        var result = await _transferService.ExecuteTransferAsync(
            accountId,
            accountId,
            amount,
            "Self transfer attempt");

        // Assert
        result.Success.Should().BeFalse();
        result.ErrorMessage.Should().Be("Cannot transfer to the same account.");
    }

    [Fact]
    public async Task ExecuteTransferAsync_WithAmountBelowMinimum_ShouldReturnFailure()
    {
        // Arrange
        var fromAccountId = Guid.Parse("11111111-1111-1111-1111-111111111111");
        var toAccountId = Guid.Parse("22222222-2222-2222-2222-222222222222");
        var amount = 0.001m; // Below minimum of 0.01

        // Act
        var result = await _transferService.ExecuteTransferAsync(
            fromAccountId,
            toAccountId,
            amount,
            "Below minimum amount");

        // Assert
        result.Success.Should().BeFalse();
        result.ErrorMessage.Should().Contain("must be at least");
        result.ErrorMessage.Should().Contain("0");
    }

    [Fact]
    public async Task ExecuteTransferAsync_WithAmountAboveMaximum_ShouldReturnFailure()
    {
        // Arrange
        var fromAccountId = Guid.Parse("11111111-1111-1111-1111-111111111111");
        var toAccountId = Guid.Parse("22222222-2222-2222-2222-222222222222");
        var amount = 10000.01m; // Above maximum of 10000.00

        // Act
        var result = await _transferService.ExecuteTransferAsync(
            fromAccountId,
            toAccountId,
            amount,
            "Above maximum amount");

        // Assert
        result.Success.Should().BeFalse();
        result.ErrorMessage.Should().Contain("cannot exceed");
        result.ErrorMessage.Should().Contain("10");
    }

    [Fact]
    public async Task ExecuteTransferAsync_WithMoreThanTwoDecimalPlaces_ShouldReturnFailure()
    {
        // Arrange
        var fromAccountId = Guid.Parse("11111111-1111-1111-1111-111111111111");
        var toAccountId = Guid.Parse("22222222-2222-2222-2222-222222222222");
        var amount = 100.123m; // Three decimal places

        // Act
        var result = await _transferService.ExecuteTransferAsync(
            fromAccountId,
            toAccountId,
            amount,
            "Invalid decimal places");

        // Assert
        result.Success.Should().BeFalse();
        result.ErrorMessage.Should().Contain("cannot have more than 2 decimal places");
    }

    [Fact]
    public async Task ExecuteTransferAsync_WithValidTransfer_ShouldSucceed()
    {
        // Arrange
        var fromAccountId = Guid.Parse("11111111-1111-1111-1111-111111111111");
        var toAccountId = Guid.Parse("22222222-2222-2222-2222-222222222222");
        var amount = 100.00m;
        var initialFromBalance = 5000.00m;
        var initialToBalance = 10000.00m;

        // Act
        var result = await _transferService.ExecuteTransferAsync(
            fromAccountId,
            toAccountId,
            amount,
            "Valid transfer");

        // Assert
        result.Success.Should().BeTrue();
        result.ErrorMessage.Should().BeNull();

        // Verify balances were updated
        var fromAccount = await _context.Accounts.FindAsync(fromAccountId);
        var toAccount = await _context.Accounts.FindAsync(toAccountId);

        fromAccount.Should().NotBeNull();
        toAccount.Should().NotBeNull();
        fromAccount!.Balance.Should().Be(initialFromBalance - amount);
        toAccount!.Balance.Should().Be(initialToBalance + amount);
    }

    [Fact]
    public async Task ExecuteTransferAsync_WithInsufficientFunds_ShouldReturnFailure()
    {
        // Arrange
        var fromAccountId = Guid.Parse("33333333-3333-3333-3333-333333333333"); // Balance: 100.00
        var toAccountId = Guid.Parse("22222222-2222-2222-2222-222222222222");
        var amount = 150.00m; // More than available balance

        // Act
        var result = await _transferService.ExecuteTransferAsync(
            fromAccountId,
            toAccountId,
            amount,
            "Insufficient funds");

        // Assert
        result.Success.Should().BeFalse();
        result.ErrorMessage.Should().Be("Insufficient funds in source account.");
    }

    public void Dispose()
    {
        _context.Database.EnsureDeleted();
        _context.Dispose();
    }
}
