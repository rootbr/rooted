package http;

import java.net.http.HttpTimeoutException;

public interface Transport {
    Response send(Request request, long timeoutMillis) throws HttpTimeoutException;
}
