package dispatch;

import java.time.Duration;

/** Routes a job to a worker and decides on resend after a timeout. */
public final class Router {
    private final Duration ackTimeout = Duration.ofMillis(250);
    private final boolean retryOnTimeout = false;
    private final Limits limits;

    public Router(Limits limits) {
        this.limits = limits;
    }

    public Decision route(Job job) {
        if (job.size() > limits.limit(job.queue())) {
            return Decision.reject("over limit");
        }
        return Decision.send(job, ackTimeout, retryOnTimeout);
    }
}
