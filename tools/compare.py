"""Visual check: a port next to the original applet, capture by capture.

For every PNG that tools/CtProbe.java or DtProbe.java wrote to reference/captures/<ct|dt>/,
this loads the port's page with #shot=<scenario>:<step> in headless Chrome at the applet's size
and 1x scale (the page then shows only the applet, unscaled), and writes to
reference/captures/compare/<ct|dt>/:

    <name>.png   original | port | difference (differing pixels in magenta)

and prints the share of pixels that differ. Text never matches exactly (the browser
antialiases, Java 1.0 did not), so expect a few percent; look at the images, not the number.

    py tools/compare.py ct       (or dt; needs Pillow, Chrome or Edge, and the reference captures)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
PAGES = {"ct": ("joy_of_convolution.html", 480, 600, "s*.png"),
         "dt": ("joy_of_convolution_dt.html", 600, 600, "d*.png")}
BROWSERS = [Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")]


def shot_spec(stem: str) -> str:
    """s2_pulse_decay_c_t237 -> s2_pulse_decay:c ; s0_initial -> s0_initial"""
    parts = stem.split("_")
    if len(parts) >= 4 and len(parts[-2]) == 1:
        return "_".join(parts[:-2]) + ":" + parts[-2]
    if len(parts) >= 3 and parts[-1] == "signals":
        return "_".join(parts[:-2]) + ":a"
    return stem


def screenshot(browser: Path, page: Path, size, spec: str, dest: Path) -> None:
    url = page.as_uri() + "#shot=" + spec
    subprocess.run([str(browser), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=%d,%d" % size,
                    "--screenshot=" + str(dest), url],
                   check=True, capture_output=True, timeout=60)


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else "ct"
    page_name, W, H, pattern = PAGES[which]
    page = ROOT / page_name
    caps = ROOT / "reference" / "captures" / which
    out = ROOT / "reference" / "captures" / "compare" / which
    browser = next((b for b in BROWSERS if b.exists()), None)
    if browser is None or not caps.is_dir():
        print(f"needs Chrome/Edge and reference/captures/{which} (see CLAUDE.md)")
        return 1
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for cap in sorted(caps.glob(pattern)):
            if "hover" in cap.stem:           # mouse-over state: not scripted in the port
                continue
            spec = shot_spec(cap.stem)
            mine = Path(tmp) / (cap.stem + ".png")
            screenshot(browser, page, (W, H), spec, mine)
            a = Image.open(cap).convert("RGB")
            b = Image.open(mine).convert("RGB").crop((0, 0, W, H))
            diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 48 else 0)
            share = diff.histogram()[255] / (W * H)
            marked = a.copy()
            marked.paste((255, 0, 255), mask=diff)
            sheet = Image.new("RGB", (W * 3 + 20, H), (128, 128, 128))
            for k, im in enumerate((a, b, marked)):
                sheet.paste(im, (k * (W + 10), 0))
            sheet.save(out / (cap.stem + ".png"))
            print(f"{cap.stem:32s} {spec:28s} {share * 100:5.2f} % pixels differ")
    print("side-by-side images:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
