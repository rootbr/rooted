package dispatch;

/** Per-queue size limits, read from configuration. */
public final class Limits {
    private final LimitsConfig config;

    public Limits(LimitsConfig config) {
        this.config = config;
    }

    public long limit(String queue) {
        return config.limit(queue);
    }
}
