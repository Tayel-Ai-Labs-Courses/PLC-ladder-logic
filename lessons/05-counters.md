# 05. Counters and why rung order matters

## The up counter (CTU)

A **CTU** box counts **rising edges**: each time its input goes from 0 to 1,
the count goes up by one. Holding the input at 1 does not count again. When
the count reaches the preset, the done bit `C0.0` turns 1 and stays 1 until a
**reset coil** `(R)` clears it.

| Box | Done bit is 1 when | Cleared by |
|---|---|---|
| `CTU C0.0 PV=10` | count >= 10 | `--( R )--` with address `C0.0` |

This is the real meaning of `(R)` in ladder, which is why lesson 02 renamed
the LED coil.

## Exercise 5: count 10 boxes, pause 10 s, run again

A conveyor (M1) carries boxes past a proximity sensor on `I0.2`. After 10
boxes it stops for 10 s, then starts again by itself.

```text
      I0.0      I0.1      C0.0                Q0.0
 |--+--] [--+----]/[-------]/[----------------( M1 )--|
 |  |  Q0.0 |   stop     "10 done"
 |  +--] [--+
 |  |  T0.0 |
 |  +--] [--+   <- restart after the pause
 |
 |    I0.2
 |----] [------------------------------[ CTU C0.0 PV=10 ]
 |   sensor
 |    C0.0
 |----] [------------------------------[ TON T0.0 10000 ]
 |    T0.0                                    C0.0
 |----] [-------------------------------------( R )-----|
```

How it is meant to work:

1. Start latches M1. Every box pulses the sensor; the counter counts.
2. At 10 the NC `C0.0` opens and M1 stops. `C0.0` also starts the 10 s TON.
3. After 10 s, `T0.0` resets the counter **and** restarts M1 through its
   branch in rung 1. M1 latches again and the cycle repeats.

The run sends one box per second for 10 s, then three more boxes from 21 s:

<!-- output: examples/apps.py counter -->
```text
  t (s)  start  sensor  M1  C0.0  T0.0  count
   0.00    0      0     0    0     0      0
   0.50    1      0     1    0     0      0
   0.70    0      0     1    0     0      0
   1.00    0      1     1    0     0      1
   1.20    0      0     1    0     0      1
   2.00    0      1     1    0     0      2
   2.20    0      0     1    0     0      2
   3.00    0      1     1    0     0      3
   3.20    0      0     1    0     0      3
   4.00    0      1     1    0     0      4
   4.20    0      0     1    0     0      4
   5.00    0      1     1    0     0      5
   5.20    0      0     1    0     0      5
   6.00    0      1     1    0     0      6
   6.20    0      0     1    0     0      6
   7.00    0      1     1    0     0      7
   7.20    0      0     1    0     0      7
   8.00    0      1     1    0     0      8
   8.20    0      0     1    0     0      8
   9.00    0      1     1    0     0      9
   9.20    0      0     1    0     0      9
  10.00    0      1     1    1     0      10
  10.01    0      1     0    1     0      10
  10.20    0      0     0    1     0      10
  20.00    0      0     0    0     1      0
  20.01    0      0     1    0     0      0
  21.00    0      1     1    0     0      1
  21.20    0      0     1    0     0      1
  22.00    0      1     1    0     0      2
  22.20    0      0     1    0     0      2
  23.00    0      1     1    0     0      3
  23.20    0      0     1    0     0      3
```

It works: M1 stops at 10.01 s, the 10 s pause runs, and at 20.01 s M1 is
back and counting from 1 again.

### Why it works: look at 20.00 and 20.01

`T0.0` is on for **one scan** only. In the scan at 20.00 s the timer finishes
(rung 3) and the reset clears the counter (rung 4). In the next scan rung 1
runs **first**: it still sees `T0.0 = 1` from the previous scan and
`C0.0 = 0`, so M1 turns on and seals in. Only then does rung 3 see
`C0.0 = 0` and reset the timer.

So the restart depends on rung 1 reading `T0.0` **before** rung 3 clears it.

### Prove it: move one rung

Here is the same program with the timer rung moved to the top. Not one
contact changed:

<!-- output: examples/apps.py counter-reordered -->
```text
  t (s)  start  sensor  M1  C0.0  T0.0  count
   0.00    0      0     0    0     0      0
   0.50    1      0     1    0     0      0
   0.70    0      0     1    0     0      0
   1.00    0      1     1    0     0      1
   1.20    0      0     1    0     0      1
   2.00    0      1     1    0     0      2
   2.20    0      0     1    0     0      2
   3.00    0      1     1    0     0      3
   3.20    0      0     1    0     0      3
   4.00    0      1     1    0     0      4
   4.20    0      0     1    0     0      4
   5.00    0      1     1    0     0      5
   5.20    0      0     1    0     0      5
   6.00    0      1     1    0     0      6
   6.20    0      0     1    0     0      6
   7.00    0      1     1    0     0      7
   7.20    0      0     1    0     0      7
   8.00    0      1     1    0     0      8
   8.20    0      0     1    0     0      8
   9.00    0      1     1    0     0      9
   9.20    0      0     1    0     0      9
  10.00    0      1     1    1     0      10
  10.01    0      1     0    1     0      10
  10.20    0      0     0    1     0      10
  20.01    0      0     0    0     1      0
  20.02    0      0     0    0     0      0
  21.00    0      1     0    0     0      1
  21.20    0      0     0    0     0      1
  22.00    0      1     0    0     0      2
  22.20    0      0     0    0     0      2
  23.00    0      1     0    0     0      3
  23.20    0      0     0    0     0      3
```

M1 never restarts. `T0.0` turns on at 20.01 s and the counter is reset in
that scan. In the next scan (20.02 s) the timer rung runs first, sees
`C0.0 = 0` and clears `T0.0`, so by the time rung 1 runs the restart pulse
is already gone.
The counter keeps counting boxes (if any arrive) while the conveyor stands
still.

**Lesson:** a one-scan pulse is only seen by rungs that run between the rung
that sets it and the rung that clears it. A more robust design does not rely
on order: restart M1 from the same condition that resets the counter, or use
a separate memory bit (`M0.0`) set by the timer and cleared by M1.

## Check yourself

1. Add a "reset count" button on `I0.3` that clears `C0.0` at any time. Which
   rung do you add?
2. Rewrite exercise 5 so the restart does not depend on rung order, then run
   both orders to prove it.

**Next:** [06. Interlocks: H-bridge and oil pump](06-interlocks.md)
