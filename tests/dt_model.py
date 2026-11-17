"""Reference model of the discrete-time applet's arithmetic, in Python.

An independent transcription, from the `javap -c` disassembly of DTConvolve.jar (Steven
Crutchfield 1997, update Michael Ross 2001; no source survives), of everything that decides
what the applet shows: the presets, mouse drawing, flipping and shifting x, the product, y[n],
and the y-axis autoscaling. The browser port (joy_of_convolution_dt.html) must produce the
same values, and when the original's output is present locally
(reference/captures/dt/*.json, from tools/DtProbe.java) this model must match it too.

Panel sizes are the original's: x/h panels 286 x 126, the three wide panels 582 x 126.
"""
import math

IN_W, IN_H = 286, 126
WIDE_W, WIDE_H = 582, 126
ZERO, PULSE, DECAY, SINE, RIGHT_PULSE, SQUARE_WAVE, UNIT_IMPULSE = range(7)
# Button tooltips -> signal types, in button order (DTConvolve.init)
PRESETS = {"Square pulse": RIGHT_PULSE, "One period of a square wave": SQUARE_WAVE,
           "Right-sided exponential": DECAY, "Unit Impulse": UNIT_IMPULSE, "Clear": ZERO}


def jround(v):
    """Java Math.round(double): floor(v + 0.5)."""
    return math.floor(v + 0.5)


class Signal:
    def __init__(self, lower, upper, max_index):
        self.lower, self.upper = (lower, upper) if lower < upper else (upper, lower)
        self.range = upper - lower
        self.res = 1.0
        self.max_index = max_index
        self.data = [0.0] * max_index
        self.max_value = self.min_value = 0.0

    @classmethod
    def copy(cls, src, lower, upper, max_index):
        """Signal(Signal, double, double, int): src centred in a longer array (no max/min copied)."""
        s = cls(lower, upper, max_index)
        diff = max_index - src.max_index
        if diff > 0:
            for i in range(max_index):
                if diff // 2 <= i < max_index - diff // 2:
                    j = i - diff // 2
                    if j < src.max_index:
                        s.data[i] = src.data[j]
        return s

    @classmethod
    def generate(cls, lower, upper, max_index, kind):
        s = cls(lower, upper, max_index)
        r = s.res
        if kind == ZERO:
            return s
        if kind == PULSE:
            x = lower / 3.0
            while x <= upper / 3.0:
                s.set_at(x, 2.0); x += r
        elif kind == DECAY:
            x = 0.0
            while x <= upper:
                s.set_at(x, 3.0 * math.exp(-x)); x += r
        elif kind == SINE:
            x = -6.0
            while x <= 6.0:
                s.set_at(x, 3.0 * math.sin(0.5 * x)); x += 1.0
        elif kind == RIGHT_PULSE:
            x = 0.0
            while x <= upper / 4.0:
                s.set_at(x, 2.0); x += r
        elif kind == SQUARE_WAVE:
            x = 0.0
            while x <= upper / 3.0:
                s.set_at(x, 2.0); x += r
            x = upper / 3.0
            while x <= 2.0 * upper / 3.0:
                s.set_at(x, -2.0); x += r
        elif kind == UNIT_IMPULSE:
            s.set_at(0.0, 1.0)
        return s

    def set_at(self, x, y):
        if x < self.lower or x > self.upper:
            return
        if y > self.max_value:
            self.max_value = y
        if y < self.min_value:
            self.min_value = y
        i = jround((x - self.lower) / self.res)
        if 0 <= i < self.max_index:
            self.data[i] = y

    def get_at(self, x):
        if x < self.lower or x > self.upper:
            return 0.0
        i = jround((x - self.lower) / self.res)
        return self.data[i] if 0 <= i < self.max_index else 0.0

    def _remap(self, f):
        new, x = [], self.lower
        for _ in range(self.max_index):
            new.append(f(x)); x += self.res
        self.data = new
        return self

    def x_shift_by(self, c):
        return self._remap(lambda x: self.get_at(x - c))

    def x_scale_by(self, b):
        return self._remap(lambda x: self.get_at(b * x))

    @staticmethod
    def multiply(s1, s2):
        out = Signal(s1.lower, s1.upper, s1.max_index)
        for i in range(s1.max_index):
            y = s1.data[i] * s2.data[i]
            if y > out.max_value:
                out.max_value = y
            if y < out.min_value:
                out.min_value = y
            out.data[i] = y
        return out

    @staticmethod
    def sum_terms(s):
        t = 0.0
        for v in s.data:
            t += v
        return t

    def fill_range_linear(self, x1, x2, y1, y2):
        if x1 > x2:
            x1, x2, y1, y2 = x2, x1, y2, y1
        slope = (y2 - y1) / (x2 - x1)
        cx = x1
        while cx <= x2:
            self.set_at(cx, slope * (cx - x1) + y1)
            cx += self.res

    def dump(self):
        return {"xmin": self.lower, "xmax": self.upper, "maxIndex": self.max_index,
                "data": list(self.data)}


class Applet:
    def __init__(self):
        self.x = Signal(-12.0, 12.0, 24)
        self.h = Signal(-12.0, 12.0, 24)
        self.s1 = Signal(-24.0, 24.0, 48)      # dual panel: x[n-k]
        self.s2 = Signal(-24.0, 24.0, 48)      # dual panel: h[k]
        self.n = 0
        self.hide_n = True
        self.product = Signal(-24.0, 24.0, 48)
        self.y = Signal(-24.0, 24.0, 48)
        self.product_axes = [-5.0, 5.0]
        self.y_axes = [-5.0, 5.0]
        self.reset = True
        self.old = (0.0, 0.0)                  # input-panel mouse listener's oldX, oldY
        self.old_n = 0                         # dual-panel mouse listener's oldN

    # --- DTConvolve.updateOutputPanels: x or h changed --------------------------------
    def update_output_panels(self):
        self.reset = True
        self.n = 0; self.hide_n = True
        self.s1 = Signal.copy(self.x, -24.0, 24.0, 48).x_shift_by(-self.n).x_scale_by(-1.0)
        self.s2 = Signal.copy(self.h, -24.0, 24.0, 48)
        A, a = self.x.max_value, self.x.min_value
        B, b = self.h.max_value, self.h.min_value
        if A * B > 0:
            new_max, new_min = A * B, a * b
            if a * B < new_min: new_min = a * B
            if A * b < new_min: new_min = A * b
        else:
            new_min, new_max = A * B, a * b
            if a * B > new_max: new_max = a * B
            if A * b > new_max: new_max = A * b
        temp = abs(new_max) if abs(new_max) > abs(new_min) else abs(new_min)
        div = int(temp / 5.0)
        if temp / 5.0 > div or div == 0:
            div += 1
        self.product_axes = [float(-5 * div), float(5 * div)]
        self.product = Signal.multiply(self.s1, self.s2)
        # y axis: the extremes over n of a sum that flips x a second time, so it is really
        # the cross-correlation's range, not the convolution's (a quirk of the original).
        new_min, new_max = -5.0, 5.0
        for n_index in range(-26, 25):
            t = Signal(-24.0, 24.0, 48)
            t.data = list(self.s1.data)
            t.x_shift_by(float(-1 * n_index)).x_scale_by(-1.0)
            v = Signal.sum_terms(Signal.multiply(t, self.s2))
            if v > new_max:
                new_max = v
            elif v < new_min:
                new_min = v
        temp = abs(new_max) if abs(new_max) > abs(new_min) else abs(new_min)
        div = jround(temp / 5.0)
        new_min, new_max = float(-5 * div), float(5 * div)
        if temp > new_max or temp < new_min:
            new_min -= 10.0; new_max += 10.0
        self.y.data = [0.0] * 48; self.y.max_value = self.y.min_value = 0.0
        self.y_axes = [new_min, new_max]

    # --- DTConvolve.nChanged: n moved -----------------------------------------------------
    def set_n(self, n):
        self.n = n
        self.reset = False
        self.s1 = Signal.copy(self.x, -24.0, 24.0, 48).x_shift_by(float(-self.n)).x_scale_by(-1.0)
        self.hide_n = False
        self.product = Signal.multiply(self.s1, self.s2)
        self.y.set_at(float(self.n), Signal.sum_terms(self.product))

    # --- mouse ------------------------------------------------------------------------------
    def preset(self, which, tip):
        s = Signal.generate(-12.0, 12.0, 24, PRESETS[tip])
        if which == "x": self.x = s
        else: self.h = s
        self.update_output_panels()

    @staticmethod
    def _xy(mx, my):
        return 24.0 * mx / IN_W + -12.0, -(10.0 * my / IN_H + -5.0)

    def draw_press(self, which, mx, my):
        sig = self.x if which == "x" else self.h
        x, y = self._xy(mx, my)
        sig.set_at(x, y)
        self.old = (x, y)
        self.update_output_panels()

    def draw_drag(self, which, mx, my):
        sig = self.x if which == "x" else self.h
        x, y = self._xy(mx, my)
        if self.old[0] == x:
            sig.set_at(x, y)
        else:
            sig.fill_range_linear(self.old[0], x, self.old[1], y)
        self.old = (x, y)
        self.update_output_panels()

    @staticmethod
    def _n(mx):
        return int(48.0 * mx / WIDE_W + -24.0)      # (int) truncates toward zero

    def dual_press(self, mx):
        self.old_n = self._n(mx)
        self.set_n(self.old_n)

    def dual_drag(self, mx):
        big = self._n(mx)
        if big < self.old_n:
            big, self.old_n = self.old_n, big
        for i in range(self.old_n, big + 1):
            self.set_n(i)

    def dump(self):
        return {"n": self.n, "x": self.x.dump(), "h": self.h.dump(), "dual_signal1": self.s1.dump(),
                "dual_signal2": self.s2.dump(), "product": self.product.dump(), "y": self.y.dump(),
                "product_axes": self.product_axes, "y_axes": self.y_axes, "reset": self.reset}


# tools/DtProbe.java's scripted actions (and the page's #selftest), in order.
SCENARIOS = [
    ("d1_pulse_pulse", "Square pulse", "Square pulse", False),
    ("d2_pulse_exponential", "Square pulse", "Right-sided exponential", False),
    ("d3_squarewave_exponential", "One period of a square wave", "Right-sided exponential", False),
    ("d4_impulse_squarewave", "Unit Impulse", "One period of a square wave", False),
    ("d5_drawn_exponential", "Clear", "Right-sided exponential", True),
]


def run_scenario(app, x_tip, h_tip, draw):
    app.preset("x", x_tip)
    app.preset("h", h_tip)
    if draw:
        w, h = IN_W, IN_H
        app.draw_press("x", w // 2, h // 2)
        for i in range(1, 21):
            app.draw_drag("x", w // 2 + i * (w // 2 - 4) // 20, h // 2 - i * (h // 4) // 20)
    app.dual_press(1)
    prev = 1
    for stop in (WIDE_W // 4, WIDE_W // 2, 3 * WIDE_W // 4, WIDE_W - 2):
        for mx in range(prev + 1, stop + 1):
            app.dual_drag(mx)
        prev = stop


def all_scenarios():
    app, out = Applet(), {}
    for name, xt, ht, draw in SCENARIOS:
        run_scenario(app, xt, ht, draw)
        out[name] = app.dump()
    return out
