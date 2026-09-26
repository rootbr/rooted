package com.example.app;

import java.util.concurrent.ConcurrentHashMap;

/** Running totals per account, updated concurrently by the ingest workers. */
public class Totals {
    private final ConcurrentHashMap<String, Integer> totals = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, Integer> limits = new ConcurrentHashMap<>();

    public void add(String account, int amount) {
        totals.merge(account, amount, Integer::sum);
    }
}
