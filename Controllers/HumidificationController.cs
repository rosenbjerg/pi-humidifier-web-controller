using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace HumidiferWebController.Controllers
{
    [ApiController]
    [Route("humidification")]
    public class HumidificationController : ControllerBase
    {
        private readonly HumidificationService _humidificationService;
        private readonly ILogger<HumidificationController> _logger;

        public HumidificationController(HumidificationService humidificationService, ILogger<HumidificationController> logger)
        {
            _humidificationService = humidificationService;
            _logger = logger;
        }

        [HttpPost("on")]
        public void On()
        {
            _logger.LogInformation("Starting humidifier");
            _humidificationService.Start();
        }

        [HttpPost("off")]
        public void Off()
        {
            _logger.LogInformation("Stopping humidifier");
            _humidificationService.Stop();
        }
    }
}