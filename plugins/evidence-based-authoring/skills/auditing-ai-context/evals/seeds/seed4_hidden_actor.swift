// Session access goes through an actor to remove the old races
// that used to happen with direct calls from multiple threads.
actor Session {
    func run(_ q: Query) -> Result { /* ... */ }
}
