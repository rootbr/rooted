package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/** Renders and archives orders. */
@Service
public class OrderService {
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);

    @Autowired
    private Repo repo;

    private final Formatter formatter;
    private boolean archived;

    public OrderService(Formatter formatter) {
        this.formatter = formatter;
    }

    public String render(String order, boolean forEmail) {
        if (forEmail) {
            return "<p>" + order + "</p>";
        }
        return order;
    }

    public void setArchived(boolean archived) {
        this.archived = archived;
    }

    public String loadName(String email) {
        try {
            return repo.findNameByEmail(email);
        } catch (java.sql.SQLException e) {
            log.error("lookup failed for {}", email, e);
            throw new IllegalStateException("lookup failed", e);
        }
    }

    public int loadCount() {
        try {
            return repo.count();
        } catch (java.sql.SQLException e) {
            throw new IllegalStateException("count failed", e);
        }
    }
}
