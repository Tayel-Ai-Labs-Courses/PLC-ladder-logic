# 03. Latch and stop

The gates in lesson 02 only work while you hold the buttons. A real machine
needs "press start once, it keeps running, press stop to end". That is a
**latch** (also called **seal-in** or **self-holding**).

## The trick: the output holds itself

Put a contact of the output **itself** in parallel with the start condition,
and an NC stop contact in series after it:

```text
      I0.0      I0.1      I0.2      Q0.0
 |--+--] [-------] [--+----]/[------( )----|
 |  |   A         B   |   stop
 |  +--] [------------+
 |     Q0.0  (seal-in)
```

Follow one press:

1. A and B pressed: power passes, `Q0.0` turns on.
2. Next scan, the `Q0.0` contact on the lower branch is now closed too.
3. A and B released: the top branch opens, but power still flows through the
   `Q0.0` branch. The output **holds itself**.
4. Stop pressed: the NC `I0.2` contact opens, `Q0.0` drops, and the seal-in
   branch opens with it. Releasing stop does not bring it back.

Every "with stop" gate on the revision sheet is the same pattern:
`(gate OR Q0.0) AND NOT stop`. The rows below come from
[`examples/gates.py`](../examples/gates.py); a row is printed only when
something changes.

### AND with stop

<!-- output: examples/gates.py latch and -->
```text
  t (s)  A   B   stop  Q0.0
   0.00  0   0    0     0
   0.50  1   0    0     0
   0.70  1   1    0     1
   1.00  0   0    0     1
   2.00  0   0    1     0
   2.20  0   0    0     0
```

Exactly steps 1 to 4: on at 0.70 s, still on after release at 1.00 s, off at
2.00 s, stays off after stop is released.

### OR with stop

```text
      I0.0                I0.2      Q0.0
 |--+--] [--+-------------]/[-------( )----|
 |  |  I0.1 |             stop
 |  +--] [--+
 |  |  Q0.0 |
 |  +--] [--+
```

<!-- output: examples/gates.py latch or -->
```text
  t (s)  A   B   stop  Q0.0
   0.00  0   0    0     0
   0.50  1   0    0     1
   1.00  0   0    0     1
   2.00  0   0    1     0
   2.20  0   0    0     0
```

### XOR with stop

The XOR rung from lesson 02 with a third branch for `Q0.0`, then NC stop.

<!-- output: examples/gates.py latch xor -->
```text
  t (s)  A   B   stop  Q0.0
   0.00  0   0    0     0
   0.50  1   0    0     1
   1.00  0   0    0     1
   1.50  1   1    0     1
   1.80  0   0    0     1
   2.00  0   0    1     0
   2.20  0   0    0     0
```

Look at 1.50 s: both buttons are pressed, XOR is false, yet the LED stays on.
**Once latched, the gate condition no longer matters**. Only stop turns it
off. That is true for every latched gate, and it is the point of a latch.

## The trap: NAND, NOR and XNOR with stop

The sheet also latches NAND, NOR and XNOR. The rungs are drawn correctly, but
run them:

### NAND with stop

```text
      I0.0                I0.2      Q0.0
 |--+--]/[--+-------------]/[-------( )----|
 |  |  I0.1 |             stop
 |  +--]/[--+
 |  |  Q0.0 |
 |  +--] [--+
```

<!-- output: examples/gates.py latch nand -->
```text
  t (s)  A   B   stop  Q0.0
   0.00  0   0    0     1
   1.00  0   0    1     0
   1.20  0   0    0     1
   1.50  1   1    0     1
   2.00  1   1    1     0
   2.20  1   1    0     0
```

### NOR with stop

<!-- output: examples/gates.py latch nor -->
```text
  t (s)  A   B   stop  Q0.0
   0.00  0   0    0     1
   1.00  0   0    1     0
   1.20  0   0    0     1
   1.50  1   0    0     1
   2.00  1   0    1     0
   2.20  1   0    0     0
```

### XNOR with stop

<!-- output: examples/gates.py latch xnor -->
```text
  t (s)  A   B   stop  Q0.0
   0.00  0   0    0     1
   1.00  0   0    1     0
   1.20  0   0    0     1
   1.50  1   0    0     1
   2.00  1   0    1     0
   2.20  1   0    0     0
```

Three things the runs show:

1. **At 0.00 s the LED is already on.** Nobody pressed anything. These three
   gates are true when no button is pressed, so the very first scan latches
   the output.
2. **Stop only works while you hold it.** Stop at 1.00 s turns it off, but
   releasing stop at 1.20 s brings it straight back, because the gate is still
   true with nothing pressed.
3. Stop "sticks" only if a button that makes the gate false is held during
   the release (2.00 to 2.20 s in all three runs).

So the latch adds nothing useful to NAND, NOR and XNOR. Latching makes sense
for a condition that is **false at rest** and becomes true when an operator
acts: AND, OR, XOR. Know this before an exam asks "what happens at power up?".

## Check yourself

1. In the AND rung, move the seal-in branch so it goes round **B only**.
   Which button must stay pressed now? Change `latched()` in
   `examples/gates.py` and run it.
2. Why does the stop contact sit **after** the branches and not inside the
   seal-in branch only?

**Next:** [04. Timers](04-timers.md)
