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

    pub fn insert(&mut self, id: SessionId, user: String, now: Instant) {
        self.sessions.insert(id, Session { user, last_seen: now });
    }

    /// The sessions that have been idle for longer than the timeout.
    pub fn idle_sessions(&mut self) -> Vec<SessionId> {
        let now = Instant::now();
        let idle: Vec<SessionId> = self
            .sessions
            .iter()
            .filter(|(_, session)| now.duration_since(session.last_seen) > self.idle_timeout)
            .map(|(id, _)| *id)
            .collect();
        for id in &idle {
            self.sessions.remove(id);
        }
        idle
    }

    /// The time left before the session times out, or `None` when it already has or is unknown.
    pub fn remaining_lifetime(&self, id: SessionId, now: Instant) -> Option<Duration> {
        let session = self.sessions.get(&id)?;
        let expires = session.last_seen + self.idle_timeout;
        let expired = now >= expires;
        if expired {
            return None;
        }
        Some(expires - now)
    }
}
