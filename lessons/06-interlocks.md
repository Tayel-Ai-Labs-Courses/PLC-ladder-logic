# 06. Interlocks: H-bridge and oil pump

An **interlock** is a contact that stops one output from running when it
must not: two directions at once, or a machine without its lubrication.

## Exercise 3: H-bridge (forward and reverse)

An H-bridge has four switches round a DC motor. Closing one diagonal pair
(T1 and T4) drives the motor forward; the other pair (T2 and T3) drives it in
reverse. If both pairs are on at once, the supply is shorted straight through
one side of the bridge (**shoot-through**), and transistors or fuses die.

```text
        +V ------+-----------+
                 |           |
               [T1]        [T2]
                 |           |
                 +---(M)-----+
                 |           |
               [T3]        [T4]
                 |           |
       GND ------+-----------+

   Q0.0 (forward) drives T1 + T4
   Q0.1 (reverse) drives T2 + T3
```

Check your own wiring against this: each output must drive **one diagonal**.
The drawing on the revision sheet is hard to read at this point, so confirm it
on the real board.

### The program on the sheet

```text
      I0.0      I0.1      I0.2                Q0.0
 |--+--] [--+----]/[-------]/[----------------( fwd )--|
 |  +--] [--+   stop     start2
 |     Q0.0
 |    I0.2      I0.1      I0.0                Q0.1
 |--+--] [--+----]/[-------]/[----------------( rev )--|
 |  +--] [--+   stop     start1
 |     Q0.1
```

This is a **button interlock**: pressing one start button opens the other
direction's rung. Run it: forward, then press reverse while forward runs.
The `scan` column is the scan number.

<!-- output: examples/apps.py hbridge -->
```text
  t (s)  scan  start1  stop  start2  fwd  rev
   0.00     1    0      0      0      0    0
   0.50    51    1      0      0      1    0
   0.70    71    0      0      0      1    0
   1.50   151    0      0      1      0    1
   1.70   171    0      0      0      0    1
```

At scan 151, in **the same scan**, forward goes off and reverse goes on. The
PLC writes both outputs at the end of that scan, so the hardware gets "T1+T4
off" and "T2+T3 on" at the same moment. Transistors and relays take time to
switch off, so for a short while all four can conduct. That is shoot-through.

### Does the usual output interlock fix it?

Every textbook adds an NC contact of the other output to each rung:

```text
 |  ... ]/[ I0.2 ... ]/[ Q0.1 ...( fwd )
 |  ... ]/[ I0.0 ... ]/[ Q0.0 ...( rev )
```

<!-- output: examples/apps.py hbridge-interlock -->
```text
  t (s)  scan  start1  stop  start2  fwd  rev
   0.00     1    0      0      0      0    0
   0.50    51    1      0      0      1    0
   0.70    71    0      0      0      1    0
   1.50   151    0      0      1      0    1
   1.70   171    0      0      0      0    1
```

**Identical.** The output interlock stops both rungs from being on at the
same time **inside the program**, but rung 1 switches forward off before
rung 2 runs, so rung 2 already sees `Q0.0 = 0` and switches reverse on in the
same scan. You still need the interlock (it protects you against both start
buttons and against later edits), but it does not create a gap in time.

### Add a dead time

Give each direction a TOF that stays on for 500 ms after it stops, and block
the other direction while it is on:

```text
      I0.0      I0.1   I0.2   Q0.1   T0.1             Q0.0
 |--+--] [--+----]/[----]/[----]/[----]/[-------------( fwd )--|
 |  +--] [--+
 |     Q0.0
 |    I0.2      I0.1   I0.0   Q0.0   T0.0             Q0.1
 |--+--] [--+----]/[----]/[----]/[----]/[-------------( rev )--|
 |  +--] [--+
 |     Q0.1
 |    Q0.0
 |----] [-------------------------------[ TOF T0.0 500 ]
 |    Q0.1
 |----] [-------------------------------[ TOF T0.1 500 ]
```

<!-- output: examples/apps.py hbridge-deadtime -->
```text
  t (s)  scan  start1  stop  start2  fwd  rev  T0.0
   0.00     1    0      0      0      0    0    0
   0.50    51    1      0      0      1    0    1
   0.70    71    0      0      0      1    0    1
   1.50   151    0      0      1      0    0    1
   1.70   171    0      0      0      0    0    1
   2.00   201    0      0      0      0    0    0
   2.50   251    0      0      1      0    1    0
   2.70   271    0      0      0      0    1    0
```

Pressing reverse at 1.50 s now only stops the motor. `T0.0` holds until 2.00
s; the press at 2.50 s starts reverse with half a second of everything off in
between. Real drives use the same idea, usually with a few milliseconds of
dead time in hardware as well.

## Exercise 7: oil pump before the main motor

The main motor (M2) may only run while the oil pump (M1) is running.

| Input | Button | Output | Load |
|---|---|---|---|
| `I0.0` | start oil | `Q0.0` | oil pump M1 |
| `I0.1` | stop oil | `Q0.1` | main motor M2 |
| `I0.2` | stop main | | |
| `I0.3` | start main | | |

```text
      I0.0      I0.1      I0.2                Q0.0
 |--+--] [--+----]/[-------]/[----------------( oil )--|
 |  +--] [--+  stop oil  stop main
 |     Q0.0
 |    Q0.0      I0.3      I0.2                Q0.1
 |----] [----+--] [--+-----]/[----------------( main )-|
 |   oil on  |  Q0.1 |   stop main
 |           +--] [--+
```

The `Q0.0` contact at the start of rung 2 is the interlock.

<!-- output: examples/apps.py oil -->
```text
  t (s)  st_oil  sp_oil  st_main  sp_main  oil  main
   0.00    0       0        0        0      0    0
   0.50    0       0        1        0      0    0
   0.70    0       0        0        0      0    0
   1.00    1       0        0        0      1    0
   1.20    0       0        0        0      1    0
   1.50    0       0        1        0      1    1
   1.70    0       0        0        0      1    1
   3.00    0       1        0        0      0    0
   3.20    0       0        0        0      0    0
   4.00    1       0        0        0      1    0
   4.20    0       0        0        0      1    0
   4.50    0       0        1        0      1    1
   4.70    0       0        0        0      1    1
   6.00    0       0        0        1      0    0
   6.20    0       0        0        0      0    0
```

- 0.50 s: start main with no oil, nothing happens.
- 1.50 s: with oil running, main starts.
- 3.00 s: stop oil also stops main, because main's rung loses `Q0.0`.
- 6.00 s: stop main stops **both**, because the sheet puts `I0.2` in the oil
  rung too. That makes "stop main" an emergency stop. If the oil pump should
  keep running to cool the bearings after the main motor stops, remove `I0.2`
  from rung 1.

## Check yourself

1. In the dead-time version, hold reverse pressed from 1.50 s to 2.70 s
   instead of tapping it. When does reverse start?
2. In exercise 7, make the oil pump keep running for 10 s after main stops,
   then stop by itself (hint: lesson 04).

**Next:** [07. Sensors: the water tank](07-water-tank.md)
