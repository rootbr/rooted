use std::collections::HashMap;
use std::time::{Duration, Instant};

pub type SessionId = u64;

pub struct Session {
    pub user: String,
    pub last_seen: Instant,
}

/// Live user sessions; a session times out once it has been idle for longer than `idle_timeout`.
pub struct SessionCache {
    sessions: HashMap<SessionId, Session>,
    idle_timeout: Duration,
}

impl SessionCache {
    pub fn new(idle_timeout: Duration) -> Self {
        SessionCache { sessions: HashMap::new(), idle_timeout }
    }

    pub fn insert(&mut self, id: SessionId, user: String) {
        self.sessions.insert(id, Session { user, last_seen: Instant::now() });
    }
}
