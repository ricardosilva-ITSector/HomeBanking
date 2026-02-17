using HomeBanking.Api.Models;

namespace HomeBanking.Api.Data;

/// <summary>
/// Provides seed data for the Home Banking application.
/// </summary>
public static class SeedData
{
    /// <summary>
    /// Seeds the database with demo accounts and transactions.
    /// </summary>
    /// <param name="context">The database context.</param>
    public static void Initialize(HomeBankingDbContext context)
    {
        // Ensure database is created
        context.Database.EnsureCreated();

        // Check if data already exists
        if (context.Accounts.Any())
        {
            return; // Database has been seeded
        }

        // Create demo accounts
        var checkingAccountId = Guid.NewGuid();
        var savingsAccountId = Guid.NewGuid();

        var accounts = new[]
        {
            new Account
            {
                Id = checkingAccountId,
                AccountNumber = "CHK-001-123456",
                AccountName = "My Checking Account",
                Type = AccountType.Checking,
                Balance = 5000.00m,
                Currency = "USD",
                CreatedAt = DateTime.UtcNow.AddYears(-2)
            },
            new Account
            {
                Id = savingsAccountId,
                AccountNumber = "SAV-001-789012",
                AccountName = "My Savings Account",
                Type = AccountType.Savings,
                Balance = 15000.00m,
                Currency = "USD",
                CreatedAt = DateTime.UtcNow.AddYears(-2)
            }
        };

        context.Accounts.AddRange(accounts);
        context.SaveChanges();

        // Generate realistic transactions for the last 90 days
        var transactions = GenerateTransactions(checkingAccountId, savingsAccountId);
        context.Transactions.AddRange(transactions);
        context.SaveChanges();

        // Update final account balances based on transactions
        UpdateAccountBalances(context, checkingAccountId, savingsAccountId);
    }

    /// <summary>
    /// Generates realistic transactions for the demo accounts.
    /// </summary>
    private static List<Transaction> GenerateTransactions(Guid checkingAccountId, Guid savingsAccountId)
    {
        var transactions = new List<Transaction>();
        var random = new Random(42); // Fixed seed for reproducible data
        var currentDate = DateTime.UtcNow.AddDays(-90);

        // Starting balances
        decimal checkingBalance = 2000.00m;
        decimal savingsBalance = 14000.00m;

        // Transaction templates with realistic amounts
        var incomeTransactions = new[]
        {
            (Category: "Salary", MinAmount: 3000m, MaxAmount: 3500m, Type: TransactionType.Credit),
            (Category: "Refund", MinAmount: 25m, MaxAmount: 200m, Type: TransactionType.Credit)
        };

        var expenseTransactions = new[]
        {
            (Category: "Groceries", MinAmount: 15m, MaxAmount: 150m, Type: TransactionType.Debit),
            (Category: "Utilities", MinAmount: 50m, MaxAmount: 250m, Type: TransactionType.Debit),
            (Category: "Entertainment", MinAmount: 10m, MaxAmount: 100m, Type: TransactionType.Debit),
            (Category: "Transport", MinAmount: 5m, MaxAmount: 80m, Type: TransactionType.Debit),
            (Category: "Shopping", MinAmount: 20m, MaxAmount: 300m, Type: TransactionType.Debit),
            (Category: "Healthcare", MinAmount: 30m, MaxAmount: 200m, Type: TransactionType.Debit)
        };

        // Generate monthly salary deposits (3 months)
        for (int month = 0; month < 3; month++)
        {
            var salaryDate = currentDate.AddDays(month * 30 + 1);
            var salaryAmount = 3250.00m + (decimal)(random.NextDouble() * 250);
            checkingBalance += salaryAmount;

            transactions.Add(new Transaction
            {
                Id = Guid.NewGuid(),
                AccountId = checkingAccountId,
                Date = salaryDate,
                Description = "Monthly Salary Deposit",
                Amount = salaryAmount,
                Type = TransactionType.Credit,
                Category = "Salary",
                BalanceAfter = checkingBalance
            });
        }

        // Generate regular expense transactions
        for (int day = 0; day < 90; day++)
        {
            var transactionDate = currentDate.AddDays(day);

            // Skip some days randomly
            if (random.Next(100) < 40) continue;

            // Determine number of transactions for this day (1-3)
            int dailyTransactions = random.Next(1, 4);

            for (int i = 0; i < dailyTransactions; i++)
            {
                var template = expenseTransactions[random.Next(expenseTransactions.Length)];
                var amount = template.MinAmount + (decimal)(random.NextDouble() * (double)(template.MaxAmount - template.MinAmount));
                amount = Math.Round(amount, 2);

                checkingBalance -= amount;

                var description = GenerateDescription(template.Category, random);

                transactions.Add(new Transaction
                {
                    Id = Guid.NewGuid(),
                    AccountId = checkingAccountId,
                    Date = transactionDate.AddHours(random.Next(8, 20)).AddMinutes(random.Next(0, 60)),
                    Description = description,
                    Amount = amount,
                    Type = TransactionType.Debit,
                    Category = template.Category,
                    BalanceAfter = checkingBalance
                });
            }
        }

        // Add some refund transactions
        for (int i = 0; i < 5; i++)
        {
            var refundDate = currentDate.AddDays(random.Next(0, 90));
            var amount = 25m + (decimal)(random.NextDouble() * 175);
            amount = Math.Round(amount, 2);
            checkingBalance += amount;

            transactions.Add(new Transaction
            {
                Id = Guid.NewGuid(),
                AccountId = checkingAccountId,
                Date = refundDate,
                Description = $"Refund - {GenerateRefundReason(random)}",
                Amount = amount,
                Type = TransactionType.Credit,
                Category = "Refund",
                BalanceAfter = checkingBalance
            });
        }

        // Add internal transfers between accounts
        for (int i = 0; i < 4; i++)
        {
            var transferDate = currentDate.AddDays(random.Next(0, 90));
            var amount = 500m + (decimal)(random.NextDouble() * 1000);
            amount = Math.Round(amount, 2);

            // Transfer from checking to savings
            checkingBalance -= amount;
            transactions.Add(new Transaction
            {
                Id = Guid.NewGuid(),
                AccountId = checkingAccountId,
                Date = transferDate,
                Description = "Transfer to Savings Account",
                Amount = amount,
                Type = TransactionType.Debit,
                Category = "Internal Transfer",
                BalanceAfter = checkingBalance
            });

            savingsBalance += amount;
            transactions.Add(new Transaction
            {
                Id = Guid.NewGuid(),
                AccountId = savingsAccountId,
                Date = transferDate,
                Description = "Transfer from Checking Account",
                Amount = amount,
                Type = TransactionType.Credit,
                Category = "Internal Transfer",
                BalanceAfter = savingsBalance
            });
        }

        // Add a couple of transfers from savings to checking
        for (int i = 0; i < 2; i++)
        {
            var transferDate = currentDate.AddDays(random.Next(0, 90));
            var amount = 300m + (decimal)(random.NextDouble() * 500);
            amount = Math.Round(amount, 2);

            // Transfer from savings to checking
            savingsBalance -= amount;
            transactions.Add(new Transaction
            {
                Id = Guid.NewGuid(),
                AccountId = savingsAccountId,
                Date = transferDate,
                Description = "Transfer to Checking Account",
                Amount = amount,
                Type = TransactionType.Debit,
                Category = "Internal Transfer",
                BalanceAfter = savingsBalance
            });

            checkingBalance += amount;
            transactions.Add(new Transaction
            {
                Id = Guid.NewGuid(),
                AccountId = checkingAccountId,
                Date = transferDate,
                Description = "Transfer from Savings Account",
                Amount = amount,
                Type = TransactionType.Credit,
                Category = "Internal Transfer",
                BalanceAfter = checkingBalance
            });
        }

        // Sort transactions by date
        return transactions.OrderBy(t => t.Date).ToList();
    }

    /// <summary>
    /// Generates a realistic transaction description based on category.
    /// </summary>
    private static string GenerateDescription(string category, Random random)
    {
        return category switch
        {
            "Groceries" => new[] { "Whole Foods Market", "Trader Joe's", "Safeway", "Costco", "Local Grocery Store" }[random.Next(5)],
            "Utilities" => new[] { "Electric Company", "Water & Sewer", "Internet Service", "Gas Company", "Phone Bill" }[random.Next(5)],
            "Entertainment" => new[] { "Netflix Subscription", "Movie Theater", "Concert Tickets", "Spotify Premium", "Gaming Purchase" }[random.Next(5)],
            "Transport" => new[] { "Gas Station", "Public Transit", "Uber Ride", "Parking Fee", "Car Maintenance" }[random.Next(5)],
            "Shopping" => new[] { "Amazon Purchase", "Target", "Best Buy", "Clothing Store", "Online Shopping" }[random.Next(5)],
            "Healthcare" => new[] { "Pharmacy", "Doctor Visit Co-pay", "Dental Appointment", "Health Insurance", "Medical Supply" }[random.Next(5)],
            _ => "Transaction"
        };
    }

    /// <summary>
    /// Generates a realistic refund reason.
    /// </summary>
    private static string GenerateRefundReason(Random random)
    {
        return new[] { "Returned Item", "Billing Error", "Service Credit", "Overcharge Correction", "Product Return" }[random.Next(5)];
    }

    /// <summary>
    /// Updates account balances based on their transactions.
    /// </summary>
    private static void UpdateAccountBalances(HomeBankingDbContext context, Guid checkingAccountId, Guid savingsAccountId)
    {
        var checkingAccount = context.Accounts.Find(checkingAccountId);
        var savingsAccount = context.Accounts.Find(savingsAccountId);

        if (checkingAccount != null)
        {
            var lastCheckingTransaction = context.Transactions
                .Where(t => t.AccountId == checkingAccountId)
                .OrderByDescending(t => t.Date)
                .FirstOrDefault();

            if (lastCheckingTransaction != null)
            {
                checkingAccount.Balance = lastCheckingTransaction.BalanceAfter;
            }
        }

        if (savingsAccount != null)
        {
            var lastSavingsTransaction = context.Transactions
                .Where(t => t.AccountId == savingsAccountId)
                .OrderByDescending(t => t.Date)
                .FirstOrDefault();

            if (lastSavingsTransaction != null)
            {
                savingsAccount.Balance = lastSavingsTransaction.BalanceAfter;
            }
        }

        context.SaveChanges();
    }
}
