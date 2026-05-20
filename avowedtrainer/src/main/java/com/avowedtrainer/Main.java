package com.avowedtrainer;

import java.util.Scanner;

/**
 * Entry point for the Avowed Trainer. Provides a simple console interface
 * to activate cheats. In a real project, this would be a GUI or hotkey-driven.
 */
public class Main {

    public static void main(String[] args) {
        System.out.println("=== Avowed Trainer v1.0.0 ===");
        System.out.print("Enter the Avowed process ID: ");
        Scanner scanner = new Scanner(System.in);
        int pid;
        try {
            pid = Integer.parseInt(scanner.nextLine().trim());
        } catch (NumberFormatException e) {
            System.err.println("Invalid PID. Exiting.");
            return;
        }

        Trainer trainer;
        try {
            trainer = new Trainer(pid);
        } catch (RuntimeException e) {
            System.err.println("Could not attach to process: " + e.getMessage());
            return;
        }

        System.out.println("Attached to process " + pid + ".");
        System.out.println("Commands: health <value>, essence <value>, godmode, status, quit");

        while (true) {
            System.out.print("> ");
            String input = scanner.nextLine().trim().toLowerCase();
            if (input.equals("quit") || input.equals("exit")) {
                break;
            } else if (input.equals("godmode")) {
                trainer.enableGodMode();
            } else if (input.equals("status")) {
                System.out.println("Health: " + trainer.getHealth());
                System.out.println("Essence: " + trainer.getEssence());
            } else if (input.startsWith("health ")) {
                try {
                    int val = Integer.parseInt(input.split(" ")[1]);
                    trainer.setHealth(val);
                } catch (Exception e) {
                    System.out.println("Usage: health <number>");
                }
            } else if (input.startsWith("essence ")) {
                try {
                    int val = Integer.parseInt(input.split(" ")[1]);
                    trainer.setEssence(val);
                } catch (Exception e) {
                    System.out.println("Usage: essence <number>");
                }
            } else {
                System.out.println("Unknown command.");
            }
        }

        trainer.shutdown();
        scanner.close();
        System.out.println("Trainer exited.");
    }
}
