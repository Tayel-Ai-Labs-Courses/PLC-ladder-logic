"""A tiny PLC scan-cycle simulator for teaching ladder logic.

A ladder program is a plain Python function that receives the PLC and runs
its rungs top to bottom, exactly like a real PLC scan:

    def program(p):
        p.coil("Q0.0", (p.NO("I0.0") or p.NO("Q0.0")) and p.NC("I0.1"))

Every rung writes its result immediately, so a rung lower down already sees
what a rung higher up just wrote in the same scan. That ordering is the whole
point of several lessons, so the simulator keeps it on purpose.
"""
from itertools import product

__all__ = ["PLC", "timeline", "truth_table"]


class PLC:
    """One PLC: a bit memory, timers, counters and a clock in milliseconds."""

    def __init__(self, program, scan_ms=10):
        self.program = program
        self.scan_ms = scan_ms
        self.bits = {}        # every address: I0.0, Q0.0, T0.0, C0.0 ...
        self._start = {}      # timer name -> time its timing started
        self._count = {}      # counter name -> [count, previous input]
        self.now = 0          # time at the start of the current scan (ms)
        self.scans = 0

    # ---- contacts --------------------------------------------------------
    def NO(self, addr):
        """Normally open contact: passes power when the bit is 1."""
        return self.bits.get(addr, False)

    def NC(self, addr):
        """Normally closed contact: passes power when the bit is 0."""
        return not self.bits.get(addr, False)

    # ---- outputs ---------------------------------------------------------
    def coil(self, addr, power):
        """Output coil: the bit follows the power reaching it."""
        self.bits[addr] = bool(power)

    def ton(self, name, enable, preset_ms):
        """On-delay timer: done bit turns 1 after `enable` stays 1 for preset."""
        if enable:
            start = self._start.setdefault(name, self.now)
            self.bits[name] = self.now - start >= preset_ms
        else:
            self._start.pop(name, None)
            self.bits[name] = False

    def tof(self, name, enable, preset_ms):
        """Off-delay timer: done bit is 1 while enabled and for preset after."""
        if enable:
            self._start.pop(name, None)
            self.bits[name] = True
        elif self.bits.get(name):
            start = self._start.setdefault(name, self.now)
            self.bits[name] = self.now - start < preset_ms
        else:
            self._start.pop(name, None)
            self.bits[name] = False

    def ctu(self, name, count_in, preset):
        """Up counter: counts rising edges of `count_in`, done at preset."""
        state = self._count.setdefault(name, [0, False])
        if count_in and not state[1]:
            state[0] += 1
        state[1] = bool(count_in)
        self.bits[name] = state[0] >= preset

    def reset(self, name, power):
        """Reset coil (R) for a counter or timer: clears it while powered."""
        if power:
            if name in self._count:
                self._count[name][0] = 0
            self._start.pop(name, None)
            self.bits[name] = False

    def count(self, name):
        return self._count.get(name, [0])[0]

    # ---- running ---------------------------------------------------------
    def set(self, addr, value):
        self.bits[addr] = bool(value)

    def scan(self):
        self.program(self)
        self.scans += 1
        self.now += self.scan_ms


def truth_table(program, inputs, outputs, scans=1):
    """Print one row per input combination, each on a fresh PLC."""
    head = list(inputs.values()) + list(outputs.values())
    widths = [max(4, len(h)) for h in head]
    print("  ".join(h.center(w) for h, w in zip(head, widths)).rstrip())
    for combo in product([0, 1], repeat=len(inputs)):
        plc = PLC(program)
        for addr, value in zip(inputs, combo):
            plc.set(addr, value)
        for _ in range(scans):
            plc.scan()
        row = list(combo) + [int(plc.NO(a)) for a in outputs]
        print("  ".join(str(v).center(w) for v, w in zip(row, widths)).rstrip())


def timeline(program, events, until_ms, watch, scan_ms=10, plc=None,
             show_scan=False, extra=None):
    """Run a scenario and print a row every time a watched value changes.

    events : list of (time_ms, address, value) applied at the start of a scan
    watch  : {address: label} columns to print, inputs first by convention
    extra  : optional {label: function(plc)} extra columns, e.g. a count
    """
    plc = plc or PLC(program, scan_ms)
    events = sorted(events)
    extra = extra or {}
    labels = list(watch.values()) + list(extra)
    widths = [max(2, len(h)) for h in labels]
    head = "  t (s)  " + ("scan  " if show_scan else "")
    print((head + "  ".join(h.center(w) for h, w in zip(labels, widths))).rstrip())
    previous = None
    while plc.now <= until_ms:
        while events and events[0][0] <= plc.now:
            _, addr, value = events.pop(0)
            plc.set(addr, value)
        t = plc.now
        plc.scan()
        row = [int(plc.NO(a)) for a in watch] + [f(plc) for f in extra.values()]
        if row != previous:
            cells = "  ".join(str(v).center(w) for v, w in zip(row, widths))
            scan = f"{plc.scans:>4}  " if show_scan else ""
            print(f"{t / 1000:7.2f}  {scan}{cells}".rstrip())
            previous = row
    return plc
