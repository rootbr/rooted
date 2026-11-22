# How the service rotates its log file

The service writes its log into one file, and a file that only grows fills the disk. So the service closes the file from time to time, puts it aside under a dated name and starts a new one. This page explains when it does that and what happens to the files put aside. The mechanism is five steps and two limits.

## The whole mechanism

The mechanism keeps the size of the current file and the time it was opened. It takes in one event, a line to be written.

Before each line the service checks the current file against two limits, 100 megabytes and one day. Under both limits it writes the line into the current file. Over either limit it closes the file and renames it with the date and time of closing. It then opens a new file and writes the line there. After a rename it deletes the oldest dated files until seven are left.

```
on a line:    over = size > 100 MB or age > 1 day
if not over:  write the line to the current file
if over:      close the file; rename it to log.<date-time>
              open a new file; write the line to it
              delete the oldest log.<date-time> files until 7 remain
```

So the logs never take more than about 800 megabytes: seven files put aside and the current one.
