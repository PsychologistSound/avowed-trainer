using System;
using System.Diagnostics;
using System.Runtime.InteropServices;

namespace AvowedTrainer.Core
{
    /// <summary>
    /// Provides low-level memory operations using Win32 API.
    /// Used as a fallback or alternative to MemorySharp.
    /// </summary>
    public static class MemoryHelper
    {
        [DllImport("kernel32.dll")]
        private static extern IntPtr OpenProcess(uint dwDesiredAccess, bool bInheritHandle, int dwProcessId);

        [DllImport("kernel32.dll")]
        private static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, int dwSize, out int lpNumberOfBytesRead);

        [DllImport("kernel32.dll")]
        private static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, int dwSize, out int lpNumberOfBytesWritten);

        [DllImport("kernel32.dll")]
        private static extern bool CloseHandle(IntPtr hObject);

        private const uint PROCESS_VM_READ = 0x0010;
        private const uint PROCESS_VM_WRITE = 0x0020;
        private const uint PROCESS_VM_OPERATION = 0x0008;

        /// <summary>
        /// Reads a value of type T from the target process's memory.
        /// </summary>
        public static T Read<T>(Process process, IntPtr address) where T : unmanaged
        {
            IntPtr hProcess = OpenProcess(PROCESS_VM_READ, false, process.Id);
            if (hProcess == IntPtr.Zero)
                throw new InvalidOperationException("Cannot open process for reading.");

            try
            {
                int size = Marshal.SizeOf<T>();
                byte[] buffer = new byte[size];
                if (!ReadProcessMemory(hProcess, address, buffer, size, out int bytesRead))
                    throw new InvalidOperationException("ReadProcessMemory failed.");

                IntPtr ptr = Marshal.AllocHGlobal(size);
                Marshal.Copy(buffer, 0, ptr, size);
                T result = Marshal.PtrToStructure<T>(ptr);
                Marshal.FreeHGlobal(ptr);
                return result;
            }
            finally
            {
                CloseHandle(hProcess);
            }
        }

        /// <summary>
        /// Writes a value of type T to the target process's memory.
        /// </summary>
        public static void Write<T>(Process process, IntPtr address, T value) where T : unmanaged
        {
            IntPtr hProcess = OpenProcess(PROCESS_VM_WRITE | PROCESS_VM_OPERATION, false, process.Id);
            if (hProcess == IntPtr.Zero)
                throw new InvalidOperationException("Cannot open process for writing.");

            try
            {
                int size = Marshal.SizeOf<T>();
                byte[] buffer = new byte[size];
                IntPtr ptr = Marshal.AllocHGlobal(size);
                Marshal.StructureToPtr(value, ptr, false);
                Marshal.Copy(ptr, buffer, 0, size);
                Marshal.FreeHGlobal(ptr);

                if (!WriteProcessMemory(hProcess, address, buffer, size, out int bytesWritten))
                    throw new InvalidOperationException("WriteProcessMemory failed.");
            }
            finally
            {
                CloseHandle(hProcess);
            }
        }
    }
}
