"""Visual check: the CT port next to the original applet, capture by capture.

For every PNG that tools/CtProbe.java wrote to reference/captures/ct/, this loads
joy_of_convolution.html#shot=<scenario>:<step> in headless Chrome at 480 x 600 and 1x scale
(the page then shows only the applet, unscaled), and writes to reference/captures/compare/ct/:

    <name>.png   original | port | difference (differing pixels in magenta)

and prints the share of pixels that differ. Text never matches exactly (the browser
antialiases, Java 1.0 did not), so expect a few percent; look at the images, not the number.

    py tools/compare_ct.py            (needs Pillow, Chrome or Edge, and the reference captures)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
CAPS = ROOT / "reference" / "captures" / "ct"
OUT = ROOT / "reference" / "captures" / "compare" / "ct"
PAGE = ROOT / "joy_of_convolution.html"
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


def screenshot(browser: Path, spec: str, dest: Path) -> None:
    url = PAGE.as_uri() + "#shot=" + spec
    subprocess.run([str(browser), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=480,600",
                    "--screenshot=" + str(dest), url],
                   check=True, capture_output=True, timeout=60)


def main() -> int:
    browser = next((b for b in BROWSERS if b.exists()), None)
    if browser is None or not CAPS.is_dir():
        print("needs Chrome/Edge and reference/captures/ct (see CLAUDE.md)")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for cap in sorted(CAPS.glob("s*.png")):
            spec = shot_spec(cap.stem)
            mine = Path(tmp) / (cap.stem + ".png")
            screenshot(browser, spec, mine)
            a = Image.open(cap).convert("RGB")
            b = Image.open(mine).convert("RGB").crop((0, 0, 480, 600))
            diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 48 else 0)
            share = diff.histogram()[255] / (480 * 600)
            marked = a.copy()
            marked.paste((255, 0, 255), mask=diff)
            sheet = Image.new("RGB", (480 * 3 + 20, 600), (128, 128, 128))
            for k, im in enumerate((a, b, marked)):
                sheet.paste(im, (k * 490, 0))
            sheet.save(OUT / (cap.stem + ".png"))
            print(f"{cap.stem:32s} {spec:28s} {share * 100:5.2f} % pixels differ")
    print("side-by-side images:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
