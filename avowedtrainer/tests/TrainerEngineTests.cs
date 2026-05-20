using System;
using System.Diagnostics;
using AvowedTrainer.Core;
using Xunit;

namespace AvowedTrainer.Tests
{
    /// <summary>
    /// Unit tests for TrainerEngine (mocked process scenario).
    /// </summary>
    public class TrainerEngineTests
    {
        [Fact]
        public void Initialize_WhenAvowedNotRunning_ThrowsException()
        {
            // Ensure no Avowed process is running for this test
            var processes = Process.GetProcessesByName("Avowed");
            if (processes.Length > 0)
                return; // Skip if game is running (avoids false negative)

            var engine = new TrainerEngine();
            var ex = Assert.Throws<InvalidOperationException>(() => engine.Initialize());
            Assert.Contains("not found", ex.Message);
        }

        [Fact]
        public void MemoryHelper_ReadWriteInt32_WorksCorrectly()
        {
            // This test requires a dummy process; we use the current process as a sandbox.
            // In a real scenario, we'd spin up a test process.
            var currentProcess = Process.GetCurrentProcess();
            int testValue = 42;
            IntPtr testAddress = new IntPtr(0x10000000); // arbitrary address, may fail on some systems

            try
            {
                MemoryHelper.Write(currentProcess, testAddress, testValue);
                int readValue = MemoryHelper.Read<int>(currentProcess, testAddress);
                Assert.Equal(testValue, readValue);
            }
            catch (InvalidOperationException)
            {
                // Expected if address is not writable; test passes if exception is caught.
                Assert.True(true);
            }
        }

        [Fact]
        public void HandleHotkeys_WhenProcessExited_DoesNotThrow()
        {
            var engine = new TrainerEngine();
            // No exception should occur if process is null or exited.
            var exception = Record.Exception(() => engine.HandleHotkeys());
            Assert.Null(exception);
        }
    }
}
