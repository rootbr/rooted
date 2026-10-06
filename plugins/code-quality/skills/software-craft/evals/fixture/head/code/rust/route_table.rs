use std::collections::{HashMap, HashSet};

/// A hub on the planning grid; one grid cell is `km_per_cell` kilometres wide.
pub struct Hub {
    pub code: String,
    pub grid_x: f64,
    pub grid_y: f64,
}

/// The hubs that can forward shipments today and how many shipments each one already holds.
pub struct RouteTable {
    closed_hubs: HashSet<String>,
    load_by_hub: HashMap<String, u32>,
    hub_capacity: u32,
    km_per_cell: f64,
}

impl RouteTable {
    pub fn new(hub_capacity: u32, km_per_cell: f64) -> Self {
        RouteTable { closed_hubs: HashSet::new(), load_by_hub: HashMap::new(), hub_capacity, km_per_cell }
    }

    /// Closes the hub to new shipments; returns whether it was open until this call.
    pub fn close_hub(&mut self, hub: &str) -> bool {
        self.closed_hubs.insert(hub.to_owned())
    }

    /// Reports the hub's state for today's planning.
    pub fn hub_status(&self, hub: &str) -> bool {
        let closed = self.closed_hubs.contains(hub);
        let load = self.load_by_hub.get(hub).copied().unwrap_or(0);
        !closed && load < self.hub_capacity
    }

    /// Straight-line distance between two hubs on the planning grid, in kilometres.
    pub fn grid_distance_km(&self, from: &Hub, to: &Hub) -> f64 {
        let delta_x = to.grid_x - from.grid_x;
        let delta_y = to.grid_y - from.grid_y;
        (delta_x * delta_x + delta_y * delta_y).sqrt() * self.km_per_cell
    }
}
