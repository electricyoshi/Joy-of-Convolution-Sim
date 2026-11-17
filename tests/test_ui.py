"""Behaviour of both pages in a real browser that #selftest and the parity tests don't reach.

1. Event wiring: keyboard activation of the preset buttons, one pointer at a time (a second
   finger is ignored), a lost pointer release can't freeze the applet, only the panel the
   original listened to sets t / n, the rAF repaint and the screen-reader readout follow a
   click, and layout(z, dpr) rescales without touching the state.
2. Tooling: a mistyped #shot= scenario shows the red error bar instead of a wrong screenshot.
3. Drawing: at 1x, the pixels where the Python model says each signal sample lands are that
   signal's colour (and the panels the original leaves empty have none of those colours).
   This checks the paint code on any clone, without the original's captures; the pixel
   comparison with the original itself is tools/compare.py (local only).

Skipped without Chrome, Edge or Chromium.
"""
import json
import math
import unittest

import ct_model
import dt_model
from test_html_portable import CT, DT, dump_dom, error_text, find_browser, run_probe

needs_browser = unittest.skipUnless(find_browser(), "needs Chrome, Edge or Chromium installed")

# Colour classes for pixel checks. Lines and dots are antialiased against white, so a class
# is "this channel clearly dominates" rather than an exact value.
def blue(p): return p[2] - max(p[0], p[1]) >= 100
def red(p): return p[0] - max(p[1], p[2]) >= 100
def green(p): return p[1] - max(p[0], p[2]) >= 100
def green128(p): return p[1] - max(p[0], p[2]) >= 50          # CT decay preset, Color(0, 128, 0)
def black(p): return max(p) <= 110
def orange(p): return p[0] >= 200 and 120 <= p[1] <= 230 and p[2] <= 100   # #FFC800
def red_or_blue(p): return red(p) or blue(p)


# Headless Chrome may dump the page before any animation frame runs, so probes that test
# the coalesced repaint queue the page's requestAnimationFrame callbacks and run them with
# frame(). Installed before any action, so every repaint request lands in the queue.
FRAMES_JS = """
var queued = [];
window.requestAnimationFrame = function (f) { queued.push(f); return queued.length; };
function frame() { var q = queued; queued = []; q.forEach(function (f) { f(performance.now()); }); return q.length; }
"""


def rgb(key):
    return tuple(int(v) for v in key.split(","))


@needs_browser
class CtEvents(unittest.TestCase):
    def probe(self, js, **kw):
        got, err = run_probe(CT, "var a = JOC.applet, out = {};\n" + js, **kw)
        self.assertEqual(err, "", "page shows a script error")
        return got

    def test_keyboard_activates_presets(self):
        # Enter/Space on a focused button arrive as a click with detail 0; a click with detail 1
        # (what follows a pointer press, which already applied the preset) must not re-apply.
        got = self.probe("""
          a.signalX.buttons[1].el.focus(); a.signalX.buttons[1].el.click();      // double pulse
          a.signalH.buttons[2].el.click();                                       // decay
          a.signalH.buttons[3].el.dispatchEvent(new MouseEvent('click', { detail: 1, bubbles: true }));
          done(JOC.dump(a));""")
        m = ct_model.Applet()
        m.press("x", "double pulse"); m.press("h", "decay")
        self.assertEqual(got, m.dump())

    def test_one_pointer_at_a_time(self):
        got = self.probe("""
          fire(a.signalX.buttons[0], 'pointerdown', 5, 5); fire(a.signalH.buttons[2], 'pointerdown', 5, 5);
          var t1 = { pointerId: 7, pointerType: 'touch' }, t2 = { pointerId: 8, pointerType: 'touch' };
          var c = a.fConvPanel, x = a.signalX.panel;
          fire(c, 'pointerdown', 100, 10, t1);
          fire(x, 'pointerdown', 50, 10, t2);                    // second finger: ignored
          fire(x, 'pointermove', 80, 10, t2);
          fire(c, 'pointermove', 150, 10, t2);                   // not the finger that pressed
          fire(a.signalH.buttons[3], 'pointerdown', 5, 5, t2);   // presets too
          fire(c, 'pointermove', 200, 10, t1);
          fire(c, 'pointerup', 200, 10, t1);
          fire(x, 'pointerdown', 50, 10, t2);                    // first finger lifted: accepted
          done(JOC.dump(a));""")
        m = ct_model.Applet()
        m.press("x", "pulse"); m.press("h", "decay")
        m.conv_down(100); m.conv_drag(200)
        m.sx.modify(50, 10); m.sig_changed_event()
        self.assertEqual(got, m.dump())

    def test_a_lost_release_cannot_freeze_the_applet(self):
        got = self.probe("""
          var pen = { pointerId: 3, pointerType: 'pen' }, x = a.signalX.panel, h = a.signalH.panel;
          fire(x, 'pointerdown', 50, 10, pen);
          fire(x, 'pointermove', 60, 30, { pointerId: 3, pointerType: 'pen', buttons: 0 });  // released unseen
          fire(x, 'pointermove', 70, 30, pen);                                               // so no drag
          fire(h, 'pointerdown', 40, 40, { pointerId: 9, pointerType: 'touch' });           // never lifted
          fire(x, 'pointerdown', 90, 90, { pointerId: 10, pointerType: 'touch' });          // ignored
          fire(x, 'pointerdown', 20, 20);                        // but a mouse press always counts
          done(JOC.dump(a));""")
        m = ct_model.Applet()
        m.sx.modify(50, 10); m.sig_changed_event()
        m.sh.modify(40, 40); m.sig_changed_event()
        m.sx.modify(20, 20); m.sig_changed_event()
        self.assertEqual(got, m.dump())

    def test_only_the_conv_panel_sets_t(self):
        # QUIRKS.md CT 5: clicking the integrand or y(t) panels does nothing.
        got = self.probe("""
          fire(a.signalX.buttons[0], 'pointerdown', 5, 5); fire(a.signalH.buttons[0], 'pointerdown', 5, 5);
          [a.signalInt, a.signalY].forEach(function (p) {
            fire(p, 'pointerdown', 300, 20); fire(p, 'pointermove', 350, 20); fire(p, 'pointerup', 350, 20);
          });
          out.state = JOC.dump(a); out.sigChanged = a.fConvPanel.fSigChanged; done(out);""")
        m = ct_model.Applet()
        m.press("x", "pulse"); m.press("h", "pulse")
        self.assertEqual(got["state"], m.dump())
        self.assertTrue(got["sigChanged"])

    def test_click_repaints_and_updates_the_readout(self):
        # The repaint is coalesced into the next animation frame; so is the readout update.
        got = self.probe(FRAMES_JS + """
          fire(a.signalX.buttons[0], 'pointerdown', 5, 5); fire(a.signalH.buttons[0], 'pointerdown', 5, 5);
          a.signalY.painted = false;
          fire(a.fConvPanel, 'pointerdown', 294, 10); fire(a.fConvPanel, 'pointerup', 294, 10);
          out.before = document.getElementById('readout').textContent;
          out.frames = frame();                                    // presets + click: one frame
          out.after = document.getElementById('readout').textContent;
          out.painted = a.signalY.painted;
          fire(a.signalX.buttons[1], 'pointerdown', 5, 5);         // changing x clears it again
          frame();
          out.cleared = document.getElementById('readout').textContent;
          done(out);""")
        m = ct_model.Applet()
        m.press("x", "pulse"); m.press("h", "pulse")
        m.conv_down(294)
        t = (294 - 237) * 2 * math.pi / 474
        self.assertEqual(got["before"], "")
        self.assertEqual(got["frames"], 1, "repaints should coalesce into one animation frame")
        self.assertTrue(got["painted"], "y(t) panel not repainted in the next frame")
        self.assertEqual(got["after"], f"t = {t:.2f}, y(t) = {m.y[294] / 31:.2f}")
        self.assertEqual(got["cleared"], "")

    def test_layout_rescales_without_changing_state(self):
        got = self.probe("""
          JOC.runScenario(a, JOC.SCENARIOS[1], null);
          out.before = JOC.dump(a);
          a.layout(1.5, 2);
          out.after = JOC.dump(a);
          out.root = [a.root.style.width, a.root.style.height];
          out.sizes = a.comps.map(function (c) { return [c.bw, c.bh, c.canvas.width, c.canvas.height, c.el.style.width]; });
          done(out);""")
        self.assertEqual(got["before"], got["after"])
        self.assertEqual(got["root"], ["720px", "900px"])
        self.assertEqual(len(got["sizes"]), 13)
        for bw, bh, cw, ch, css in got["sizes"]:
            self.assertEqual((cw, ch), (round(bw * 3), round(bh * 3)))
            self.assertEqual(css, f"{bw * 1.5:g}px")

    def test_unknown_shot_name_shows_the_error_bar(self):
        err = error_text(dump_dom(CT, "#shot=s3_doublepulse_decy:c"))
        self.assertIn('unknown #shot scenario "s3_doublepulse_decy"', err)


@needs_browser
class DtEvents(unittest.TestCase):
    def probe(self, js, **kw):
        got, err = run_probe(DT, "var a = JOC.applet, out = {};\n" + js, **kw)
        self.assertEqual(err, "", "page shows a script error")
        return got

    def test_keyboard_activates_presets(self):
        got = self.probe("""
          a.buttons.x[1].el.focus(); a.buttons.x[1].el.click();              // square wave
          a.buttons.h[2].el.click();                                         // exponential
          a.buttons.h[4].el.dispatchEvent(new MouseEvent('click', { detail: 1, bubbles: true }));
          done(JOC.dump(a));""")
        m = dt_model.Applet()
        m.preset("x", "One period of a square wave"); m.preset("h", "Right-sided exponential")
        self.assertEqual(got, m.dump())

    def test_one_pointer_at_a_time(self):
        got = self.probe("""
          fire(a.buttons.x[0], 'pointerdown', 5, 5); fire(a.buttons.h[2], 'pointerdown', 5, 5);
          var t1 = { pointerId: 7, pointerType: 'touch' }, t2 = { pointerId: 8, pointerType: 'touch' };
          var d = a.xhDualPanel, x = a.xInputPanel;
          fire(d, 'pointerdown', 250, 60, t1);
          fire(x, 'pointerdown', 50, 10, t2);
          fire(x, 'pointermove', 80, 10, t2);
          fire(d, 'pointermove', 400, 60, t2);
          fire(a.buttons.h[4], 'pointerdown', 5, 5, t2);
          fire(d, 'pointermove', 330, 60, t1);
          fire(d, 'pointerup', 330, 60, t1);
          fire(x, 'pointerdown', 50, 10, t2);
          done(JOC.dump(a));""")
        m = dt_model.Applet()
        m.preset("x", "Square pulse"); m.preset("h", "Right-sided exponential")
        m.dual_press(250); m.dual_drag(330)
        m.draw_press("x", 50, 10)
        self.assertEqual(got, m.dump())

    def test_a_lost_release_cannot_freeze_the_applet(self):
        got = self.probe("""
          var pen = { pointerId: 3, pointerType: 'pen' }, x = a.xInputPanel, h = a.hInputPanel;
          fire(x, 'pointerdown', 50, 10, pen);
          fire(x, 'pointermove', 90, 30, { pointerId: 3, pointerType: 'pen', buttons: 0 });
          fire(x, 'pointermove', 120, 30, pen);
          fire(h, 'pointerdown', 40, 40, { pointerId: 9, pointerType: 'touch' });
          fire(x, 'pointerdown', 200, 90, { pointerId: 10, pointerType: 'touch' });
          fire(x, 'pointerdown', 20, 20);
          done(JOC.dump(a));""")
        m = dt_model.Applet()
        m.draw_press("x", 50, 10); m.draw_press("h", 40, 40); m.draw_press("x", 20, 20)
        self.assertEqual(got, m.dump())

    def test_only_the_dual_panel_sets_n(self):
        got = self.probe("""
          fire(a.buttons.x[0], 'pointerdown', 5, 5); fire(a.buttons.h[0], 'pointerdown', 5, 5);
          [a.xhOutputPanel, a.yOutputPanel].forEach(function (p) {
            fire(p, 'pointerdown', 300, 20); fire(p, 'pointermove', 350, 20); fire(p, 'pointerup', 350, 20);
          });
          done(JOC.dump(a));""")
        m = dt_model.Applet()
        m.preset("x", "Square pulse"); m.preset("h", "Square pulse")
        self.assertEqual(got, m.dump())

    def test_click_repaints_and_updates_the_readout(self):
        got = self.probe(FRAMES_JS + """
          fire(a.buttons.x[0], 'pointerdown', 5, 5); fire(a.buttons.h[0], 'pointerdown', 5, 5);
          var painted = 0, orig = a.paintAll;
          a.paintAll = function () { painted++; return orig.apply(this, arguments); };
          fire(a.xhDualPanel, 'pointerdown', 340, 60); fire(a.xhDualPanel, 'pointerup', 340, 60);
          out.before = document.getElementById('readout').textContent;
          out.frames = frame();
          out.after = document.getElementById('readout').textContent;
          out.painted = painted;
          fire(a.buttons.x[1], 'pointerdown', 5, 5);
          frame();
          out.cleared = document.getElementById('readout').textContent;
          done(out);""")
        m = dt_model.Applet()
        m.preset("x", "Square pulse"); m.preset("h", "Square pulse")
        m.dual_press(340)
        self.assertEqual(got["before"], "")
        self.assertEqual(got["frames"], 1, "repaints should coalesce into one animation frame")
        self.assertEqual(got["painted"], 1, "expected exactly one coalesced repaint")
        self.assertEqual(got["after"], f"n = {m.n}, y[n] = {m.y.get_at(float(m.n)):.2f}")
        self.assertEqual(got["cleared"], "")

    def test_layout_rescales_without_changing_state(self):
        got = self.probe("""
          JOC.runScenario(a, JOC.SCENARIOS[1], null);
          out.before = JOC.dump(a);
          a.layout(1.5, 2);
          out.after = JOC.dump(a);
          out.root = [a.root.style.width, a.root.style.height];
          out.sizes = a.comps.map(function (c) { return [c.bw, c.bh, c.canvas.width, c.canvas.height, !!c.tip]; });
          done(out);""")
        self.assertEqual(got["before"], got["after"])
        self.assertEqual(got["root"], ["900px", "900px"])
        self.assertEqual(len(got["sizes"]), 15)
        for bw, bh, cw, ch, icon in got["sizes"]:
            self.assertEqual((cw, ch), (round(29 * 3), round(21 * 3)) if icon else (round(bw * 3), round(bh * 3)))

    def test_unknown_shot_name_shows_the_error_bar(self):
        err = error_text(dump_dom(DT, "#shot=d9_nothing"))
        self.assertIn('unknown #shot scenario "d9_nothing"', err)


# --- drawing -------------------------------------------------------------------------------

PIXELS_JS = """
var req = %s, panels = %s, out = { size: {}, at: {}, colours: {} };
function canvas(k) { return eval(panels[k]).canvas; }
function data(k) { var c = canvas(k); out.size[k] = [c.width, c.height]; return c.getContext('2d').getImageData(0, 0, c.width, c.height).data; }
Object.keys(req.at).forEach(function (k) {
  var d = data(k), w = canvas(k).width;
  out.at[k] = req.at[k].map(function (p) { var i = (p[1] * w + p[0]) * 4; return [d[i], d[i + 1], d[i + 2]]; });
});
req.whole.forEach(function (k) {
  var d = data(k), n = {};
  for (var i = 0; i < d.length; i += 4) { var key = d[i] + ',' + d[i + 1] + ',' + d[i + 2]; n[key] = (n[key] || 0) + 1; }
  out.colours[k] = n;
});
done(out);
"""


class PixelCase(unittest.TestCase):
    PAGE = None
    PANELS = {}      # panel name -> JS expression for its component (with a = JOC.applet)
    SIZES = {}       # panel name -> (w, h) in applet pixels

    def pixels(self, shot, at, whole=()):
        js = "var a = JOC.applet;\n" + PIXELS_JS % (json.dumps({"at": at, "whole": list(whole)}),
                                                   json.dumps(self.PANELS))
        got, err = run_probe(self.PAGE, js, fragment="#shot=" + shot)
        self.assertEqual(err, "", "page shows a script error")
        for k, size in got["size"].items():
            self.assertEqual(tuple(size), self.SIZES[k], f"{k}: #shot pages draw at 1x")
        return got

    def check(self, shot, expect, whole=(), min_share=0.95):
        """expect: panel -> list of ((x, y), predicate, label). Each panel needs min_share of
        its points to pass; a broken paint routine fails nearly all of them."""
        at = {k: [list(p) for p, _, _ in pts] for k, pts in expect.items()}
        got = self.pixels(shot, at, whole)
        for k, pts in expect.items():
            self.assertGreater(len(pts), 10, f"{shot} {k}: too few points to mean anything")
            bad = [(p, lab, tuple(c)) for (p, ok, lab), c in zip(pts, got["at"][k]) if not ok(c)]
            share = 1 - len(bad) / len(pts)
            self.assertGreaterEqual(share, min_share, f"{shot} {k}: {len(bad)}/{len(pts)} wrong, e.g. {bad[:6]}")
        return got

    def inside(self, k, x, y):
        w, h = self.SIZES[k]
        return 0 <= x < w and 0 <= y < h


@needs_browser
class CtDrawing(PixelCase):
    PAGE = CT
    PANELS = {"x": "a.signalX.panel", "h": "a.signalH.panel", "conv": "a.fConvPanel",
              "integ": "a.signalInt", "y": "a.signalY"}
    SIZES = {"x": (234, 124), "h": (234, 124), "conv": (474, 124), "integ": (474, 124), "y": (474, 174)}
    Y_SCALE = 174 / 2 / 62          # ConvSigPanel.paint: height / 2 / conv fAmplitude

    def expected(self, s, x_colour=blue):
        """Where every drawn sample of state s (a model dump) lands, and its colour."""
        e = {k: [] for k in self.PANELS}
        for k, arr, col in (("x", s["x"], x_colour), ("h", s["h"], red), ("integ", s["integrand"], black)):
            for i, v in enumerate(arr):
                if self.inside(k, i, 62 - v):
                    e[k].append(((i, 62 - v), col, f"{k}[{i}]"))
        shown = s["y_shown"]
        for i, v in enumerate(s["y"]):
            row = 87 - math.trunc(self.Y_SCALE * v)
            linked = shown[i] and ((i > 0 and shown[i - 1]) or (i < 473 and shown[i + 1]))
            if linked and self.inside("y", i, row):
                e["y"].append(((i, row), black, f"y[{i}]"))
        off, t = s["fOffset"], s["fT"]
        for i, v in enumerate(s["h"]):                 # h(v): red, under the blue x(t - v)
            nz = v or (i > 0 and s["h"][i - 1]) or (i < 233 and s["h"][i + 1])
            if nz and self.inside("conv", off + i, 62 - v):
                e["conv"].append(((off + i, 62 - v), red_or_blue, f"h({i})"))
        for i, v in enumerate(s["x"]):                 # x(t - v): blue, flipped, slid to t
            nz = v or (i > 0 and s["x"][i - 1]) or (i < 233 and s["x"][i + 1])
            col = t - off - i
            if nz and self.inside("conv", col, 62 - v):
                e["conv"].append(((col, 62 - v), blue, f"x(t-{i})"))
        return {k: v for k, v in e.items() if v}

    def test_swept_scenarios_draw_every_sample(self):
        model = ct_model.all_scenarios()
        for name, x_colour in (("s3_doublepulse_decay", blue), ("s7_left_and_outside", blue)):
            with self.subTest(name):
                exp = self.expected(model[name], x_colour)
                self.assertEqual(set(exp), set(self.PANELS))
                self.check(name, exp)

    def test_y_is_drawn_only_where_revealed(self):
        # s9 reveals y at four clicked t values only (QUIRKS.md CT 3): every other y sample
        # must be absent, i.e. the pixel where it would be is not black.
        s = ct_model.all_scenarios()["s9_clicks"]
        pts = []
        for i, v in enumerate(s["y"]):
            row = 87 - math.trunc(self.Y_SCALE * v)
            near_click = any(abs(i - c) <= 5 for c in (0, 100, 300, 473))
            busy = (abs(row - 87) <= 2 or 230 <= i <= 260 or i >= 455 or (i < 152 and row < 52))
            if not s["y_shown"][i] and not near_click and not busy and self.inside("y", i, row):
                pts.append(((i, row), lambda p: not black(p), f"hidden y[{i}]"))
        self.check("s9_clicks", {"y": pts}, min_share=0.99)

    def test_cleared_state_hides_the_convolution(self):
        # s8: x changed after a sweep, so the conv panel shows only its axes and labels, and the
        # integrand is an empty black line along its axis (QUIRKS.md CT 4 and 9).
        s = ct_model.all_scenarios()["s8_cleared"]
        exp = self.expected(s, x_colour=blue)
        got = self.check("s8_cleared", {"x": exp["x"], "integ": exp["integ"]}, whole=("conv",))
        coloured = {c: n for c, n in got["colours"]["conv"].items() if red(rgb(c)) or blue(rgb(c))}
        self.assertEqual(coloured, {}, "conv panel draws signals while they are being changed")


@needs_browser
class DtDrawing(PixelCase):
    PAGE = DT
    PANELS = {"x": "a.xInputPanel", "h": "a.hInputPanel", "dual": "a.xhDualPanel",
              "product": "a.xhOutputPanel", "y": "a.yOutputPanel"}
    SIZES = {"x": (286, 126), "h": (286, 126), "dual": (582, 126), "product": (582, 126), "y": (582, 126)}

    @staticmethod
    def stems(sig, w, h, min_y):
        """GraphPanel.drawSignal: (x, y) of each dot centre, one per index plus one at maxX."""
        n = sig["maxIndex"]
        out = []
        for i in range(n + 1):
            v = sig["data"][i] if i < n else 0.0
            out.append((dt_model.jround(w * i / n), dt_model.jround(h * (0.5 + 0.5 * v / min_y))))
        return out

    def expected(self, s):
        e = {}
        for k, sig, col, min_y in (("x", s["x"], green, -5.0), ("h", s["h"], blue, -5.0),
                                   ("product", s["product"], orange, s["product_axes"][0]),
                                   ("y", s["y"], red, s["y_axes"][0])):
            w, h = self.SIZES[k]
            pts = self.stems(sig, w, h, min_y)
            if k == "y":                      # the equation box (drawn last) hides the top left
                pts = [p for p in pts if not (p[0] <= 155 and p[1] <= 46)]
            e[k] = [(p, col, f"{k}[{i}]") for i, p in enumerate(pts) if self.inside(k, *p)]
        w, h = self.SIZES["dual"]
        half = dt_model.jround(h / 2.0)
        blue_pts = self.stems(s["dual_signal2"], w, h, -5.0)
        dual = [(p, blue, f"h[{i}]") for i, p in enumerate(blue_pts) if self.inside("dual", *p)]
        for i, p in enumerate(self.stems(s["dual_signal1"], w, h, -5.0)):
            yb = blue_pts[i][1]               # h's stem and dot are drawn over x[n - k]'s
            if not (min(yb, half) - 2 <= p[1] <= max(yb, half) + 2) and self.inside("dual", *p):
                dual.append((p, green, f"x[n-{i}]"))
        e["dual"] = dual
        return e

    def test_swept_scenarios_draw_every_sample(self):
        model = dt_model.all_scenarios()
        for name in ("d3_squarewave_exponential", "d6_left_and_outside"):
            with self.subTest(name):
                self.check(name, self.expected(model[name]))

    def test_cleared_state_hides_the_lower_panels(self):
        # d7: x changed, so the three lower panels show axes only until the next click.
        s = dt_model.all_scenarios()["d7_cleared"]
        self.assertTrue(s["reset"])
        exp = self.expected(s)
        got = self.check("d7_cleared", {"x": exp["x"], "h": exp["h"]}, whole=("dual", "product", "y"))
        for k in ("dual", "product", "y"):
            coloured = {c: n for c, n in got["colours"][k].items()
                        if green(rgb(c)) or blue(rgb(c)) or orange(rgb(c)) or red(rgb(c))}
            self.assertEqual(coloured, {}, f"{k} panel draws signals while reset")


if __name__ == "__main__":
    unittest.main()
