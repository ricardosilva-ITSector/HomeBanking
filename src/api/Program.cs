using HomeBanking.Api.Data;
using HomeBanking.Api.Services;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Scalar.AspNetCore;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

// Add CORS configuration
var corsConfig = builder.Configuration.GetSection("Cors");
var allowedOrigins = corsConfig.GetSection("AllowedOrigins").Get<string[]>() ?? [];

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins(allowedOrigins)
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

// Add DbContext with InMemory provider
builder.Services.AddDbContext<HomeBankingDbContext>(options =>
    options.UseInMemoryDatabase("HomeBankingDb"));

// Register application services
builder.Services.AddScoped<ITransferService, TransferService>();

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// Configure OpenAPI with metadata
builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer((document, context, cancellationToken) =>
    {
        document.Info.Title = "Home Banking API";
        document.Info.Version = "v1";
        document.Info.Description = "REST API for home banking operations including account management, transaction history, and money transfers.";
        return Task.CompletedTask;
    });
});

// Add health checks
builder.Services.AddHealthChecks()
    .AddDbContextCheck<HomeBankingDbContext>(
        name: "database",
        failureStatus: HealthStatus.Unhealthy,
        tags: ["db", "ready"]);

var app = builder.Build();

// Seed the database
using (var scope = app.Services.CreateScope())
{
    var services = scope.ServiceProvider;
    var context = services.GetRequiredService<HomeBankingDbContext>();
    SeedData.Initialize(context);
}

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}

app.UseHttpsRedirection();

// Enable CORS
app.UseCors();

app.UseAuthorization();

app.MapControllers();

// Map health check endpoint with detailed JSON response
app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResponseWriter = async (context, report) =>
    {
        context.Response.ContentType = "application/json";

        var result = JsonSerializer.Serialize(new
        {
            status = report.Status.ToString(),
            checks = report.Entries.Select(e => new
            {
                name = e.Key,
                status = e.Value.Status.ToString(),
                description = e.Value.Description,
                duration = e.Value.Duration.TotalMilliseconds
            }),
            totalDuration = report.TotalDuration.TotalMilliseconds
        }, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true
        });

        await context.Response.WriteAsync(result);
    },
    ResultStatusCodes =
    {
        [HealthStatus.Healthy] = StatusCodes.Status200OK,
        [HealthStatus.Degraded] = StatusCodes.Status200OK,
        [HealthStatus.Unhealthy] = StatusCodes.Status503ServiceUnavailable
    }
});

app.Run();
