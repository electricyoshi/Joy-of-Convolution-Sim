"""Will joy_of_convolution.html open on a student's laptop, and does it compute what the
original computed?

Static checks (always run): one self-contained file, nothing fetched, no syntax that older
Safari can't parse. Browser checks (skipped when no Chrome, Edge or Chromium is installed):
load the page from file:// in headless Chrome, confirm no script error and every panel drawn,
then run its #selftest (the tools/CtProbe.java scenarios) and require the arrays to equal the
Python reference model's, and the original applet's when reference/ is present locally.
"""
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

import ct_model

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = [ROOT / "joy_of_convolution.html", ROOT / "index.html", ROOT / "joy_of_convolution_dt.html"]
CT = PAGES[0]
ORACLE = ROOT / "reference" / "captures" / "ct"
# The only URLs allowed in the pages: plain links back to the original JHU site.
ALLOWED_URL = re.compile(r"https://pages\.jh\.edu/signals/[\w./-]*")


def find_browser():
    for n in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge", "microsoft-edge"):
        if shutil.which(n):
            return shutil.which(n)
    paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    for env in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        base = os.environ.get(env)
        if base:
            paths += [os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"),
                      os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe")]
    return next((p for p in paths if os.path.exists(p)), None)


def dump_dom(page, fragment=""):
    out = subprocess.run([find_browser(), "--headless=new", "--disable-gpu", "--dump-dom",
                          page.as_uri() + fragment],
                         capture_output=True, timeout=120, check=True)
    return out.stdout.decode("utf-8")


class Static(unittest.TestCase):
    def pages(self):
        for p in PAGES:
            raw = p.read_bytes()
            yield p.name, raw, raw.decode("utf-8")      # fails here if it isn't valid UTF-8

    def test_encoding_declared_and_no_bom(self):
        for name, raw, text in self.pages():
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), name)
            self.assertTrue(text.lstrip().lower().startswith("<!doctype html>"), name)
            self.assertIn('<meta charset="utf-8">', text[:1024], name)

    def test_nothing_is_loaded_from_anywhere(self):
        # works offline from a double-click: no external scripts, styles, fonts, images,
        # modules or network calls (and no JHU images)
        for name, _, text in self.pages():
            for pat in (r"<script[^>]+src=", r"<link\b", r"<img\b", r"<iframe\b", r"<audio\b",
                        r"@import", r"url\(", r"\bimport\s*\(", r"\bfetch\s*\(", r"XMLHttpRequest",
                        r'type="module"', r"\.gif\b", r"\.jpg\b", r"\.mp3\b", r"\.class\b"):
                self.assertIsNone(re.search(pat, text, re.I), f"{name}: {pat}")
            leftover = ALLOWED_URL.sub("", text)
            self.assertIsNone(re.search(r"(https?:)?//[\w-]+\.[\w.-]+", leftover), name)

    def test_no_syntax_that_breaks_older_safari(self):
        for name, _, text in self.pages():
            script = "".join(re.findall(r"<script>(.*?)</script>", text, re.S))
            script = re.sub(r"//[^\n]*", "", script)        # comments may mention #selftest etc.
            for pat, why in ((r"\bstatic\s+\w+\s*=", "static class fields (Safari < 14.1)"),
                             (r"\?\.", "optional chaining (Safari < 13.1)"),
                             (r"\?\?", "nullish coalescing (Safari < 13.1)"),
                             (r"(?<!['\"])#\w+\s*[=(;]", "private class members (Safari < 14.1)"),
                             (r"\.at\(", "Array.at (Safari < 15.4)"),
                             (r"\.replaceAll\(", "replaceAll (Safari < 13.1)"),
                             (r"structuredClone", "structuredClone (Safari < 15.4)")):
                self.assertIsNone(re.search(pat, script), f"{name}: {why}")
            self.assertNotIn("inset:", text, f"{name}: CSS inset (Safari < 14.1)")

    def test_error_banner_comes_before_the_main_script(self):
        text = CT.read_text(encoding="utf-8")
        self.assertLess(text.index("window.onerror"), text.index("'use strict'"))

    def test_credits_on_every_page(self):
        for name, _, text in self.pages():
            for who in ("Steven Crutchfield", "Johns Hopkins University", "Wilson J. Rugh",
                        "Michael Ross", "Work in progress"):
                self.assertIn(who, text, f"{name}: {who}")


@unittest.skipUnless(find_browser(), "needs Chrome, Edge or Chromium installed")
class InBrowser(unittest.TestCase):
    def no_error(self, dom):
        m = re.search(r'<div id="err"[^>]*>(.*?)</div>', dom, re.S)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1).strip(), "", "page shows a script error")

    def test_page_loads_and_draws_every_panel(self):
        dom = dump_dom(CT)
        self.no_error(dom)
        m = re.search(r'data-painted="(\d+)"', dom)
        self.assertIsNotNone(m, "applet never painted")
        self.assertEqual(int(m.group(1)), 2 * 5 + 3)   # x, h, 8 buttons, conv, integrand, y

    def test_index_page_loads(self):
        self.no_error(dump_dom(PAGES[1]))

    def test_shot_mode_runs(self):
        self.no_error(dump_dom(CT, "#shot=s3_doublepulse_decay:c"))

    def test_pointer_events_drive_the_applet(self):
        # Real PointerEvents at screen coordinates (the applet is scaled, z != 1): exercises
        # the event wiring and the screen-to-applet coordinate mapping, which #selftest skips.
        probe = """<script>
        (function () {
          var a = JOC.applet, out = {};
          function at(comp, lx, ly) {
            var r = comp.el.getBoundingClientRect();
            return { clientX: r.left + (lx + 0.5) * r.width / comp.bw,
                     clientY: r.top + (ly + 0.5) * r.height / comp.bh,
                     button: 0, pointerId: 1, bubbles: true };
          }
          function fire(comp, type, lx, ly) { comp.el.dispatchEvent(new PointerEvent(type, at(comp, lx, ly))); }
          out.z = a.root.getBoundingClientRect().width / 480;
          fire(a.signalX.buttons[2], 'pointerdown', 5, 5);           // x: decay
          fire(a.signalH.buttons[0], 'pointerdown', 5, 5);           // h: pulse
          var p = a.signalH.panel;                                   // then sketch on h
          fire(p, 'pointerdown', 60, 40); fire(p, 'pointermove', 80, 20); fire(p, 'pointerup', 80, 20);
          var c = a.fConvPanel;
          fire(c, 'pointerdown', 200, 10);
          for (var x = 205; x <= 300; x += 5) fire(c, 'pointermove', x, 10);
          fire(c, 'pointerup', 300, 10);
          fire(c, 'pointermove', 400, 10);                           // after release: ignored
          out.state = JOC.dump(a);
          document.getElementById('selftest-out').textContent = JSON.stringify(out);
        })();
        </script></body>"""
        src = CT.read_text(encoding="utf-8").replace("</body>", probe)
        with tempfile.TemporaryDirectory() as tmp:
            page = pathlib.Path(tmp) / "probe.html"
            page.write_text(src, encoding="utf-8")
            dom = dump_dom(page)
        self.no_error(dom)
        got = json.loads(html.unescape(re.search(r'<pre id="selftest-out"[^>]*>(.*?)</pre>', dom, re.S).group(1)))
        self.assertNotAlmostEqual(got["z"], 1.0, places=2)
        a = ct_model.Applet()
        a.press("x", "decay"); a.press("h", "pulse")
        a.sh.modify(60, 40); a.sh.drag(60, 40, 80, 20); a.sig_changed_event()
        a.conv_down(200)
        for x in range(205, 301, 5):
            a.conv_drag(x)
        self.assertEqual(got["state"], a.dump())

    def test_selftest_matches_reference_model_and_original(self):
        dom = dump_dom(CT, "#selftest")
        self.no_error(dom)
        m = re.search(r'<pre id="selftest-out"[^>]*>(.*?)</pre>', dom, re.S)
        self.assertTrue(m and m.group(1), "selftest produced no output")
        got = json.loads(html.unescape(m.group(1)))["scenarios"]
        model = ct_model.all_scenarios()
        for name, _, _, _ in ct_model.SCENARIOS:
            for key, val in model[name].items():
                self.assertEqual(got[name][key], val, f"page vs model: {name}.{key}")
            if ORACLE.is_dir():
                ref = json.loads((ORACLE / f"{name}.json").read_text(encoding="utf-8"))
                for key in model[name]:
                    self.assertEqual(got[name][key], ref[key], f"page vs original: {name}.{key}")


if __name__ == "__main__":
    unittest.main()
