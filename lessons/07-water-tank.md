# 07. Sensors: the water tank

## Exercise 6: keep a tank between two levels

A pump (M1) fills a tank that the house drains all the time. Two level
sensors sit on the wall: **LL** (low level) near the bottom and **HL** (high
level) near the top. The pump must start when the water falls to LL and stop
when it reaches HL. Between the two it keeps doing whatever it was doing.
That gap is called **hysteresis**, and it stops the pump from switching on
and off every second.

| Input | Device |
|---|---|
| `I0.0` | start button |
| `I0.1` | stop button |
| `I0.2` | HL sensor |
| `I0.3` | LL sensor |
| `Q0.0` | pump M1 |

### The program on the sheet

```text
      I0.0      I0.1      I0.2                Q0.0
 |--+--] [--+----]/[-------]/[----------------( M1 )--|
 |  |  I0.3 |   stop      HL
 |  +--] [--+
 |  |  Q0.0 |
 |  +--] [--+
```

LL is a **normally open** contact in parallel with start. Whether that is
right depends on one question the sheet does not answer: **when does the LL
sensor read 1?**

The simulation below uses a tank model in
[`examples/apps.py`](../examples/apps.py): LL at 20 %, HL at 80 %, the pump
adds 4 %/s, the house takes 1 %/s, the tank starts at 50 %. HL reads 1 when
the water covers it. Only LL changes between the runs.

### Case A: LL reads 1 when the water is below it

<!-- output: examples/apps.py tank-sheet -->
```text
  t (s)  level  LL  HL  pump
   0.00   50.0   0   0    0
  30.01   20.0   1   0    1
  30.02   20.1   0   0    1
  50.02   80.0   0   1    0
  50.05   80.0   0   0    0
 110.05   20.0   1   0    1
 110.06   20.1   0   0    1
pump starts in 130 s: 2
```

This is what the sheet means and it works: the tank drains to 20 % (30 s),
LL starts the pump, the latch holds it as the water rises past LL, HL stops
it at 80 %, and the cycle repeats. Two starts in 130 s.

### Case B: LL is a float switch that reads 1 when the water covers it

Most cheap level switches work this way: wet = 1. Same program:

<!-- output: examples/apps.py tank-float -->
```text
  t (s)  level  LL  HL  pump
   0.00   50.0   1   0    1
  10.00   80.0   1   1    0
  10.01   80.0   1   0    1
  10.02   80.0   1   1    0
  10.05   80.0   1   0    1
  10.06   80.0   1   1    0
  10.09   80.0   1   0    1
  10.10   80.0   1   1    0
  10.13   80.0   1   0    1
  10.14   80.0   1   1    0
  10.17   80.0   1   0    1
  10.18   80.0   1   1    0
pump starts in 130 s: 3002
```

(The run prints only the first 12 changes.) The pump starts at once because
LL reads 1 at 50 %, fills to HL, stops, the level drops a hair below HL, LL
still reads 1, so it starts again. **3002 pump starts in 130 s.** On a real
pump that is a burnt motor or a tripped breaker.

### The fix for float switches: LL as NC

```text
      I0.0      I0.1      I0.2                Q0.0
 |--+--] [--+----]/[-------]/[----------------( M1 )--|
 |  |  I0.3 |
 |  +--]/[--+   <- NC: "LL is dry"
 |  |  Q0.0 |
 |  +--] [--+
```

<!-- output: examples/apps.py tank-float-fixed -->
```text
  t (s)  level  LL  HL  pump
   0.00   50.0   1   0    0
  30.01   20.0   0   0    1
  30.02   20.1   1   0    1
  50.02   80.0   1   1    0
  50.05   80.0   1   0    0
 110.05   20.0   0   0    1
 110.06   20.1   1   0    1
pump starts in 130 s: 2
```

Back to two starts. Same behaviour as case A, with the sensor's meaning
flipped and the contact flipped to match.

**Rule:** before you draw a sensor contact, write down what the sensor
outputs in each physical state. The contact type (NO or NC) follows from
that, not from the sensor's name.

## Check yourself

1. Add overflow protection: an extra sensor `I0.4` at 95 % (wet = 1) that
   stops the pump and lights an alarm lamp `Q0.1`, in case HL ever fails.
   Which contact type goes in the pump rung, and which in the alarm rung?
2. The house now draws 5 %/s, more than the pump can fill. What does the run
   show? Change the model in `run_tank` and see.

**Back to:** [Course home](../README.md)
