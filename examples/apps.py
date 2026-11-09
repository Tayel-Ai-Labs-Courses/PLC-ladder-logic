"""Lessons 05 to 08: the seven application exercises from the revision sheet.

    python3 examples/apps.py <scenario>

Every program below is the ladder from the sheet written rung by rung, top to
bottom, in the same order as the drawing. Timer presets are in milliseconds,
so 10000 means 10 seconds.
"""
import sys

import _path  # noqa: F401
from plc import PLC, timeline


def press(t_ms, addr, hold_ms=200):
    """A push button: pressed at t, released hold_ms later."""
    return [(t_ms, addr, 1), (t_ms + hold_ms, addr, 0)]


# ---- Exercise 1: three motors one after another ---------------------------
def motors(p):
    r1 = (p.NO("I0.0") or p.NO("Q0.0")) and p.NC("I0.1")
    p.coil("Q0.0", r1)
    p.ton("T0.0", r1, 10000)
    r2 = p.NO("T0.0") and p.NC("I0.1")
    p.coil("Q0.1", r2)
    p.ton("T0.1", r2, 10000)
    p.coil("Q0.2", p.NO("T0.1") and p.NC("I0.1"))


# ---- Exercise 2: then run all three together for 10 s and stop -----------
def motors_together(p):
    r1 = (p.NO("I0.0") or p.NO("Q0.0")) and p.NC("I0.1") and p.NC("T0.2")
    p.coil("Q0.0", r1)
    p.ton("T0.0", r1, 10000)
    r2 = p.NO("T0.0") and p.NC("I0.1") and p.NC("T0.2")
    p.coil("Q0.1", r2)
    p.ton("T0.1", r2, 10000)
    r3 = p.NO("T0.1") and p.NC("I0.1") and p.NC("T0.2")
    p.coil("Q0.2", r3)
    p.ton("T0.2", r3, 10000)


# ---- Exercise 3: H-bridge, forward / reverse ------------------------------
# I0.0 start1 (forward), I0.1 stop, I0.2 start2 (reverse)
def hbridge(p):
    p.coil("Q0.0", (p.NO("I0.0") or p.NO("Q0.0"))
           and p.NC("I0.1") and p.NC("I0.2"))
    p.coil("Q0.1", (p.NO("I0.2") or p.NO("Q0.1"))
           and p.NC("I0.1") and p.NC("I0.0"))


def hbridge_interlock(p):
    """Add the usual output interlock: each direction blocks the other."""
    p.coil("Q0.0", (p.NO("I0.0") or p.NO("Q0.0"))
           and p.NC("I0.1") and p.NC("I0.2") and p.NC("Q0.1"))
    p.coil("Q0.1", (p.NO("I0.2") or p.NO("Q0.1"))
           and p.NC("I0.1") and p.NC("I0.0") and p.NC("Q0.0"))


def hbridge_deadtime(p):
    """Interlock plus a 500 ms dead time: a direction may only start once the
    other has been off for 500 ms (TOF bits T0.0 / T0.1 cover that gap)."""
    p.coil("Q0.0", (p.NO("I0.0") or p.NO("Q0.0")) and p.NC("I0.1")
           and p.NC("I0.2") and p.NC("Q0.1") and p.NC("T0.1"))
    p.coil("Q0.1", (p.NO("I0.2") or p.NO("Q0.1")) and p.NC("I0.1")
           and p.NC("I0.0") and p.NC("Q0.0") and p.NC("T0.0"))
    p.tof("T0.0", p.NO("Q0.0"), 500)
    p.tof("T0.1", p.NO("Q0.1"), 500)


# ---- Exercise 4: keep the cooler running after the motor stops -----------
def cooler(p):
    p.coil("Q0.0", (p.NO("I0.0") or p.NO("Q0.0")) and p.NC("I0.1"))
    p.tof("T0.0", p.NO("Q0.0"), 5000)
    p.coil("Q0.1", p.NO("T0.0"))


def cooler_after_only(p):
    p.coil("Q0.0", (p.NO("I0.0") or p.NO("Q0.0")) and p.NC("I0.1"))
    p.tof("T0.0", p.NO("Q0.0"), 5000)
    p.coil("Q0.1", p.NO("T0.0") and p.NC("Q0.0"))


# ---- Exercise 5: count 10 boxes, pause 10 s, restart ----------------------
# I0.0 start, I0.1 stop, I0.2 proximity sensor
def counter(p):
    p.coil("Q0.0", (p.NO("I0.0") or p.NO("Q0.0") or p.NO("T0.0"))
           and p.NC("I0.1") and p.NC("C0.0"))
    p.ctu("C0.0", p.NO("I0.2"), 10)
    p.ton("T0.0", p.NO("C0.0"), 10000)
    p.reset("C0.0", p.NO("T0.0"))


def counter_reordered(p):
    """Same four rungs, timer rung moved to the top. Nothing else changed."""
    p.ton("T0.0", p.NO("C0.0"), 10000)
    p.coil("Q0.0", (p.NO("I0.0") or p.NO("Q0.0") or p.NO("T0.0"))
           and p.NC("I0.1") and p.NC("C0.0"))
    p.ctu("C0.0", p.NO("I0.2"), 10)
    p.reset("C0.0", p.NO("T0.0"))


BOXES = [e for k in range(10) for e in press(1000 + 1000 * k, "I0.2")] + \
        [e for k in range(3) for e in press(21000 + 1000 * k, "I0.2")]


# ---- Exercise 6: water tank -----------------------------------------------
# I0.0 start, I0.1 stop, I0.2 HL, I0.3 LL, Q0.0 pump
def tank_sheet(p):
    p.coil("Q0.0", (p.NO("I0.0") or p.NO("I0.3") or p.NO("Q0.0"))
           and p.NC("I0.1") and p.NC("I0.2"))


def tank_fixed(p):
    """LL as a normally closed contact, for sensors that read 1 when wet."""
    p.coil("Q0.0", (p.NO("I0.0") or p.NC("I0.3") or p.NO("Q0.0"))
           and p.NC("I0.1") and p.NC("I0.2"))


def run_tank(program, ll_means, seconds=130, max_rows=12):
    """Tank model: level in %, LL sensor at 20 %, HL sensor at 80 %.
    Pump adds 4 %/s, the house draws 1 %/s all the time.

    ll_means = "low"  : LL reads 1 while the water is BELOW it (as on the sheet)
    ll_means = "wet"  : LL reads 1 while the water covers it (a float switch)
    HL reads 1 while the water covers it in both cases.
    """
    plc = PLC(program)
    level, rows, starts, previous = 50.0, 0, 0, None
    print("  t (s)  level  LL  HL  pump")
    while plc.now <= seconds * 1000:
        covered = level >= 20
        plc.set("I0.3", covered if ll_means == "wet" else not covered)
        plc.set("I0.2", level >= 80)
        was_on = plc.NO("Q0.0")
        t = plc.now
        plc.scan()
        on = plc.NO("Q0.0")
        starts += on and not was_on
        level += (4.0 * on - 1.0) * plc.scan_ms / 1000
        row = (int(plc.NO("I0.3")), int(plc.NO("I0.2")), int(on))
        if row != previous:
            rows += 1
            if rows <= max_rows:
                print(f"{t / 1000:7.2f}  {level:5.1f}  {row[0]:>2}  "
                      f"{row[1]:>2}  {row[2]:>3}")
            previous = row
    print(f"pump starts in {seconds} s: {starts}")


# ---- Exercise 7: oil pump must run before the main motor ------------------
# I0.0 start oil, I0.1 stop oil, I0.2 stop main, I0.3 start main
def oil(p):
    p.coil("Q0.0", (p.NO("I0.0") or p.NO("Q0.0"))
           and p.NC("I0.1") and p.NC("I0.2"))
    p.coil("Q0.1", p.NO("Q0.0") and (p.NO("I0.3") or p.NO("Q0.1"))
           and p.NC("I0.2"))


MOTORS = {"I0.0": "start", "I0.1": "stop", "Q0.0": "M1", "Q0.1": "M2",
          "Q0.2": "M3"}
HB = {"I0.0": "start1", "I0.1": "stop", "I0.2": "start2",
      "Q0.0": "fwd", "Q0.1": "rev"}
COUNT = {"I0.0": "start", "I0.2": "sensor", "Q0.0": "M1", "C0.0": "C0.0",
         "T0.0": "T0.0"}

SCENARIOS = {
    "motors": lambda: timeline(
        motors, press(500, "I0.0") + press(25000, "I0.1"), 26000, MOTORS),
    "motors-together": lambda: timeline(
        motors_together, press(500, "I0.0"), 32000,
        {**MOTORS, "T0.2": "T0.2"}),
    "hbridge": lambda: timeline(
        hbridge, press(500, "I0.0") + press(1500, "I0.2"), 2000, HB,
        show_scan=True),
    "hbridge-interlock": lambda: timeline(
        hbridge_interlock, press(500, "I0.0") + press(1500, "I0.2"), 2000,
        HB, show_scan=True),
    "hbridge-deadtime": lambda: timeline(
        hbridge_deadtime,
        press(500, "I0.0") + press(1500, "I0.2") + press(2500, "I0.2"),
        3000, {**HB, "T0.0": "T0.0"}, show_scan=True),
    "cooler": lambda: timeline(
        cooler, press(500, "I0.0") + press(3000, "I0.1"), 9000,
        {"I0.0": "start", "I0.1": "stop", "Q0.0": "motor",
         "Q0.1": "cooler"}),
    "cooler-after": lambda: timeline(
        cooler_after_only, press(500, "I0.0") + press(3000, "I0.1"), 9000,
        {"I0.0": "start", "I0.1": "stop", "Q0.0": "motor",
         "Q0.1": "cooler"}),
    "counter": lambda: timeline(
        counter, press(500, "I0.0") + BOXES, 24000, COUNT,
        extra={"count": lambda p: p.count("C0.0")}),
    "counter-reordered": lambda: timeline(
        counter_reordered, press(500, "I0.0") + BOXES, 24000, COUNT,
        extra={"count": lambda p: p.count("C0.0")}),
    "tank-sheet": lambda: run_tank(tank_sheet, "low"),
    "tank-float": lambda: run_tank(tank_sheet, "wet"),
    "tank-float-fixed": lambda: run_tank(tank_fixed, "wet"),
    "oil": lambda: timeline(
        oil, press(500, "I0.3") + press(1000, "I0.0") + press(1500, "I0.3")
        + press(3000, "I0.1") + press(4000, "I0.0") + press(4500, "I0.3")
        + press(6000, "I0.2"), 6500,
        {"I0.0": "st_oil", "I0.1": "sp_oil", "I0.3": "st_main",
         "I0.2": "sp_main", "Q0.0": "oil", "Q0.1": "main"}),
}

if __name__ == "__main__":
    SCENARIOS[sys.argv[1]]()
