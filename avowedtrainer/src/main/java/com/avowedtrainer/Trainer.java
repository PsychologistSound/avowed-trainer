package com.avowedtrainer;

/**
 * Main trainer class for Avowed. Provides high-level cheat functions
 * by manipulating game memory addresses.
 * <p>
 * Note: Addresses are examples and would need to be discovered dynamically
 * via pattern scanning in a real trainer.
 */
public class Trainer {

    private final MemoryManager memoryManager;
    // Example static addresses (would be dynamic in production)
    private static final long HEALTH_ADDRESS = 0x00A1B2C0;
    private static final long ESSENCE_ADDRESS = 0x00A1B2C4;
    private static final long MAX_HEALTH_ADDRESS = 0x00A1B2C8;

    /**
     * Creates a Trainer instance bound to a specific game process.
     *
     * @param processId The process ID of the Avowed game.
     */
    public Trainer(int processId) {
        this.memoryManager = new MemoryManager(processId);
    }

    /**
     * Sets the player's health to a specific value.
     *
     * @param health The desired health value (e.g., 999).
     */
    public void setHealth(int health) {
        memoryManager.writeInt(HEALTH_ADDRESS, health);
        System.out.println("Health set to " + health);
    }

    /**
     * Sets the player's essence (mana) to a specific value.
     *
     * @param essence The desired essence value (e.g., 500).
     */
    public void setEssence(int essence) {
        memoryManager.writeInt(ESSENCE_ADDRESS, essence);
        System.out.println("Essence set to " + essence);
    }

    /**
     * Sets the player's maximum health (useful for god mode).
     *
     * @param maxHealth The desired maximum health.
     */
    public void setMaxHealth(int maxHealth) {
        memoryManager.writeInt(MAX_HEALTH_ADDRESS, maxHealth);
        System.out.println("Max health set to " + maxHealth);
    }

    /**
     * Enables god mode by setting current health to a high value and max health.
     */
    public void enableGodMode() {
        setMaxHealth(99999);
        setHealth(99999);
        System.out.println("God mode enabled.");
    }

    /**
     * Reads and returns the current health value.
     *
     * @return The current health integer.
     */
    public int getHealth() {
        return memoryManager.readInt(HEALTH_ADDRESS);
    }

    /**
     * Reads and returns the current essence value.
     *
     * @return The current essence integer.
     */
    public int getEssence() {
        return memoryManager.readInt(ESSENCE_ADDRESS);
    }

    /**
     * Cleans up the memory manager.
     */
    public void shutdown() {
        memoryManager.close();
        System.out.println("Trainer shutdown complete.");
    }
}
