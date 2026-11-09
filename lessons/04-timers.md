# 04. Timers: TON and TOF

A timer is a box on a rung. It watches the power reaching it and sets a
**done bit** (`T0.0`) that other rungs use as a contact.

| Timer | Done bit `T0.x` is 1 ... | Use it for |
|---|---|---|
| **TON** on-delay | after the rung has been powered for the preset | "start M2 ten seconds after M1" |
| **TOF** off-delay | while the rung is powered **and** for the preset after it drops | "keep the fan running after the motor stops" |

If the power to a TON drops before the preset, it resets to zero and starts
again next time. Presets are in milliseconds (see lesson 01).

The runs below come from [`examples/apps.py`](../examples/apps.py). Buttons
are pressed for 0.2 s.

## Exercise 1: three motors, one after another

Start M1, then M2 after 10 s, then M3 after another 10 s. Stop turns all off.

```text
      I0.0      I0.1                Q0.0
 |--+--] [--+----]/[---------+------( M1 )--|
 |  |       |   stop         |
 |  +--] [--+                +--[ TON T0.0 10000 ]
 |     Q0.0
 |
 |    T0.0      I0.1                Q0.1
 |----] [--------]/[---------+------( M2 )--|
 |                           |
 |                           +--[ TON T0.1 10000 ]
 |
 |    T0.1      I0.1                Q0.2
 |----] [--------]/[----------------( M3 )--|
```

The TON sits **in parallel with the coil**, so it is powered exactly while
M1 runs. Because M1 is latched, T0.0 stays done, so M2 keeps running too.

<!-- output: examples/apps.py motors -->
```text
  t (s)  start  stop  M1  M2  M3
   0.00    0     0    0   0   0
   0.50    1     0    1   0   0
   0.70    0     0    1   0   0
  10.50    0     0    1   1   0
  20.50    0     0    1   1   1
  25.00    0     1    0   0   0
  25.20    0     0    0   0   0
```

M2 starts 10 s after the press (0.50 to 10.50 s), M3 10 s later. One stop
press drops everything: M1 falls, T0.0 resets, so M2 falls, and so on. The
cascade even happens inside one scan, because each rung reads what the rung
above just wrote.

## Exercise 2: run all three together for 10 s, then stop all

Add a third timer on M3 and an NC `T0.2` contact in every rung:

```text
      I0.0      I0.1      T0.2                Q0.0
 |--+--] [--+----]/[-------]/[-------+--------( M1 )--|
 |  +--] [--+                        +--[ TON T0.0 10000 ]
 |     Q0.0
 |    T0.0      I0.1      T0.2                Q0.1
 |----] [--------]/[-------]/[-------+--------( M2 )--|
 |                                   +--[ TON T0.1 10000 ]
 |    T0.1      I0.1      T0.2                Q0.2
 |----] [--------]/[-------]/[-------+--------( M3 )--|
 |                                   +--[ TON T0.2 10000 ]
```

<!-- output: examples/apps.py motors-together -->
```text
  t (s)  start  stop  M1  M2  M3  T0.2
   0.00    0     0    0   0   0    0
   0.50    1     0    1   0   0    0
   0.70    0     0    1   0   0    0
  10.50    0     0    1   1   0    0
  20.50    0     0    1   1   1    0
  30.50    0     0    1   1   1    1
  30.51    0     0    0   0   0    0
```

All three run together from 20.50 to 30.50 s. T0.2 turns on for **one scan**
(10 ms): it kills M1, M2 and M3 in the following scan, which drops M3's rung,
which resets T0.2 itself. A timer that resets itself this way is a classic
"one-shot" pattern.

Strictly, the NC `T0.2` in rung 1 is enough: once M1 drops, the cascade from
exercise 1 drops the rest. The extra contacts in rungs 2 and 3 make the
intent obvious to the next reader and cost nothing.

## Exercise 4: cool the motor after it stops (TOF)

```text
      I0.0      I0.1                Q0.0
 |--+--] [--+----]/[----------------( M1 )------|
 |  +--] [--+   stop
 |     Q0.0
 |    Q0.0
 |----] [---------------------[ TOF T0.0 5000 ]-|
 |    T0.0                          Q0.1
 |----] [---------------------------( cooler )--|
```

<!-- output: examples/apps.py cooler -->
```text
  t (s)  start  stop  motor  cooler
   0.00    0     0      0      0
   0.50    1     0      1      1
   0.70    0     0      1      1
   3.00    0     1      0      1
   3.20    0     0      0      1
   8.00    0     0      0      0
```

Read the run carefully: the cooler is on **the whole time the motor runs**
(from 0.50 s) and for 5 s after stop (3.00 to 8.00 s). That is what TOF does.

If the task means "cooler only **after** the motor turns off", add an NC
`Q0.0` contact in the cooler rung:

```text
 |    T0.0      Q0.0                Q0.1
 |----] [--------]/[----------------( cooler )--|
```

<!-- output: examples/apps.py cooler-after -->
```text
  t (s)  start  stop  motor  cooler
   0.00    0     0      0      0
   0.50    1     0      1      0
   0.70    0     0      1      0
   3.00    0     1      0      1
   3.20    0     0      0      1
   8.00    0     0      0      0
```

Now the cooler starts exactly when the motor stops and runs for 5 s. Ask which
one the exam wants; the sheet title "cool motor after off" fits the second.

## Check yourself

1. In exercise 1, what happens if you press stop at 15 s and start again at
   16 s? When does M2 come back? Add the presses to the `motors` scenario.
2. Change exercise 2 so the three motors stop **one by one** in reverse order
   (M3, then M2, then M1), 5 s apart.

**Next:** [05. Counters and the scan order](05-counters.md)
