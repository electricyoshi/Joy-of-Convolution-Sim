"""Is the reference model (tests/ct_model.py) right?

1. Analytic checks that need nothing but this repo: pulse * pulse is a triangle of known
   height and width, pulse * decay follows the closed form, a double pulse has zero net
   area, and mouse drawing interpolates like the Java code.
2. When the original applet's own output is present locally (reference/captures/ct/*.json,
   written by tools/CtProbe.java; gitignored because it is JHU material), the model must
   reproduce it exactly. Skipped on a fresh clone.
"""
import json
import math
import pathlib
import unittest

import ct_model as m

ROOT = pathlib.Path(__file__).resolve().parent.parent
ORACLE = ROOT / "reference" / "captures" / "ct"
DX = 2 * math.pi / m.CONV_N         # the original's integration step
ONE = m.AMP // 2                    # 31 px is "1" (the +1 tick)


class Presets(unittest.TestCase):
    def test_pulse_is_one_on_58_samples_from_the_origin(self):
        s = m.Signal(); s.pulse()
        on = [i for i, v in enumerate(s.x) if v]
        self.assertEqual((on[0], on[-1]), (117, 174))
        self.assertTrue(all(s.x[i] == ONE for i in on))

    def test_double_pulse_has_zero_net_area_and_last_sample_zero(self):
        s = m.Signal(); s.double_pulse()
        self.assertEqual(sum(s.x), 0)
        self.assertEqual(s.x[-1], 0)            # second half stops at N - 1 (as in the original)
        self.assertEqual(s.x[117], -ONE)
        self.assertEqual(s.x[232], ONE)

    def test_decay_starts_at_one_and_falls_as_exp(self):
        s = m.Signal(); s.decay()
        self.assertEqual(s.x[117], ONE)
        self.assertEqual(s.x[116], 0)
        for i in range(117, 234):
            exact = 31 * math.exp(-4.0 * (i - 117) / 234)
            self.assertTrue(0 <= exact - s.x[i] < 1, i)    # int truncation only


class Convolution(unittest.TestCase):
    def conv(self, xp, hp):
        a = m.Applet()
        a.press("x", xp); a.press("h", hp)
        a.conv_down(0)
        return a

    def test_pulse_pulse_is_the_triangle(self):
        # Two 58-sample pulses: overlap count 58 - |k - 57| at shift k; t index 237 is t = 0.
        a = self.conv("pulse", "pulse")
        for t in range(m.CONV_N):
            overlap = max(0, 58 - abs(t - 237 - 57))
            self.assertEqual(a.y[t], int(overlap * ONE * ONE * DX * a.scale), t)
        # Peak height in units of the +1 tick = pulse width in the integral's time units.
        self.assertAlmostEqual(max(a.y) / ONE, 58 * DX, delta=1 / ONE)

    def test_pulse_decay_matches_closed_form(self):
        # y(tau) = integral over the pulse of exp(-c v) dv, with c per sample = 4 / 234.
        a = self.conv("pulse", "decay")
        c = 4.0 / 234
        for t in range(m.CONV_N):
            k = t - 237                      # shift in samples
            lo, hi = max(0, k - 57), k       # h samples s with 0 <= k - s <= 57
            if hi < 0:
                exact = 0.0
            else:
                exact = sum(math.exp(-c * s) for s in range(lo, hi + 1)) * ONE * ONE * DX * a.scale
            # Each of the 58 h samples is truncated by < 1 px (58 * 31 * DX * scale = 1.8 px
            # in y), plus < 1 px for the final (int) cast.
            self.assertLessEqual(abs(a.y[t] - exact), 2.8, t)

    def test_y_is_zero_before_t_zero_for_causal_signals(self):
        a = self.conv("pulse", "decay")
        self.assertTrue(all(v == 0 for v in a.y[:237]))

    def test_double_pulse_output_returns_to_zero(self):
        a = self.conv("double pulse", "pulse")
        # double pulse spans 116 samples, pulse 58: no overlap from shift 115 + 58 + 1 on
        self.assertTrue(all(v == 0 for v in a.y[237 + 174:]))
        self.assertNotEqual(a.y[237 + 170], 0)   # 3-sample overlap = 1.2 px; 1 or 2 truncate to 0

    def test_commutative_up_to_truncation(self):
        a, b = self.conv("double pulse", "decay"), self.conv("decay", "double pulse")
        self.assertLessEqual(max(abs(p - q) for p, q in zip(a.y, b.y)), 1)


class Drawing(unittest.TestCase):
    def test_drag_interpolates_with_java_int_division(self):
        s = m.Signal()
        s.drag(10, 62, 20, 0)      # 62 px up over 10 samples
        self.assertEqual(s.x[10:21], [0, 6, 12, 18, 24, 31, 37, 43, 49, 55, 62])

    def test_end_samples_are_locked(self):
        s = m.Signal()
        s.modify(0, 0); s.modify(233, 0); s.modify(1, 0)
        self.assertEqual((s.x[0], s.x[233], s.x[1]), (0, 0, 62))

    def test_values_are_not_clamped(self):
        s = m.Signal()
        s.modify(5, -40)           # dragged above the panel
        self.assertEqual(s.x[5], 102)

    def test_jdiv_truncates_toward_zero(self):
        self.assertEqual((m.jdiv(-7, 2), m.jdiv(7, -2), m.jdiv(7, 2)), (-3, -3, 3))


@unittest.skipUnless(ORACLE.is_dir(), "original applet captures not present (reference/ is local only)")
class MatchesOriginal(unittest.TestCase):
    def test_every_scenario_is_identical(self):
        mine = m.all_scenarios()
        for name in m.scenario_names():
            f = ORACLE / f"{name}.json"
            self.assertTrue(f.is_file(), f"{f.name} missing: re-run tools/CtProbe.java (CLAUDE.md)")
            ref = json.loads(f.read_text(encoding="utf-8"))
            for key, val in mine[name].items():
                self.assertEqual(val, ref[key], f"{name}.{key}")


if __name__ == "__main__":
    unittest.main()
