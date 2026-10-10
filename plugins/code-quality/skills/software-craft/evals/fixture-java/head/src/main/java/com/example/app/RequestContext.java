package com.example.app;

/** Per-request user context carried on the handler thread. */
public class RequestContext {
    private static final ThreadLocal<String> CURRENT_USER = new ThreadLocal<>();

    public static String currentUser() {
        return CURRENT_USER.get();
    }

    public void handle(String user) {
        CURRENT_USER.set(user);
        process();
        CURRENT_USER.set(null);
    }

    public void handleSafely(String user) {
        CURRENT_USER.set(user);
        try {
            process();
        } finally {
            CURRENT_USER.remove();
        }
    }

    void process() {
    }
}
