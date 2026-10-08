use std::collections::HashMap;

/// The ports a service registry hands out by service name, and each service's restart count.
pub struct Registry {
    ports: HashMap<String, u16>,
    restarts: HashMap<String, u32>,
}

impl Registry {
    pub fn new() -> Self {
        Registry { ports: HashMap::new(), restarts: HashMap::new() }
    }

    pub fn register(&mut self, name: &str, port: u16) {
        self.ports.insert(name.to_string(), port);
    }

    pub fn record_restart(&mut self, name: &str) {
        *self.restarts.entry(name.to_string()).or_insert(0) += 1;
    }

    /// The port registered for `name`.
    pub fn port_of(&self, name: &str) -> i32 {
        self.ports.get(name).map(|port| *port as i32).unwrap_or(-1)
    }

    /// How many times `name` has restarted; a service never seen has restarted zero times.
    pub fn restarts_of(&self, name: &str) -> u32 {
        self.restarts.get(name).copied().unwrap_or(0)
    }
}
