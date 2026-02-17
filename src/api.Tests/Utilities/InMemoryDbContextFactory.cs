using HomeBanking.Api.Data;
using Microsoft.EntityFrameworkCore;

namespace HomeBanking.Api.Tests.Utilities;

/// <summary>
/// Factory for creating in-memory database contexts for testing.
/// </summary>
public static class InMemoryDbContextFactory
{
    /// <summary>
    /// Creates a new in-memory database context with a unique database name.
    /// </summary>
    /// <returns>A configured HomeBankingDbContext using in-memory database.</returns>
    public static HomeBankingDbContext Create()
    {
        var options = new DbContextOptionsBuilder<HomeBankingDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .EnableSensitiveDataLogging()
            .Options;

        var context = new HomeBankingDbContext(options);
        context.Database.EnsureCreated();

        return context;
    }

    /// <summary>
    /// Creates a new in-memory database context with seed data.
    /// </summary>
    /// <returns>A configured HomeBankingDbContext with test data.</returns>
    public static HomeBankingDbContext CreateWithSeedData()
    {
        var context = Create();
        SeedTestData(context);
        return context;
    }

    /// <summary>
    /// Seeds the database with test data.
    /// </summary>
    /// <param name="context">The database context to seed.</param>
    private static void SeedTestData(HomeBankingDbContext context)
    {
        var accounts = TestDataBuilder.CreateSampleAccounts();
        context.Accounts.AddRange(accounts);
        context.SaveChanges();
    }
}
