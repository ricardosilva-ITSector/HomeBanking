using HomeBanking.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace HomeBanking.Api.Data;

/// <summary>
/// Database context for the Home Banking application.
/// </summary>
public class HomeBankingDbContext : DbContext
{
    /// <summary>
    /// Initializes a new instance of the <see cref="HomeBankingDbContext"/> class.
    /// </summary>
    /// <param name="options">The options for this context.</param>
    public HomeBankingDbContext(DbContextOptions<HomeBankingDbContext> options)
        : base(options)
    {
    }

    /// <summary>
    /// Gets or sets the accounts in the database.
    /// </summary>
    public DbSet<Account> Accounts { get; set; }

    /// <summary>
    /// Gets or sets the transactions in the database.
    /// </summary>
    public DbSet<Transaction> Transactions { get; set; }

    /// <summary>
    /// Configures the model that was discovered by convention from the entity types.
    /// </summary>
    /// <param name="modelBuilder">The builder being used to construct the model for this context.</param>
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure Account entity
        modelBuilder.Entity<Account>(entity =>
        {
            entity.HasKey(e => e.Id);

            entity.Property(e => e.AccountNumber)
                .IsRequired()
                .HasMaxLength(50);

            entity.Property(e => e.AccountName)
                .IsRequired()
                .HasMaxLength(100);

            entity.Property(e => e.Balance)
                .HasPrecision(18, 2);

            entity.Property(e => e.Currency)
                .IsRequired()
                .HasMaxLength(3);

            entity.Property(e => e.Type)
                .IsRequired();

            entity.Property(e => e.CreatedAt)
                .IsRequired();

            // Configure one-to-many relationship with Transaction
            entity.HasMany(e => e.Transactions)
                .WithOne(e => e.Account)
                .HasForeignKey(e => e.AccountId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // Configure Transaction entity
        modelBuilder.Entity<Transaction>(entity =>
        {
            entity.HasKey(e => e.Id);

            entity.Property(e => e.Description)
                .IsRequired()
                .HasMaxLength(200);

            entity.Property(e => e.Amount)
                .HasPrecision(18, 2);

            entity.Property(e => e.BalanceAfter)
                .HasPrecision(18, 2);

            entity.Property(e => e.Category)
                .IsRequired()
                .HasMaxLength(50);

            entity.Property(e => e.Type)
                .IsRequired();

            entity.Property(e => e.Date)
                .IsRequired();

            entity.Property(e => e.AccountId)
                .IsRequired();
        });
    }
}
