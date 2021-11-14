using HumidiferWebController;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddSingleton<HumidificationService>();
builder.Services.AddValidatedOptions<HumidificationOptions>(builder.Configuration);

var app = builder.Build();

app.MapControllers();

app.Run();