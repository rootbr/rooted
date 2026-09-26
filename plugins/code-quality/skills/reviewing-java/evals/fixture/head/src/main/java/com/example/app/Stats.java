package com.example.app;

/** Request statistics shared by every handler thread. */
public class Stats {
    private long total;
    private volatile int hits;
    private int samples;

    public synchronized long total() {
        return total;
    }

    public void hit() {
        hits++;
    }

    public synchronized void record() {
        total++;
    }

    /** Sampling counter for the dashboard; see the project context on approximate counters. */
    public void sample() {
        samples++;
    }

    public int hits() {
        return hits;
    }
}
