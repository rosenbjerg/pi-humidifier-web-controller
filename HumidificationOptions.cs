namespace HumidiferWebController
{
    public class HumidificationOptions
    {
        public int HumidifierPowerPin { get; set; }
        public int HumidifierButtonPin { get; set; }
        public int BurstCount { get; set; }
        public int BurstLengthSeconds { get; set; }
        public int BurstPauseLengthSeconds { get; set; }
        public int HumidifierButtonDelayMs { get; set; }
    }
}