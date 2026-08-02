func onDrag(_ event: NSEvent) {
    // Track the drag manually: NSSlider's built-in tracking is inert inside a menu's event loop.
    // Do NOT call setBrightness off the main thread — AppKit asserts.
    setBrightness(value(for: event))
}
