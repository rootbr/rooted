package app;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Properties;
import org.junit.jupiter.api.Test;

class ServerConfigTest {

    @Test
    void readsTheRenamedSetting() {
        Properties properties = new Properties();
        properties.setProperty("server.timeoutMs", "3000");
        assertEquals(3_000, new ServerConfig(properties).timeoutMs());
    }

    @Test
    void fallsBackToTheDefault() {
        assertEquals(5_000, new ServerConfig(new Properties()).timeoutMs());
    }
}
