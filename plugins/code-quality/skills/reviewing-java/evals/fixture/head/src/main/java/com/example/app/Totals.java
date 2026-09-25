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
            Integer other = totals.get(from);
            int base = current == null ? 0 : current;
            return other == null ? base : base + Math.min(amount, other);
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
}
