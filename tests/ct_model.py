"""Reference model of the continuous-time applet's arithmetic, in Python.

An independent transcription of the math in Steven Crutchfield's Convolve.java (JHU, 1996):
the presets, mouse drawing, the Riemann sum for y(t) and the integrand at t, with Java's
integer semantics (int division truncates toward zero, (int) casts truncate). The browser
port must produce the same arrays (tests/test_html_portable.py), and when the original's
own output is available locally (reference/captures/ct/*.json, from tools/CtProbe.java) this
model must match that too (tests/test_model.py).

Sizes are the original's: x and h panels 234 x 124, conv/integrand panels 474 x 124.
"""
import math

SIG_N, SIG_H = 234, 124      # x(t), h(t) drawing panels
CONV_N, CONV_H = 474, 124    # "x(t - v) and h(v)" panel; the integral's sample count
AMP = SIG_H // 2             # 62 px: signal values are int pixels, +1 tick at AMP // 2 = 31


def jdiv(a: int, b: int) -> int:
    """Java int division: truncates toward zero (Python's // floors)."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


class Signal:
    def __init__(self, n=SIG_N, height=SIG_H):
        self.n = n
        self.amp = height // 2
        self.x = [0] * n

    def get(self, i):
        return self.x[i] if 0 <= i < self.n else 0

    def zero(self):
        self.x = [0] * self.n

    def pulse(self):
        self.zero()
        for i in range(self.n // 2, 3 * self.n // 4):
            self.x[i] = self.amp // 2

    def double_pulse(self):
        self.zero()
        for i in range(self.n // 2, self.n * 3 // 4):
            self.x[i] = -(self.amp // 2)
        for i in range(self.n * 3 // 4, self.n - 1):
            self.x[i] = self.amp // 2

    def decay(self):
        self.zero()
        for i in range(self.n // 2, self.n):
            self.x[i] = int(math.exp(-4.0 * (i - self.n // 2) / self.n) * self.amp / 2)

    def preset(self, name):
        {"pulse": self.pulse, "double pulse": self.double_pulse, "decay": self.decay,
         "clear": self.zero}[name]()

    def modify(self, i, y):
        if 0 < i < self.n - 1:
            self.x[i] = self.amp - y

    def drag(self, old_i, old_y, i, y):
        if i == old_i:
            return
        if old_i > i:
            old_i, i, old_y, y = i, old_i, y, old_y
        for c in range(old_i, i + 1):
            if 0 < c < self.n - 1:
                self.x[c] = self.amp - (old_y + jdiv((y - old_y) * (c - old_i), i - old_i))


class Applet:
    """Just the state the applet's arithmetic touches (no drawing)."""

    def __init__(self):
        self.sx, self.sh = Signal(), Signal()
        self.n = CONV_N
        self.amp = CONV_H // 2
        self.scale = 2.0 / self.amp
        self.offset = 0
        self.sig_changed = True
        self.t = 0
        self.prev_x = 0
        self.integrand = [0] * CONV_N
        self.y = [0] * CONV_N
        self.shown = [False] * CONV_N
        self.set_point = -1

    def sig_changed_event(self):
        if not self.sig_changed:
            self.y = [0] * self.n          # ConvSigPanel.clear(): zero y, forget shown
            self.shown = [False] * self.n
            self.set_point = -1
            self.integrand = [0] * self.n
        self.sig_changed = True

    def press(self, which, name):
        (self.sx if which == "x" else self.sh).preset(name)
        self.sig_changed_event()

    def update_signal(self):
        n, fx, fh = self.n, self.sx, self.sh
        self.offset = (n - fh.n) // 2
        dx = 2 * math.pi / n
        y = []
        for t in range(n):
            area = 0.0
            for s in range(n):
                area += fh.get(-self.offset + s) * fx.get(-self.offset + n // 2 + t - s)
            y.append(int(area * dx * self.scale))
        self.y = y
        self.shown = [False] * n

    def conv_down(self, x):
        if self.sig_changed:
            self.update_signal()
            self.sig_changed = False
        x = min(max(x, 0), self.n - 1)
        self.t = x + self.n // 2
        self.integrand = [int(self.sh.get(-self.offset + i) * self.sx.get(-self.offset + self.t - i)
                              * self.scale) for i in range(self.n)]
        self.set_point = x
        self.shown[x] = True
        self.prev_x = x

    def conv_drag(self, x):
        x = min(max(x, 0), self.n - 1)
        if self.prev_x > x:
            for i in range(self.prev_x, x, -1):
                self.shown[i] = True
        for i in range(self.prev_x, x):
            self.shown[i] = True
        self.conv_down(x)

    def dump(self):
        return {"fT": self.t, "fOffset": self.offset, "fPrevX": self.prev_x,
                "x": list(self.sx.x), "h": list(self.sh.x), "integrand": list(self.integrand),
                "y": list(self.y), "y_shown": [1 if b else 0 for b in self.shown]}


# The scripted user actions of tools/CtProbe.java (and the page's #selftest), in order;
# state carries over from one scenario to the next, as it does in the probe.
SCENARIOS = [
    ("s1_pulse_pulse", "pulse", "pulse", None),
    ("s2_pulse_decay", "pulse", "decay", None),
    ("s3_doublepulse_decay", "double pulse", "decay", None),
    ("s4_decay_doublepulse", "decay", "double pulse", None),
    ("s5_drawn_pulse", "clear", "pulse", "ramp"),
]


def run_scenario(app, xp, hp, draw):
    app.press("x", xp)
    app.press("h", hp)
    if draw == "ramp":
        w, hgt = SIG_N, SIG_H
        app.sx.modify(w // 2, hgt // 2)
        prev = (w // 2, hgt // 2)
        app.sig_changed_event()
        for i in range(1, 11):
            cur = (w // 2 + jdiv(i * (w // 2 - 2), 10), hgt // 2 - jdiv(i * (hgt // 4), 10))
            app.sx.drag(prev[0], prev[1], cur[0], cur[1])
            prev = cur
            app.sig_changed_event()
    n = app.n
    app.conv_down(0)
    prev = 0
    for stop in (n // 4, n // 2, 3 * n // 4, n - 1):
        for x in range(prev + 1, stop + 1):
            app.conv_drag(x)
        prev = stop


# Scenarios given as user actions, for what the preset sweeps never reach: drawing on h,
# leftward strokes and t sweeps, everything outside the panels, the cleared state, single
# clicks. ("preset", "x"|"h", name) presses a button; ("down"|"drag", "x"|"h"|"conv", x, y)
# is a mouse press or drag in panel pixels. The same lists are in tools/CtProbe.java and the
# page's SCENARIOS; they run after SCENARIOS, carrying state on.
ACTION_SCENARIOS = [
    ("s7_left_and_outside", [
        ("preset", "x", "pulse"), ("preset", "h", "clear"),
        ("down", "h", 120, 30), ("drag", "h", 90, 90), ("drag", "h", 60, -40), ("drag", "h", 30, 200),
        ("drag", "h", -20, 62),
        ("down", "h", 200, 62), ("drag", "h", 250, -10), ("drag", "h", 250, 50),
        ("down", "x", 30, 100), ("drag", "x", 60, 100),
        ("down", "conv", 400, 0), ("drag", "conv", 350, 0), ("drag", "conv", 200, 0),
        ("drag", "conv", 100, 0), ("drag", "conv", -50, 0),
        ("down", "conv", 450, 0), ("drag", "conv", 600, 0), ("drag", "conv", 470, 0)]),
    ("s8_cleared", [("preset", "x", "decay")]),
    ("s9_clicks", [("down", "conv", 300, 0), ("down", "conv", 100, 0),
                   ("down", "conv", 473, 0), ("down", "conv", 0, 0)]),
]


def run_actions(app, actions):
    prev = getattr(app, "prev", {})        # MouseSigPanel.prevX/prevY, one per panel
    app.prev = prev
    for kind, which, *rest in actions:
        if kind == "preset":
            app.press(which, rest[0])
        elif which == "conv":
            (app.conv_down if kind == "down" else app.conv_drag)(rest[0])
        else:
            sig = app.sx if which == "x" else app.sh
            x, y = rest
            if kind == "down":
                sig.modify(x, y)
            else:
                sig.drag(prev[which][0], prev[which][1], x, y)
            prev[which] = (x, y)
            app.sig_changed_event()


def scenario_names():
    return [s[0] for s in SCENARIOS] + [s[0] for s in ACTION_SCENARIOS]


def all_scenarios():
    app, out = Applet(), {}
    for name, xp, hp, draw in SCENARIOS:
        run_scenario(app, xp, hp, draw)
        out[name] = app.dump()
    for name, actions in ACTION_SCENARIOS:
        run_actions(app, actions)
        out[name] = app.dump()
    return out
