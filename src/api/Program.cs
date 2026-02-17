using HomeBanking.Api.Data;
using HomeBanking.Api.Services;
using Microsoft.EntityFrameworkCore;
using Scalar.AspNetCore;

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
builder.Services.AddHealthChecks();

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

// Map health check endpoint
app.MapHealthChecks("/health");

app.Run();
