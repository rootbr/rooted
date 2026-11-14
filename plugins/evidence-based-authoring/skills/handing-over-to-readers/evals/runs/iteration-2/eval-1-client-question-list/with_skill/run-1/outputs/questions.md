# Arrival feed for your stop displays: three questions

1. **A pause when the network link drops.**
   We send predictions to your displays over one network link.
   When that link drops, the displays get no new predictions for up to 2.4 seconds, until it reconnects.
   If such a pause on the displays is acceptable, we keep the single link.
   If the displays must never pause, we add a second link, and it has to be set up on your network.
   Is a pause of up to 2.4 seconds acceptable when the link drops?

2. **A prediction that disagrees with the vehicle tracker.**
   Sometimes our predicted arrival differs from your vehicle tracker's own record by more than 1 minute.
   If a doubtful time is worse than no time, we leave that prediction off the display.
   If your dispatchers want to see it anyway, we show it with a warning mark.
   If such a difference means something is wrong upstream, we stop the feed to the displays.
   Which of these three should happen?

3. **How a missed prediction is counted.**
   Our quality report to you counts missed predictions, and our alarm fires on that count.
   A miss can be counted in two ways.
   By number: every prediction we send carries a running number, and a skipped number is one miss.
   By time: a stop that goes without a fresh prediction for longer than an agreed interval is one miss.
   If what matters to you is that every prediction arrives, we count by number.
   If what matters is that no display shows a stale time, we count by time.
   Which way should we count a missed prediction?

## Already settled

We read every time in your files as Vienna local time, because the header of your sample file names that zone.
We name the time field "ts", as in your other files.
