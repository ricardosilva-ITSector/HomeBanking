using FluentAssertions;
using HomeBanking.Api.Controllers;
using HomeBanking.Api.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace HomeBanking.Api.Tests.Controllers;

/// <summary>
/// Unit tests for TransfersController.
/// </summary>
public class TransfersControllerTests
{
    private readonly Mock<ITransferService> _mockTransferService;
    private readonly Mock<ILogger<TransfersController>> _mockLogger;
    private readonly TransfersController _controller;

    public TransfersControllerTests()
    {
        _mockTransferService = new Mock<ITransferService>();
        _mockLogger = new Mock<ILogger<TransfersController>>();
        _controller = new TransfersController(_mockTransferService.Object, _mockLogger.Object);
    }

    [Fact]
    public async Task CreateTransfer_WithValidTransfer_ShouldReturn201Created()
    {
        // Arrange
        var request = new TransferRequest
        {
            FromAccountId = Guid.NewGuid(),
            ToAccountId = Guid.NewGuid(),
            Amount = 100.00m,
            Description = "Valid transfer"
        };

        var debitTransactionId = Guid.NewGuid();
        var creditTransactionId = Guid.NewGuid();

        var transferResult = new TransferResult
        {
            Success = true,
            DebitTransactionId = debitTransactionId,
            CreditTransactionId = creditTransactionId,
            ErrorMessage = null
        };

        _mockTransferService
            .Setup(s => s.ExecuteTransferAsync(
                request.FromAccountId,
                request.ToAccountId,
                request.Amount,
                request.Description))
            .ReturnsAsync(transferResult);

        // Act
        var result = await _controller.CreateTransfer(request);

        // Assert
        result.Should().BeOfType<CreatedAtActionResult>();
        var createdResult = (CreatedAtActionResult)result;
        createdResult.StatusCode.Should().Be(StatusCodes.Status201Created);
        
        var response = createdResult.Value.Should().BeOfType<TransferResponse>().Subject;
        response.DebitTransactionId.Should().Be(debitTransactionId);
        response.CreditTransactionId.Should().Be(creditTransactionId);
        response.Timestamp.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));
    }

    [Fact]
    public async Task CreateTransfer_WithSelfTransfer_ShouldReturn400BadRequest()
    {
        // Arrange - VR-001: Self-transfer validation
        var accountId = Guid.NewGuid();
        var request = new TransferRequest
        {
            FromAccountId = accountId,
            ToAccountId = accountId,
            Amount = 100.00m,
            Description = "Self transfer"
        };

        var transferResult = new TransferResult
        {
            Success = false,
            ErrorMessage = "Cannot transfer to the same account."
        };

        _mockTransferService
            .Setup(s => s.ExecuteTransferAsync(
                request.FromAccountId,
                request.ToAccountId,
                request.Amount,
                request.Description))
            .ReturnsAsync(transferResult);

        // Act
        var result = await _controller.CreateTransfer(request);

        // Assert
        result.Should().BeOfType<BadRequestObjectResult>();
        var badRequestResult = (BadRequestObjectResult)result;
        
        var errorResponse = badRequestResult.Value.Should().BeOfType<TransferErrorResponse>().Subject;
        errorResponse.Error.Should().Be("Cannot transfer to the same account.");
    }

    [Fact]
    public async Task CreateTransfer_WithAmountBelowMinimum_ShouldReturn400BadRequest()
    {
        // Arrange - VR-002: Amount validation (minimum)
        var request = new TransferRequest
        {
            FromAccountId = Guid.NewGuid(),
            ToAccountId = Guid.NewGuid(),
            Amount = 0.001m,
            Description = "Below minimum"
        };

        var transferResult = new TransferResult
        {
            Success = false,
            ErrorMessage = "Transfer amount must be at least 0.01."
        };

        _mockTransferService
            .Setup(s => s.ExecuteTransferAsync(
                request.FromAccountId,
                request.ToAccountId,
                request.Amount,
                request.Description))
            .ReturnsAsync(transferResult);

        // Act
        var result = await _controller.CreateTransfer(request);

        // Assert
        result.Should().BeOfType<BadRequestObjectResult>();
        var badRequestResult = (BadRequestObjectResult)result;
        
        var errorResponse = badRequestResult.Value.Should().BeOfType<TransferErrorResponse>().Subject;
        errorResponse.Error.Should().Contain("must be at least");
    }

    [Fact]
    public async Task CreateTransfer_WithAmountAboveMaximum_ShouldReturn400BadRequest()
    {
        // Arrange - VR-002: Amount validation (maximum)
        var request = new TransferRequest
        {
            FromAccountId = Guid.NewGuid(),
            ToAccountId = Guid.NewGuid(),
            Amount = 10000.01m,
            Description = "Above maximum"
        };

        var transferResult = new TransferResult
        {
            Success = false,
            ErrorMessage = "Transfer amount cannot exceed 10000.00."
        };

        _mockTransferService
            .Setup(s => s.ExecuteTransferAsync(
                request.FromAccountId,
                request.ToAccountId,
                request.Amount,
                request.Description))
            .ReturnsAsync(transferResult);

        // Act
        var result = await _controller.CreateTransfer(request);

        // Assert
        result.Should().BeOfType<BadRequestObjectResult>();
        var badRequestResult = (BadRequestObjectResult)result;
        
        var errorResponse = badRequestResult.Value.Should().BeOfType<TransferErrorResponse>().Subject;
        errorResponse.Error.Should().Contain("cannot exceed");
    }

    [Fact]
    public async Task CreateTransfer_WithMoreThanTwoDecimalPlaces_ShouldReturn400BadRequest()
    {
        // Arrange - VR-003: Decimal precision validation
        var request = new TransferRequest
        {
            FromAccountId = Guid.NewGuid(),
            ToAccountId = Guid.NewGuid(),
            Amount = 100.123m,
            Description = "Invalid precision"
        };

        var transferResult = new TransferResult
        {
            Success = false,
            ErrorMessage = "Transfer amount cannot have more than 2 decimal places."
        };

        _mockTransferService
            .Setup(s => s.ExecuteTransferAsync(
                request.FromAccountId,
                request.ToAccountId,
                request.Amount,
                request.Description))
            .ReturnsAsync(transferResult);

        // Act
        var result = await _controller.CreateTransfer(request);

        // Assert
        result.Should().BeOfType<BadRequestObjectResult>();
        var badRequestResult = (BadRequestObjectResult)result;
        
        var errorResponse = badRequestResult.Value.Should().BeOfType<TransferErrorResponse>().Subject;
        errorResponse.Error.Should().Contain("cannot have more than 2 decimal places");
    }

    [Fact]
    public async Task CreateTransfer_WithInsufficientFunds_ShouldReturn400BadRequest()
    {
        // Arrange - VR-004: Sufficient funds validation
        var request = new TransferRequest
        {
            FromAccountId = Guid.NewGuid(),
            ToAccountId = Guid.NewGuid(),
            Amount = 5000.00m,
            Description = "Insufficient funds"
        };

        var transferResult = new TransferResult
        {
            Success = false,
            ErrorMessage = "Insufficient funds in source account."
        };

        _mockTransferService
            .Setup(s => s.ExecuteTransferAsync(
                request.FromAccountId,
                request.ToAccountId,
                request.Amount,
                request.Description))
            .ReturnsAsync(transferResult);

        // Act
        var result = await _controller.CreateTransfer(request);

        // Assert
        result.Should().BeOfType<BadRequestObjectResult>();
        var badRequestResult = (BadRequestObjectResult)result;
        
        var errorResponse = badRequestResult.Value.Should().BeOfType<TransferErrorResponse>().Subject;
        errorResponse.Error.Should().Be("Insufficient funds in source account.");
    }

    [Fact]
    public async Task CreateTransfer_WithException_ShouldReturn500InternalServerError()
    {
        // Arrange
        var request = new TransferRequest
        {
            FromAccountId = Guid.NewGuid(),
            ToAccountId = Guid.NewGuid(),
            Amount = 100.00m,
            Description = "Exception test"
        };

        _mockTransferService
            .Setup(s => s.ExecuteTransferAsync(
                It.IsAny<Guid>(),
                It.IsAny<Guid>(),
                It.IsAny<decimal>(),
                It.IsAny<string?>()))
            .ThrowsAsync(new Exception("Database error"));

        // Act
        var result = await _controller.CreateTransfer(request);

        // Assert
        result.Should().BeOfType<ObjectResult>();
        var objectResult = (ObjectResult)result;
        objectResult.StatusCode.Should().Be(StatusCodes.Status500InternalServerError);
        
        var errorResponse = objectResult.Value.Should().BeOfType<TransferErrorResponse>().Subject;
        errorResponse.Error.Should().Be("An unexpected error occurred while processing the transfer.");
    }

    [Fact]
    public async Task CreateTransfer_ShouldCallTransferServiceWithCorrectParameters()
    {
        // Arrange
        var fromAccountId = Guid.NewGuid();
        var toAccountId = Guid.NewGuid();
        var amount = 250.50m;
        var description = "Test transfer";

        var request = new TransferRequest
        {
            FromAccountId = fromAccountId,
            ToAccountId = toAccountId,
            Amount = amount,
            Description = description
        };

        _mockTransferService
            .Setup(s => s.ExecuteTransferAsync(
                fromAccountId,
                toAccountId,
                amount,
                description))
            .ReturnsAsync(new TransferResult
            {
                Success = true,
                DebitTransactionId = Guid.NewGuid(),
                CreditTransactionId = Guid.NewGuid()
            });

        // Act
        await _controller.CreateTransfer(request);

        // Assert
        _mockTransferService.Verify(
            s => s.ExecuteTransferAsync(fromAccountId, toAccountId, amount, description),
            Times.Once);
    }
}
