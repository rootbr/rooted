package com.example.app;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** A shared cache of loaded values; one instance serves every request thread. */
public class Cache {
    private final Map<String, String> cache = new ConcurrentHashMap<>();

    public String peek(String key) {
        return cache.get(key);
    }

    String load(String key) {
        return key.toUpperCase();
    }
}
