using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using MemorySharp;

namespace AvowedTrainer.Core
{
    /// <summary>
    /// Core engine that manages memory reading/writing and hotkey detection.
    /// </summary>
    public class TrainerEngine : IDisposable
    {
        private Process? _targetProcess;
        private SharpMemory? _memory;
        private bool _disposed;

        // Memory offsets for Avowed (example values, would need real scanning)
        private readonly IntPtr _healthOffset = new IntPtr(0x00A1B2C0);
        private readonly IntPtr _staminaOffset = new IntPtr(0x00A1B2C4);
        private readonly IntPtr _godModeFlagOffset = new IntPtr(0x00A1B2C8);

        [DllImport("user32.dll")]
        private static extern short GetAsyncKeyState(int vKey);

        public TrainerEngine()
        {
            // Constructor: no initialization here; call Initialize() separately.
        }

        /// <summary>
        /// Attaches to the Avowed process and prepares memory access.
        /// </summary>
        public void Initialize()
        {
            var processes = Process.GetProcessesByName("Avowed");
            if (processes.Length == 0)
            {
                throw new InvalidOperationException("Avowed process not found. Please start the game first.");
            }

            _targetProcess = processes[0];
            _memory = new SharpMemory(_targetProcess);
            Console.WriteLine($"Attached to Avowed (PID: {_targetProcess.Id})");
        }

        /// <summary>
        /// Checks and processes hotkey presses.
        /// F1: Toggle God Mode
        /// F2: Set Infinite Stamina
        /// </summary>
        public void HandleHotkeys()
        {
            if (_memory == null || _targetProcess == null || _targetProcess.HasExited)
                return;

            // F1 key (virtual key code 0x70)
            if (GetAsyncKeyState(0x70) != 0)
            {
                ToggleGodMode();
                Thread.Sleep(200); // debounce
            }

            // F2 key (virtual key code 0x71)
            if (GetAsyncKeyState(0x71) != 0)
            {
                SetInfiniteStamina();
                Thread.Sleep(200);
            }
        }

        /// <summary>
        /// Reads current god mode flag and toggles it.
        /// </summary>
        private void ToggleGodMode()
        {
            try
            {
                byte currentFlag = _memory.Read<byte>(_godModeFlagOffset);
                byte newFlag = (byte)(currentFlag == 0 ? 1 : 0);
                _memory.Write(_godModeFlagOffset, newFlag);
                Console.WriteLine($"God Mode toggled to {(newFlag == 1 ? "ON" : "OFF")}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to toggle God Mode: {ex.Message}");
            }
        }

        /// <summary>
        /// Sets stamina to a very high value (infinite).
        /// </summary>
        private void SetInfiniteStamina()
        {
            try
            {
                float maxStamina = 9999.0f;
                _memory.Write(_staminaOffset, maxStamina);
                Console.WriteLine("Infinite Stamina activated.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to set stamina: {ex.Message}");
            }
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                _memory?.Dispose();
                _disposed = true;
            }
        }
    }
}
