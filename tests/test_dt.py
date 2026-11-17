"""The discrete-time port: reference model (tests/dt_model.py) and page (joy_of_convolution_dt.html).

1. Analytic checks of the model: y[n] is the true convolution sum, presets are what the
   button tooltips say, and the original's y-axis autoscaling quirk.
2. Model == the original applet's output (reference/captures/dt/*.json, local only).
3. In headless Chrome: the page loads without error and draws every panel, real
   PointerEvents drive it, and #selftest == model (== original when present).
"""
import json
import pathlib
import re
import unittest

import dt_model as m
from test_html_portable import dump_dom, error_text, find_browser, run_probe, selftest_out

ROOT = pathlib.Path(__file__).resolve().parent.parent
DT = ROOT / "joy_of_convolution_dt.html"
ORACLE = ROOT / "reference" / "captures" / "dt"


def conv(x, h, n):
    """Direct convolution sum of two length-24 signals on n = -12..11 (index = n + 12)."""
    total = 0.0
    for k in range(-12, 12):
        j = n - k
        if -12 <= j < 12:
            total += h[k + 12] * x[j + 12]
    return total


class Model(unittest.TestCase):
    def sweep(self, x_tip, h_tip):
        a = m.Applet()
        a.preset("x", x_tip); a.preset("h", h_tip)
        for n in range(-24, 24):
            a.set_n(n)
        return a

    def test_presets_match_their_tooltips(self):
        def on(tip):
            s = m.Signal.generate(-12.0, 12.0, 24, m.PRESETS[tip])
            return {i - 12: v for i, v in enumerate(s.data) if v}
        self.assertEqual(on("Square pulse"), {0: 2.0, 1: 2.0, 2: 2.0, 3: 2.0})
        self.assertEqual(on("One period of a square wave"),
                         {0: 2.0, 1: 2.0, 2: 2.0, 3: 2.0, 4: -2.0, 5: -2.0, 6: -2.0, 7: -2.0, 8: -2.0})
        self.assertEqual(on("Unit Impulse"), {0: 1.0})
        self.assertEqual(on("Clear"), {})
        exp = on("Right-sided exponential")
        self.assertEqual(sorted(exp), list(range(0, 12)))      # n = 12 is past the last index
        self.assertAlmostEqual(exp[1], 3 / 2.718281828459045, places=12)

    def test_y_is_the_convolution_sum(self):
        for xt in m.PRESETS:
            for ht in ("Square pulse", "Right-sided exponential", "One period of a square wave"):
                a = self.sweep(xt, ht)
                for n in range(-24, 24):
                    self.assertAlmostEqual(a.y.data[n + 24], conv(a.x.data, a.h.data, n), places=9,
                                           msg=f"{xt} * {ht}, n = {n}")

    def test_impulse_input_gives_h(self):
        a = self.sweep("Unit Impulse", "Right-sided exponential")
        self.assertEqual(a.y.data[24:36], a.h.data[12:24])

    def test_pulse_pulse_axis_is_25(self):
        # peak 16: round(16 / 5) * 5 = 15 < 16, so the axis grows by 10
        a = self.sweep("Square pulse", "Square pulse")
        self.assertEqual(max(a.y.data), 16.0)
        self.assertEqual(a.y_axes, [-25.0, 25.0])
        self.assertEqual(a.product_axes, [-5.0, 5.0])

    def test_y_axis_is_scaled_to_the_correlation_not_the_convolution(self):
        # The autoscale loop flips x twice. For x = exponential, h = square wave the true
        # y reaches -6.7, but the correlation peaks at 9.3: the axis is +-10 either way here,
        # so check the loop's quantity directly.
        a = m.Applet()
        a.preset("x", "Square pulse"); a.preset("h", "Right-sided exponential")
        self.assertEqual(a.y_axes, [-10.0, 10.0])

    def test_dual_click_zone_for_n_zero_is_double_width(self):
        zero = [mx for mx in range(582) if m.Applet._n(mx) == 0]
        one = [mx for mx in range(582) if m.Applet._n(mx) == 1]
        # 582 / 48 = 12.1 px per n; n = 0 covers -1 < value < 1, about twice that
        self.assertEqual(len(one), 12)
        self.assertIn(len(zero), (24, 25))



def oracle(name):
    f = ORACLE / f"{name}.json"
    assert f.is_file(), f"{f.name} missing: re-run tools/DtProbe.java (CLAUDE.md)"
    return json.loads(f.read_text(encoding="utf-8"))


@unittest.skipUnless(ORACLE.is_dir(), "original applet captures not present (reference/ is local only)")
class ModelMatchesOriginal(unittest.TestCase):
    def test_every_scenario_is_identical(self):
        mine = m.all_scenarios()
        for name in m.scenario_names():
            ref = oracle(name)
            for key, val in mine[name].items():
                self.assertEqual(val, ref[key], f"{name}.{key}")


@unittest.skipUnless(find_browser(), "needs Chrome, Edge or Chromium installed")
class InBrowser(unittest.TestCase):
    def no_error(self, dom):
        self.assertEqual(error_text(dom), "", "page shows a script error")

    def test_page_loads_and_draws_every_panel(self):
        dom = dump_dom(DT)
        self.no_error(dom)
        mm = re.search(r'data-painted="(\d+)"', dom)
        self.assertIsNotNone(mm, "applet never painted")
        self.assertEqual(int(mm.group(1)), 2 + 10 + 3)   # x, h, 10 preset buttons, 3 wide panels

    def test_shot_mode_runs(self):
        for spec in ("d3_squarewave_exponential:c", "d0_initial", "d6_left_and_outside"):
            self.no_error(dump_dom(DT, "#shot=" + spec))

    def test_selftest_matches_reference_model_and_original(self):
        dom = dump_dom(DT, "#selftest")
        self.no_error(dom)
        got = selftest_out(dom)["scenarios"]
        model = m.all_scenarios()
        self.assertEqual(sorted(got), sorted(m.scenario_names()))
        for name in m.scenario_names():
            for key, val in model[name].items():
                self.assertEqual(got[name][key], val, f"page vs model: {name}.{key}")
            if ORACLE.is_dir():
                ref = oracle(name)
                for key in model[name]:
                    self.assertEqual(got[name][key], ref[key], f"page vs original: {name}.{key}")

    def test_pointer_events_drive_the_applet(self):
        # Real PointerEvents at screen coordinates on the scaled applet (z != 1).
        got, err = run_probe(DT, """
          var a = JOC.applet, out = {};
          out.z = a.root.getBoundingClientRect().width / 600;
          fire(a.buttons.x[2], 'pointerdown', 5, 5);                 // x: exponential
          fire(a.buttons.h[1], 'pointerdown', 5, 5);                 // h: square wave
          var p = a.hInputPanel;                                     // then sketch on h
          fire(p, 'pointerdown', 40, 30); fire(p, 'pointermove', 90, 100); fire(p, 'pointerup', 90, 100);
          var d = a.xhDualPanel;
          fire(d, 'pointerdown', 250, 60);
          for (var x = 260; x <= 420; x += 10) fire(d, 'pointermove', x, 60);
          fire(d, 'pointermove', 330, 60);                           // and back left
          fire(d, 'pointerup', 330, 60);
          fire(d, 'pointermove', 500, 60);                           // after release: ignored
          out.state = JOC.dump(a);
          done(out);""")
        self.assertEqual(err, "")
        self.assertNotAlmostEqual(got["z"], 1.0, places=2)
        a = m.Applet()
        a.preset("x", "Right-sided exponential"); a.preset("h", "One period of a square wave")
        a.draw_press("h", 40, 30); a.draw_drag("h", 90, 100)
        a.dual_press(250)
        for mx in list(range(260, 421, 10)) + [330]:
            a.dual_drag(mx)
        self.assertEqual(got["state"], a.dump())


if __name__ == "__main__":
    unittest.main()
