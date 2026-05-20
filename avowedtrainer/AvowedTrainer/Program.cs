using System;
using System.Threading;
using AvowedTrainer.Core;

namespace AvowedTrainer
{
    /// <summary>
    /// Entry point for the Avowed Trainer application.
    /// Initializes memory scanning and hotkey listeners.
    /// </summary>
    internal class Program
    {
        private static TrainerEngine? _engine;

        static void Main(string[] args)
        {
            Console.WriteLine("Avowed Trainer v1.0");
            Console.WriteLine("Searching for Avowed process...");

            try
            {
                _engine = new TrainerEngine();
                _engine.Initialize();
                
                Console.WriteLine("Trainer loaded. Press F1 for God Mode, F2 for Infinite Stamina.");
                
                // Keep the application running and listen for hotkeys
                while (true)
                {
                    _engine.HandleHotkeys();
                    Thread.Sleep(50);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
            }
        }
    }
}
