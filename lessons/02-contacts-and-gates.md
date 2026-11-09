# 02. Contacts, coils and the seven gates

A ladder diagram looks like a ladder: two vertical **rails** (power on the
left, return on the right) and horizontal **rungs** between them. Power flows
from left to right through contacts. If it reaches the coil, the coil turns on.

## The three symbols

| Symbol | Name | Passes power when |
|---|---|---|
| `--] [--` | Normally open (NO) contact | its bit is **1** |
| `--]/[--` | Normally closed (NC) contact | its bit is **0** |
| `--( )--` | Coil | it *is* the output: it becomes 1 when power reaches it |

The revision sheet draws the NC contact as `--N--`. Same thing.

**Naming warning.** The sheet labels the output coil `(R)` because it drives a
red LED. In ladder, `(R)` is the standard symbol for a **Reset** coil, which
lesson 05 uses for real. In this course the LED coil is written `( )` with
the address `Q0.0` above it.

## Two rules make every gate

- Contacts **in series** (one after another) = **AND**. Power needs to pass
  both.
- Contacts **in parallel** (on branches) = **OR**. Power can take either path.

An NC contact on its own is a **NOT**.

In all the gates below, `I0.0` is button A, `I0.1` is button B and `Q0.0` is
the LED. Each table was printed by
[`examples/gates.py`](../examples/gates.py), which builds the rung, sets the
inputs and runs one scan on a fresh PLC.

### AND

```text
      I0.0      I0.1                Q0.0
 |----] [-------] [-----------------( )----|
```

<!-- output: examples/gates.py table and -->
```text
 A     B    Q0.0
 0     0     0
 0     1     0
 1     0     0
 1     1     1
```

### OR

```text
      I0.0                          Q0.0
 |--+--] [--+-----------------------( )----|
 |  |  I0.1 |
 |  +--] [--+
```

<!-- output: examples/gates.py table or -->
```text
 A     B    Q0.0
 0     0     0
 0     1     1
 1     0     1
 1     1     1
```

### NOT

```text
      I0.0                          Q0.0
 |----]/[---------------------------( )----|
```

<!-- output: examples/gates.py table not -->
```text
 A    Q0.0
 0     1
 1     0
```

The LED is **on** while nothing is pressed. Keep that in mind for the next
lesson.

### NAND = NOT A OR NOT B

```text
      I0.0                          Q0.0
 |--+--]/[--+-----------------------( )----|
 |  |  I0.1 |
 |  +--]/[--+
```

<!-- output: examples/gates.py table nand -->
```text
 A     B    Q0.0
 0     0     1
 0     1     1
 1     0     1
 1     1     0
```

### NOR = NOT A AND NOT B

```text
      I0.0      I0.1                Q0.0
 |----]/[-------]/[-----------------( )----|
```

<!-- output: examples/gates.py table nor -->
```text
 A     B    Q0.0
 0     0     1
 0     1     0
 1     0     0
 1     1     0
```

### XOR = exactly one pressed

Two branches: "A not pressed and B pressed" OR "A pressed and B not pressed".

```text
      I0.0      I0.1                Q0.0
 |--+--]/[-------] [--+-------------( )----|
 |  |  I0.0      I0.1 |
 |  +--] [-------]/[--+
```

<!-- output: examples/gates.py table xor -->
```text
 A     B    Q0.0
 0     0     0
 0     1     1
 1     0     1
 1     1     0
```

### XNOR = both the same

Two branches: "neither pressed" OR "both pressed".

```text
      I0.0      I0.1                Q0.0
 |--+--]/[-------]/[--+-------------( )----|
 |  |  I0.0      I0.1 |
 |  +--] [-------] [--+
```

<!-- output: examples/gates.py table xnor -->
```text
 A     B    Q0.0
 0     0     1
 0     1     0
 1     0     0
 1     1     1
```

## Check yourself

1. Which three gates turn the LED on when **no** button is pressed? Read it
   off the tables.
2. Build AND out of NC contacts only. (Hint: De Morgan says
   `A AND B = NOT (NOT A OR NOT B)`. Put the NAND rung on a helper bit
   `M0.0`, then drive `Q0.0` through an NC contact of `M0.0`.)

**Next:** [03. Latch and stop](03-latch-and-stop.md)
