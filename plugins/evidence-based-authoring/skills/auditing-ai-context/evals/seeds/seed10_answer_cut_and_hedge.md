Great question! Let me walk you through what is going on here.

The client waits 30 seconds before giving up, but only on the retry path — the
first attempt uses the socket's own timeout. It seems the gateway may possibly
drop idle sockets somewhere around that mark; I have not measured it.

In summary, the timeout is 30 seconds and it applies on the retry path.
