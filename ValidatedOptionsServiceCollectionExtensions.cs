using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace HumidiferWebController
{
    public static class ValidatedOptionsServiceCollectionExtensions
    {
        public static IServiceCollection AddValidatedOptions<TOptions>(this IServiceCollection serviceCollection, IConfiguration configuration)
            where TOptions : class, new()
        {
            serviceCollection.AddOptions<TOptions>()
                .Bind(configuration.GetSection(typeof(TOptions).Name.Replace("Options", string.Empty)))
                .ValidateDataAnnotations();

            return serviceCollection
                .AddSingleton(typeof(TOptions), provider => provider.GetRequiredService<IOptions<TOptions>>().Value);
        }
    }
}