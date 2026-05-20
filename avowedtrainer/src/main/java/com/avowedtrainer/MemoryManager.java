package com.avowedtrainer;

import com.sun.jna.Native;
import com.sun.jna.Pointer;
import com.sun.jna.platform.win32.Kernel32;
import com.sun.jna.platform.win32.WinNT;

/**
 * Manages low-level memory operations for the Avowed game process.
 * Uses JNA to interface with Windows kernel32 APIs for process access.
 */
public class MemoryManager {

    private final Kernel32 kernel32;
    private WinNT.HANDLE processHandle;
    private int processId;

    /**
     * Constructs a MemoryManager and attempts to open the Avowed process.
     *
     * @param processId The PID of the Avowed game process.
     */
    public MemoryManager(int processId) {
        this.kernel32 = Kernel32.INSTANCE;
        this.processId = processId;
        this.processHandle = kernel32.OpenProcess(
                WinNT.PROCESS_VM_READ | WinNT.PROCESS_VM_WRITE | WinNT.PROCESS_VM_OPERATION,
                false,
                processId
        );
        if (processHandle == null || !processHandle.isValid()) {
            throw new RuntimeException("Failed to open process with PID: " + processId +
                    ". Error code: " + Native.getLastError());
        }
    }

    /**
     * Reads a 4-byte integer from the specified memory address.
     *
     * @param address The memory address to read from.
     * @return The integer value at that address.
     */
    public int readInt(long address) {
        int[] buffer = new int[1];
        long bytesRead = kernel32.ReadProcessMemory(
                processHandle,
                new Pointer(address),
                buffer,
                4,
                null
        );
        if (bytesRead == 0) {
            throw new RuntimeException("Failed to read memory at 0x" + Long.toHexString(address) +
                    ". Error: " + Native.getLastError());
        }
        return buffer[0];
    }

    /**
     * Writes a 4-byte integer to the specified memory address.
     *
     * @param address The memory address to write to.
     * @param value   The integer value to write.
     */
    public void writeInt(long address, int value) {
        int[] buffer = new int[]{value};
        long bytesWritten = kernel32.WriteProcessMemory(
                processHandle,
                new Pointer(address),
                buffer,
                4,
                null
        );
        if (bytesWritten == 0) {
            throw new RuntimeException("Failed to write memory at 0x" + Long.toHexString(address) +
                    ". Error: " + Native.getLastError());
        }
    }

    /**
     * Closes the process handle to free system resources.
     */
    public void close() {
        if (processHandle != null && processHandle.isValid()) {
            kernel32.CloseHandle(processHandle);
            processHandle = null;
        }
    }

    /**
     * Gets the current process ID.
     *
     * @return The process ID.
     */
    public int getProcessId() {
        return processId;
    }
}
