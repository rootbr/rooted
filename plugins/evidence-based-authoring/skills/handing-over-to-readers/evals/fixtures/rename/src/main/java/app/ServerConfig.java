package app;

import java.util.Properties;

/** Server settings; a deployment file overrides app.properties. */
public final class ServerConfig {
    private static final long DEFAULT_TIMEOUT_MS = 5_000;

    private final Properties properties;

    public ServerConfig(Properties properties) {
        this.properties = properties;
    }

    public long timeoutMs() {
        String value = properties.getProperty("server.timeoutMs");
        return value == null ? DEFAULT_TIMEOUT_MS : Long.parseLong(value);
    }
}
