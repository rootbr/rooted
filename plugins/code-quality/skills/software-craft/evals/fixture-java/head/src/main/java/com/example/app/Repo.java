package com.example.app;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import javax.sql.DataSource;

/** JDBC access to the users table. */
public class Repo {
    private final DataSource dataSource;

    public Repo(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public int count() throws SQLException {
        try (Connection c = dataSource.getConnection();
             PreparedStatement ps = c.prepareStatement("select count(*) from users");
             ResultSet rs = ps.executeQuery()) {
            return rs.next() ? rs.getInt(1) : 0;
        }
    }

    public String findNameByEmail(String email) throws SQLException {
        Connection c = dataSource.getConnection();
        PreparedStatement ps = c.prepareStatement("select name from users where email = ?");
        ps.setString(1, email);
        ResultSet rs = ps.executeQuery();
        String name = rs.next() ? rs.getString(1) : null;
        rs.close();
        ps.close();
        c.close();
        return name;
    }

    public int countActive() throws SQLException {
        try (Connection c = dataSource.getConnection();
             PreparedStatement ps = c.prepareStatement("select count(*) from users where active = true");
             ResultSet rs = ps.executeQuery()) {
            return rs.next() ? rs.getInt(1) : 0;
        }
    }
}
