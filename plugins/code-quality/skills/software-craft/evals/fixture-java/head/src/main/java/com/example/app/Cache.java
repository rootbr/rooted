package com.example.app;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** A shared cache of loaded values; one instance serves every request thread. */
public class Cache {
    private final Map<String, String> cache = new ConcurrentHashMap<>();

    public String peek(String key) {
        return cache.get(key);
    }

    public String getOrLoad(String key) {
        if (!cache.containsKey(key)) {
            cache.put(key, load(key));
        }
        return cache.get(key);
    }

    /** Builds a per-call index; the map never leaves this method. */
    public Map<String, Integer> buildIndex(List<String> words) {
        Map<String, Integer> index = new HashMap<>();
        for (String w : words) {
            if (!index.containsKey(w)) {
                index.put(w, index.size());
            }
        }
        return index;
    }

    String load(String key) {
        return key.toUpperCase();
    }
}
