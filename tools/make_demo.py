"""README demo GIFs: a convolution sweep on each page, rendered by the port itself.

For each frame, a temporary copy of the page is opened in headless Chrome with #shot=<initial>
(applet only, top left) and a script appended that presses the presets, drags the t (or n)
handle from the left edge to the frame's position, and repaints at scale Z. The frames are
cropped to the applet and assembled into docs/ct-demo.gif and docs/dt-demo.gif.

    py tools/make_demo.py          (needs Pillow and Chrome or Edge; no reference/ files)
"""
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BROWSERS = [Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")]
Z = 1.2
FRAMES = 40          # sweep frames; plus a first frame with no t chosen yet
HOLD_MS = 1800       # first and last frames
STEP_MS = 90

CT_JS = """
var a = JOC.applet, c = a.fConvPanel, W = c.fSigLength, F = %(f)d, N = %(n)d;
JOC.runScenario(a, ['demo', 'pulse', 'decay', null], 'a');
if (F > 0) {
  var X = Math.round((W - 1) * (F - 1) / (N - 1));
  c.mouseDown(0, 0);
  for (var x = 1; x <= X; x++) c.mouseDrag(x, 0);
}
a.layout(%(z)s, 1);
"""
DT_JS = """
var a = JOC.applet, d = a.xhDualPanel.mouseListener, W = a.xhDualPanel.bw, F = %(f)d, N = %(n)d;
JOC.runScenario(a, ['demo', 'Square pulse', 'Square pulse', false], 'a');
if (F > 0) {
  var X = 1 + Math.round((W - 3) * (F - 1) / (N - 1));
  d.mousePressed(1);
  for (var x = 2; x <= X; x++) d.mouseDragged(x);
}
a.layout(%(z)s, 1);
"""
PAGES = {"ct": ("joy_of_convolution.html", "s0_initial", 480, 600, CT_JS),
         "dt": ("joy_of_convolution_dt.html", "d0_initial", 600, 600, DT_JS)}


def frame(browser, tmp, key, f):
    page, initial, w, h, js = PAGES[key]
    w, h = round(w * Z), round(h * Z)
    html = (ROOT / page).read_text(encoding="utf-8")
    script = "<script>" + js % {"f": f, "n": FRAMES, "z": Z} + "</script>\n"
    copy = Path(tmp) / f"{key}_{f:03d}.html"
    copy.write_text(html.replace("</body>", script + "</body>"), encoding="utf-8")
    png = copy.with_suffix(".png")
    subprocess.run([str(browser), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size={w},{h}",
                    f"--user-data-dir={Path(tmp) / ('prof_%s_%d' % (key, f))}",
                    "--screenshot=" + str(png), copy.as_uri() + "#shot=" + initial],
                   check=True, capture_output=True, timeout=90)
    return Image.open(png).convert("RGB").crop((0, 0, w, h))


def main() -> int:
    browser = next((b for b in BROWSERS if b.exists()), None)
    if browser is None:
        print("needs Chrome or Edge")
        return 1
    with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(6) as pool:
        for key in PAGES:
            frames = list(pool.map(lambda f: frame(browser, tmp, key, f), range(FRAMES + 1)))
            durations = [HOLD_MS] + [STEP_MS] * (FRAMES - 1) + [HOLD_MS * 2]
            pal = [im.quantize(colors=64, method=Image.Quantize.MEDIANCUT) for im in frames]
            out = ROOT / "docs" / f"{key}-demo.gif"
            pal[0].save(out, save_all=True, append_images=pal[1:], duration=durations,
                        loop=0, optimize=True)
            print(f"{out.relative_to(ROOT)}: {len(frames)} frames, {out.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
