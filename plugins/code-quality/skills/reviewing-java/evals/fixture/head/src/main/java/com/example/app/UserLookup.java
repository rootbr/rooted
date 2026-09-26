package com.example.app;

import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Random;
import javax.sql.DataSource;

/** Looks up users for the account endpoints; every parameter arrives from the request. */
public class UserLookup {
    private final DataSource dataSource;
    private final SecureRandom secureRandom = new SecureRandom();

    public UserLookup(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public String findNameByEmail(String email) throws SQLException {
        try (Connection c = dataSource.getConnection();
             Statement st = c.createStatement();
             ResultSet rs = st.executeQuery("select name from users where email = '" + email + "'")) {
            return rs.next() ? rs.getString(1) : null;
        }
    }

    public String findNameById(long id) throws SQLException {
        try (Connection c = dataSource.getConnection();
             PreparedStatement ps = c.prepareStatement("select name from users where id = ?")) {
            ps.setLong(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? rs.getString(1) : null;
            }
        }
    }

    public Process convertAvatar(String uploadedFile) throws java.io.IOException {
        return Runtime.getRuntime().exec("sh -c 'convert " + uploadedFile + " avatar.png'");
    }

    public Process convertAvatarSafely(String uploadedFile) throws java.io.IOException {
        return new ProcessBuilder("convert", uploadedFile, "avatar.png").start();
    }

    public String newPasswordResetToken() {
        Random random = new Random();
        return Long.toHexString(random.nextLong()) + Long.toHexString(random.nextLong());
    }

    public String newSessionId() {
        byte[] bytes = new byte[32];
        secureRandom.nextBytes(bytes);
        return java.util.HexFormat.of().formatHex(bytes);
    }

    /** Picks the order in which sample avatars are shown; nothing depends on it being unguessable. */
    public int sampleAvatarIndex(int count) {
        Random random = new Random();
        return random.nextInt(count);
    }
}
