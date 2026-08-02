import AppKit

final class DragTracker {
    // We used to rely on NSSlider.action, but it never fired inside an open menu,
    // so mouse tracking is now done manually.
    func track(_ event: NSEvent) {
        // pump .leftMouseDragged / .leftMouseUp and map the cursor X to a value
    }
}
