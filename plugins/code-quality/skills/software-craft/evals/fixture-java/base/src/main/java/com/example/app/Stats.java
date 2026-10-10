package com.example.app;

/** Request statistics shared by every handler thread. */
public class Stats {
    private long total;

    public synchronized long total() {
        return total;
    }
}
