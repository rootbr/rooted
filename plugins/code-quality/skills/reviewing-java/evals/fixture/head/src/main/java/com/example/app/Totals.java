package com.example.app;

import java.util.concurrent.ConcurrentHashMap;

/** Running totals per account, updated concurrently by the ingest workers. */
public class Totals {
    private final ConcurrentHashMap<String, Integer> totals = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, Integer> limits = new ConcurrentHashMap<>();

    public void add(String account, int amount) {
        totals.merge(account, amount, Integer::sum);
    }

    public void transfer(String from, String to, int amount) {
        totals.compute(to, (key, current) -> {
            totals.merge(from, -amount, Integer::sum);
            return (current == null ? 0 : current) + amount;
        });
    }

    public void addWithinLimit(String account, int amount) {
        totals.compute(account, (key, current) -> {
            Integer limit = limits.get(key);
            int base = current == null ? 0 : current;
            int next = base + amount;
            return limit == null ? next : Math.min(next, limit);
        });
    }

    /** Mirrors the sibling's balance; a stale read of the sibling is accepted by the dashboard. */
    public void mirror(String account, String sibling) {
        totals.compute(account, (key, current) -> {
            Integer other = totals.get(sibling);
            return other == null ? current : other;
        });
    }
}
