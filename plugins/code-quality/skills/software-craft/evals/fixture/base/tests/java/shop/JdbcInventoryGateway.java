package shop;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import javax.sql.DataSource;

/** The production InventoryGateway: every call is a query against the inventory database. */
public final class JdbcInventoryGateway implements InventoryGateway {
    private final DataSource dataSource;

    public JdbcInventoryGateway(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public int stockOf(String sku) {
        return Integer.parseInt(queryOne("SELECT on_hand FROM stock WHERE sku = ?", sku));
    }

    @Override
    public String warehouseFor(String sku) {
        return queryOne("SELECT warehouse FROM stock WHERE sku = ?", sku);
    }

    @Override
    public boolean reserve(String sku, int quantity) {
        try (Connection connection = dataSource.getConnection();
             PreparedStatement update = connection.prepareStatement(
                     "UPDATE stock SET on_hand = on_hand - ? WHERE sku = ? AND on_hand >= ?")) {
            update.setInt(1, quantity);
            update.setString(2, sku);
            update.setInt(3, quantity);
            return update.executeUpdate() == 1;
        } catch (SQLException e) {
            throw new IllegalStateException("reserving " + quantity + " of " + sku + " failed", e);
        }
    }

    private String queryOne(String sql, String sku) {
        try (Connection connection = dataSource.getConnection();
             PreparedStatement query = connection.prepareStatement(sql)) {
            query.setString(1, sku);
            try (ResultSet row = query.executeQuery()) {
                if (!row.next()) {
                    throw new IllegalArgumentException("unknown sku " + sku);
                }
                return row.getString(1);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("query for sku " + sku + " failed", e);
        }
    }
}
