package com.example.app;

/** Per-request user context carried on the handler thread. */
public class RequestContext {
    private static final ThreadLocal<String> CURRENT_USER = new ThreadLocal<>();

    public static String currentUser() {
        return CURRENT_USER.get();
    }

    void process() {
    }
}
