"""Will the pages open on a student's laptop, and does the CT page compute what the original
computed?

Static checks (always run): self-contained files, nothing fetched, no syntax that older Safari
can't parse, credits everywhere, no JHU material tracked by git, and the scenario lists in the
page, the Python model and the Java probe agree. Browser checks (skipped when no Chrome, Edge
or Chromium is installed): load joy_of_convolution.html from file:// in headless Chrome,
confirm no script error and every panel drawn, then run its #selftest (the tools/CtProbe.java
scenarios) and require the arrays to equal the Python reference model's, and the original
applet's when reference/ is present locally.

This module also holds the browser helpers the other test modules share (find_browser,
dump_dom, run_probe, POINTER_JS).
"""
import ast
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
import dt_model

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = [ROOT / "joy_of_convolution.html", ROOT / "index.html", ROOT / "joy_of_convolution_dt.html"]
CT, DT = PAGES[0], PAGES[2]
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


def dump_dom(page, fragment="", wait_ms=0):
    """The page's DOM after load. wait_ms > 0 lets timers run (virtual time) before the dump;
    without it only the first animation frame is guaranteed."""
    args = [find_browser(), "--headless=new", "--disable-gpu"]
    if wait_ms:
        args.append(f"--virtual-time-budget={wait_ms}")
    out = subprocess.run(args + ["--dump-dom", page.as_uri() + fragment],
                         capture_output=True, timeout=120, check=True)
    return out.stdout.decode("utf-8")


def error_text(dom):
    """The text of the page's red #err bar ('' when there was no script error)."""
    m = re.search(r'<div id="err"[^>]*>(.*?)</div>', dom, re.S)
    assert m, "no #err element in the page"
    return html.unescape(m.group(1)).strip()


def selftest_out(dom):
    m = re.search(r'<pre id="selftest-out"[^>]*>(.*?)</pre>', dom, re.S)
    assert m and m.group(1), "the page wrote nothing to #selftest-out"
    return json.loads(html.unescape(m.group(1)))


# Real PointerEvents at applet-panel coordinates on the scaled page. fire(comp, type, x, y,
# opts) dispatches at the centre of panel pixel (x, y); opts can set pointerId, pointerType,
# buttons. Like a real pointer, buttons is 1 while pressed (down, move) and 0 on release.
POINTER_JS = """
function at(comp, lx, ly) {
  var r = comp.el.getBoundingClientRect();
  return { x: r.left + (lx + 0.5) * r.width / comp.bw, y: r.top + (ly + 0.5) * r.height / comp.bh };
}
function fire(comp, type, lx, ly, opts) {
  opts = opts || {};
  var p = at(comp, lx, ly);
  var init = { clientX: p.x, clientY: p.y, button: type === 'pointermove' ? -1 : 0,
               buttons: type === 'pointerup' ? 0 : 1, pointerId: 1, pointerType: 'mouse',
               bubbles: true, cancelable: true };
  for (var k in opts) init[k] = opts[k];
  comp.el.dispatchEvent(new PointerEvent(type, init));
}
"""


def run_probe(page, body_js, fragment="", wait_ms=0):
    """Load a copy of `page` with `body_js` appended after the main script (POINTER_JS is in
    scope), and return (JSON the probe wrote to #selftest-out via done(obj), error-bar text).
    The probe may finish later, e.g. in requestAnimationFrame, as long as it calls done()."""
    probe = ("<script>\n" + POINTER_JS +
             "function done(o) { document.getElementById('selftest-out').textContent = JSON.stringify(o); }\n"
             "(function () {\n" + body_js + "\n})();\n</script></body>")
    src = page.read_text(encoding="utf-8").replace("</body>", probe)
    with tempfile.TemporaryDirectory() as tmp:
        copy = pathlib.Path(tmp) / page.name
        copy.write_text(src, encoding="utf-8")
        dom = dump_dom(copy, fragment, wait_ms)
    m = re.search(r'<pre id="selftest-out"[^>]*>(.*?)</pre>', dom, re.S)
    out = json.loads(html.unescape(m.group(1))) if m and m.group(1) else None
    return out, error_text(dom)


def js_scenarios(page):
    """The page's SCENARIOS array, parsed as a Python literal."""
    text = page.read_text(encoding="utf-8")
    m = re.search(r"\nvar SCENARIOS = (\[.*?\n\]);", text, re.S)
    lit = re.sub(r"\bnull\b", "None", m.group(1))
    lit = re.sub(r"\btrue\b", "True", re.sub(r"\bfalse\b", "False", lit))
    return ast.literal_eval(lit)


def java_actions(probe, name):
    """A tools/*Probe.java action list (static final String[][] NAME = {...};) as tuples."""
    text = (ROOT / "tools" / probe).read_text(encoding="utf-8")
    body = re.search(r"String\[\]\[\] " + name + r" = \{(.*?)\};", text, re.S).group(1)
    body = re.sub(r"//[^\n]*", "", body)
    rows = re.findall(r"\{([^{}]*)\}", body)
    out = []
    for row in rows:
        cells = re.findall(r'"([^"]*)"', row)
        out.append(tuple(int(c) if re.fullmatch(r"-?\d+", c) else c for c in cells))
    return out


def as_tuples(actions):
    return [tuple(a) for a in actions]


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
        # so that a syntax error in the main script still shows the red bar
        for page in (CT, DT):
            text = page.read_text(encoding="utf-8")
            self.assertLess(text.index("window.onerror"), text.index("'use strict'"), page.name)

    def test_credits_on_every_page(self):
        for name, _, text in self.pages():
            for who in ("Steven Crutchfield", "Johns Hopkins University", "Wilson J. Rugh",
                        "Michael Ross", "Work in progress"):
                self.assertIn(who, text, f"{name}: {who}")

    def test_index_links_resolve(self):
        text = PAGES[1].read_text(encoding="utf-8")
        local = [h for h in re.findall(r'href="([^"]+)"', text) if not h.startswith("https://")]
        self.assertEqual(sorted(local), ["joy_of_convolution.html", "joy_of_convolution_dt.html"])
        for h in local:
            self.assertTrue((ROOT / h).is_file(), h)

    def test_no_jhu_material_is_tracked(self):
        # CLAUDE.md hard rule: the originals ("all rights reserved") stay in gitignored reference/.
        try:
            out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True,
                                 timeout=30, check=True).stdout.split()
        except (OSError, subprocess.SubprocessError):
            self.skipTest("not a git checkout, or git not installed")
        for f in out:
            self.assertFalse(f.startswith("reference/"), f)
            self.assertNotRegex(f.lower(), r"\.(class|jar|gif|jpe?g|mp3|au|wav|pdf)$", f)

    def test_scenarios_agree_in_page_model_and_probe(self):
        # The same scenarios are written out three times (JS page, Python model, Java probe);
        # the parity tests only mean something if the three lists are the same.
        for page, model, probe, names in ((CT, ct_model, "CtProbe.java", ("S7", "S8", "S9")),
                                          (DT, dt_model, "DtProbe.java", ("D6", "D7", "D8"))):
            js = js_scenarios(page)
            sweeps = [tuple(s) for s in js if not isinstance(s[1], list)]
            acts = [(s[0], as_tuples(s[1])) for s in js if isinstance(s[1], list)]
            self.assertEqual(sweeps, [tuple(s) for s in model.SCENARIOS], page.name)
            self.assertEqual(acts, [(n, as_tuples(a)) for n, a in model.ACTION_SCENARIOS], page.name)
            for (name, actions), const in zip(model.ACTION_SCENARIOS, names):
                self.assertEqual(java_actions(probe, const), as_tuples(actions), f"{probe} {const}")
                self.assertIn(f'actions("{name}", {const});', (ROOT / "tools" / probe).read_text(encoding="utf-8"))


@unittest.skipUnless(find_browser(), "needs Chrome, Edge or Chromium installed")
class InBrowser(unittest.TestCase):
    def no_error(self, dom):
        self.assertEqual(error_text(dom), "", "page shows a script error")

    def test_page_loads_and_draws_every_panel(self):
        dom = dump_dom(CT)
        self.no_error(dom)
        m = re.search(r'data-painted="(\d+)"', dom)
        self.assertIsNotNone(m, "applet never painted")
        self.assertEqual(int(m.group(1)), 2 * 5 + 3)   # x, h, 8 buttons, conv, integrand, y

    def test_index_page_loads(self):
        self.no_error(dump_dom(PAGES[1]))

    def test_shot_mode_runs(self):
        for spec in ("s3_doublepulse_decay:c", "s0_initial", "s6_single_click", "s7_left_and_outside"):
            self.no_error(dump_dom(CT, "#shot=" + spec))

    def test_pointer_events_drive_the_applet(self):
        # Real PointerEvents at screen coordinates (the applet is scaled, z != 1): exercises
        # the event wiring and the screen-to-applet coordinate mapping, which #selftest skips.
        got, err = run_probe(CT, """
          var a = JOC.applet, out = {};
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
          done(out);""")
        self.assertEqual(err, "")
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
        got = selftest_out(dom)["scenarios"]
        model = ct_model.all_scenarios()
        self.assertEqual(sorted(got), sorted(ct_model.scenario_names()))
        for name in ct_model.scenario_names():
            for key, val in model[name].items():
                self.assertEqual(got[name][key], val, f"page vs model: {name}.{key}")
            if ORACLE.is_dir():
                f = ORACLE / f"{name}.json"
                self.assertTrue(f.is_file(), f"{f.name} missing: re-run tools/CtProbe.java (CLAUDE.md)")
                ref = json.loads(f.read_text(encoding="utf-8"))
                for key in model[name]:
                    self.assertEqual(got[name][key], ref[key], f"page vs original: {name}.{key}")


if __name__ == "__main__":
    unittest.main()
