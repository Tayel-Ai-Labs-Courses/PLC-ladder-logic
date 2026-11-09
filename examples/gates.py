"""Lessons 03 and 04: the seven logic gates as ladder rungs.

    python3 examples/gates.py table nand     # truth table, no latch
    python3 examples/gates.py latch nand     # with seal-in and stop
"""
import sys

import _path  # noqa: F401
from plc import timeline, truth_table

A, B, STOP, OUT = "I0.0", "I0.1", "I0.2", "Q0.0"

GATES = {
    "and":  lambda p: p.NO(A) and p.NO(B),
    "or":   lambda p: p.NO(A) or p.NO(B),
    "not":  lambda p: p.NC(A),
    "nand": lambda p: p.NC(A) or p.NC(B),
    "nor":  lambda p: p.NC(A) and p.NC(B),
    "xor":  lambda p: (p.NC(A) and p.NO(B)) or (p.NO(A) and p.NC(B)),
    "xnor": lambda p: (p.NC(A) and p.NC(B)) or (p.NO(A) and p.NO(B)),
}


def plain(gate):
    """Rung: gate contacts -> ( Q0.0 )"""
    return lambda p: p.coil(OUT, GATES[gate](p))


def latched(gate):
    """Rung: (gate contacts OR Q0.0 seal-in) -> ]/[ stop -> ( Q0.0 )"""
    return lambda p: p.coil(OUT, (GATES[gate](p) or p.NO(OUT)) and p.NC(STOP))


# One story per gate: press things, release them, press stop, release stop.
STORIES = {
    "and": [(500, A, 1), (700, B, 1), (1000, A, 0), (1000, B, 0),
            (2000, STOP, 1), (2200, STOP, 0)],
    "or": [(500, A, 1), (1000, A, 0), (2000, STOP, 1), (2200, STOP, 0)],
    "xor": [(500, A, 1), (1000, A, 0), (1500, A, 1), (1500, B, 1),
            (1800, A, 0), (1800, B, 0), (2000, STOP, 1), (2200, STOP, 0)],
    "nand": [(1000, STOP, 1), (1200, STOP, 0), (1500, A, 1), (1500, B, 1),
             (2000, STOP, 1), (2200, STOP, 0)],
    "nor": [(1000, STOP, 1), (1200, STOP, 0), (1500, A, 1),
            (2000, STOP, 1), (2200, STOP, 0)],
    "xnor": [(1000, STOP, 1), (1200, STOP, 0), (1500, A, 1),
             (2000, STOP, 1), (2200, STOP, 0)],
}

if __name__ == "__main__":
    mode, gate = sys.argv[1], sys.argv[2]
    if mode == "table":
        ins = {A: "A"} if gate == "not" else {A: "A", B: "B"}
        truth_table(plain(gate), ins, {OUT: "Q0.0"})
    else:
        timeline(latched(gate), STORIES[gate], 2500,
                 {A: "A", B: "B", STOP: "stop", OUT: "Q0.0"})
