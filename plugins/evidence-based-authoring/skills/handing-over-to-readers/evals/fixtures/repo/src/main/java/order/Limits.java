package order;

/** Per-instrument quantity limits, read from configuration. */
public final class Limits {
    private final LimitsConfig config;

    public Limits(LimitsConfig config) {
        this.config = config;
    }

    public long limit(String instrument) {
        return config.limit(instrument);
    }
}
