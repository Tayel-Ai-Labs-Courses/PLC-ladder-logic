# PLC Ladder Logic

The PLC part of the **Advanced IoT** course, as its own track: from "what is
a contact" to timers, counters, interlocks and sensors, built on the seven
exercises of the course revision sheet.

Every table in the lessons is printed by a real run of a small PLC simulator
written in Python (stdlib only), and CI re-runs all of them on every push. You
can change any rung and watch what the machine does, without a PLC on your
desk.

## Lessons

| # | Lesson | From the revision sheet |
|---|---|---|
| 01 | [What a PLC is and how it thinks](lessons/01-plc-basics.md) | I/O addresses, wiring, the scan cycle |
| 02 | [Contacts, coils and the seven gates](lessons/02-contacts-and-gates.md) | AND, OR, NOT, NAND, NOR, XOR, XNOR "without" |
| 03 | [Latch and stop](lessons/03-latch-and-stop.md) | every gate "with stop", and why NAND, NOR and XNOR misbehave |
| 04 | [Timers: TON and TOF](lessons/04-timers.md) | exercise 1 (3 motors), 2 (together 10 s), 4 (cooler) |
| 05 | [Counters and why rung order matters](lessons/05-counters.md) | exercise 5 (proximity sensor count) |
| 06 | [Interlocks: H-bridge and oil pump](lessons/06-interlocks.md) | exercise 3 (H-bridge), 7 (oil pump) |
| 07 | [Sensors: the water tank](lessons/07-water-tank.md) | exercise 6 (water tank) |

## Run it yourself

Python 3.10 or newer, nothing to install.

```bash
python3 examples/gates.py table xor
python3 examples/gates.py latch nand
python3 examples/apps.py hbridge
python3 examples/apps.py counter-reordered
```

The full list of scenarios is at the bottom of
[`examples/apps.py`](examples/apps.py). The simulator itself is one short
file, [`plc/__init__.py`](plc/__init__.py): read it, it is part of the course.

## What the runs found in the revision sheet

The sheet is correct as drawn. Running it exposed five things worth teaching:

1. **NAND, NOR and XNOR "with stop"** turn on at power up by themselves, and
   stop only works while it is held (lesson 03).
2. **The cooler (exercise 4)** runs the whole time the motor runs, not only
   after it stops. One NC contact changes that (lesson 04).
3. **The counter restart (exercise 5)** works only because of rung order.
   Move the timer rung to the top and the conveyor never restarts (lesson 05).
4. **The H-bridge (exercise 3)** reverses inside one scan, and the textbook
   output interlock does not change that. A 500 ms dead time does (lesson 06).
5. **The water tank (exercise 6)** is right only if LL reads 1 when the water
   is below it. With a normal float switch the same program starts the pump
   3002 times in 130 s (lesson 07).

## Checks

```bash
python3 tools/check_outputs.py   # every output block matches a fresh run
python3 tools/check_links.py     # no broken relative links
```

`python3 tools/check_outputs.py --write` refreshes all output blocks after you
change an example.

## License

[MIT](LICENSE)
