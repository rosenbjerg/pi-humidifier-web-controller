using System;
using System.Device.Gpio;
using System.Threading;
using System.Threading.Tasks;

namespace HumidiferWebController
{
    public class HumidificationService
    {
        private readonly HumidificationOptions _humidifierOptions;
        private volatile bool _humidifying;
        private readonly object _lock = new();
        private CancellationTokenSource? _cancellationTokenSource;

        public HumidificationService(HumidificationOptions humidifierOptions)
        {
            _humidifierOptions = humidifierOptions;
        }

        public void Stop()
        {
            if (_humidifying)
                _cancellationTokenSource!.Cancel();
        }

        public void Start()
        {
            StartHumidification();
        }
        private async Task StartHumidification()
        {
            if (_humidifying) return;
            lock (_lock)
            {
                if (_humidifying) return;
                _humidifying = true;
            }

            _cancellationTokenSource = new CancellationTokenSource();

            using var controller = new GpioController();
            controller.OpenPin(_humidifierOptions.HumidifierPowerPin, PinMode.Output);
            controller.OpenPin(_humidifierOptions.HumidifierButtonPin, PinMode.Output);

            try
            {
                await RunHumidifierLoop(controller);
            }
            catch (TaskCanceledException)
            {
            }
            
            TurnOffHumidifier(controller);

            _cancellationTokenSource = default;
            lock (_lock) _humidifying = false;
        }

        private async Task RunHumidifierLoop(GpioController controller)
        {
            for (var i = 0; i < _humidifierOptions.BurstCount; i++)
            {
                if (_cancellationTokenSource!.IsCancellationRequested) break;

                await TurnOnHumidifier(controller);
                await Task.Delay(TimeSpan.FromSeconds(_humidifierOptions.BurstLengthSeconds), _cancellationTokenSource.Token);

                TurnOffHumidifier(controller);
                await Task.Delay(TimeSpan.FromSeconds(_humidifierOptions.BurstPauseLengthSeconds), _cancellationTokenSource.Token);
            }
        }

        private async Task TurnOnHumidifier(GpioController controller)
        {
            controller.Write(_humidifierOptions.HumidifierPowerPin, PinValue.High);
            await Task.Delay(_humidifierOptions.HumidifierButtonDelayMs, _cancellationTokenSource!.Token);
            controller.Write(_humidifierOptions.HumidifierButtonPin, PinValue.High);
        }

        private void TurnOffHumidifier(GpioController controller)
        {
            controller.Write(_humidifierOptions.HumidifierPowerPin, PinValue.Low);
            controller.Write(_humidifierOptions.HumidifierButtonPin, PinValue.Low);
        }
    }
}