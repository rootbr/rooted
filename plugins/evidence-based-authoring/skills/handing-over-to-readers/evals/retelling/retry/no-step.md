# How the client repeats a request

The client asks the price service for a quote and sometimes gets no answer in time. It then asks again, a little later each time, and gives up after a fixed number of tries. This page explains the order of those tries. The mechanism is five steps and two numbers it keeps.

## The whole mechanism

The mechanism keeps two numbers for one request: the tries made so far and the pause before the next try. It takes in one signal, whether an answer came within two seconds of a try.

The client sends the request and counts the try. An answer within two seconds ends the work with that answer. Without an answer the client waits for the pause, which starts at 200 milliseconds. After the fourth try without an answer the client reports a failure to its caller.

```
send(request); tries = tries + 1
if answered within 2 s:   return the answer
else:                      wait(pause)
if tries == 4:             report failure; else go to the first line
```

With no answer at all the client waits 200, 400 and 800 milliseconds between its four tries.
