# Research notes — original "Joy of Convolution" (gathered 2026-11-17)

Source: https://pages.jh.edu/signals/convolve/index.html
Parent index: https://pages.jh.edu/signals/index.html

**Access gotcha:** the site is behind Cloudflare and returns 403 to curl/WebFetch.
Only a real browser works (used Claude-in-Chrome + in-page `fetch()`).

## Credits (as stated on the original site)
- Applet by **Steven Crutchfield**, Fall 1996 (source header: "Convolution Demo by Steve Crutchfield").
- Part of the JHU *Signals, Systems, and Control Demonstrations* project directed by
  **Wilson J. Rugh**, 1994–2003. Narration on several demos by **Cherie Weinert**.
  Support: NSF, Kenan Fund, JHU Center for Educational Resources, E.J. Schaefer Chair.
  Site page design: Mark Nesky. Premier Engineering Courseware of 2001.
- Discrete-time version: original by Crutchfield (Summer 1997), update by **Michael Ross** (Fall 2001).

## Copyright notice on the parent page (verbatim)
"Copyright 1995-2003, Johns Hopkins University and Wilson J. Rugh, all rights reserved.
Visitors are permitted to access this site for personal or non-profit educational use only.
Copying or duplicating the images or code is prohibited. Use of this site for business or
commercial purposes also is prohibited."
→ Permission question is open; see plan/questions. Original code is NOT stored in this repo.

## What it actually is
A **Java applet** (`<applet code="Convolve.class" width=480 height=600>`), not JavaScript.
Browsers removed applet/NPAPI support entirely (~2015–2017); the parent page itself says
(March 2014) "Recent updates to Java ... have broken most of the demonstrations."

## Assets on the server (all HTTP 200)
| File | Size | Notes |
|---|---|---|
| `Convolve.java` | 20.9 KB, 2003-07-27 | **Full original source**, 11 classes, one file |
| `*.class` (11) | ~1–5 KB each | compiled classes |
| `conv.gif` / `conv.jpg` | 0.5 / 2.5 KB | convolution-integral equation images (jpg drawn in y panel) |
| `welcome.mp3` | 1.77 MB | audio intro (page links to old `www.jhu.edu/...` host) |
| `exercises.mp3` | 2.99 MB | audio suggested exercises |
| `Quizconvolution.pdf` | 28.9 KB | 1-page, 5 multiple-choice questions, **no answer key** |
| Discrete-time: `../discreteconv2/DTConvolve.jar` | 20.8 KB | Java 1.3 plugin `<object>`, 600×600; quiz `Quizdtconvolution.pdf` |

## Applet behavior (from reading Convolve.java)
Layout (GridBag, top→bottom):
1. **x(t)** panel (blue) and **h(t)** panel (red) side by side, each a mouse-drawable canvas
   with a button row: `Select: [pulse] [double pulse] [decay] [clear]`. Buttons are drawn as
   tiny thumbnails of their signal shape (colored blue/red/green/black). Main panels start **empty**.
2. **"x(t - v) and h(v)"** panel, full width: h(v) fixed in red; flipped x(t−v) in blue overlaid
   (white made transparent) and slid horizontally to the current t. Click anywhere sets t;
   dragging moves t. A small "t" marker sits on the axis of the sliding x image.
3. **"x(t - v) h(v)"** integrand panel (black).
4. **y(t)** panel (black) with the equation image in the corner. y is computed for all t on the
   first click (Riemann sum), but only **revealed** at t values the user has visited
   (`shown[]`); dragging fills in every pixel passed. A dot marks the current (t, y(t)).
- Any edit to x or h clears panels 2–4 (forces recompute on next click).

Units/scales:
- **No horizontal tick marks or numeric time labels anywhere** — only the origin line and ±1
  vertical ticks. Time units are implicit: the integral uses `dx = 2π / W` where W is the
  *conv panel* width (~470 px). x/h panels are ~half that width (N px) and are pasted 1:1 in
  pixels, centered (`fOffset = (W − N)/2`). So x/h panels show ~half the span of the conv/y panels.
  The port should define clean physical units and decide whether to label the time axis.
- Vertical: ±1 tick marks at amplitude/2 pixels; signals stored as **int pixels** (truncation).
- Presets, in samples from the panel centre (sample 117 of 234; checked against the original's
  arrays, 2026-11-17):
  - pulse: +1 (31 px) on samples 0..57
  - double pulse: −1 on 0..57, +1 on 58..115 (the very last sample of the panel stays 0)
  - decay: `exp(-4.0*(i - N/2)/N)`, i.e. e^(−4k/234) at sample k ≥ 0
  - **In the integral's units** (one sample = dx = 2π/474, because x and h are pasted 1:1 into
    the 474-px conv panel): pulse width 58·dx ≈ 0.77 ≈ π/4 (not π/2, which an earlier note here
    assumed by using 2π/234), decay e^(−1.29 t) (time constant ≈ 0.78). pulse ∗ pulse peaks at
    23 px ≈ 0.74 in tick units, i.e. the pulse width less int truncation.
- Mouse drawing: click sets one sample to the cursor height; drag linearly interpolates between
  the previous and current mouse positions. First/last samples are not editable.
- `startConvolution()` exists (auto-picks a starting t) but is never called.

## Other Crutchfield applets on the same index (possible future scope)
Fourier Series Approximation (1996), SampleMania (1997), Bode Servo Analysis (1997),
Robust Stabilization (2000), plus applets inside the CT LTI Interactive Lecture Module (1998).

## Ground truth captured from the running originals (2026-11-17)
Produced by `tools/CtProbe.java` / `tools/DtProbe.java` under JDK 8 (see CLAUDE.md). Output in
`reference/captures/{ct,dt}/` (gitignored): `geometry.txt`, 1x PNG captures of scripted scenarios
(presets, freehand drawing, t/n sweeps at 1/4, 1/2, 3/4 and full width), and `<scenario>.json`
dumps of the internal arrays. The JSON is the numeric oracle for the port's tests.

### CT geometry (exact, applet 480×600, from AWT GridBag)
| Component | x, y, w, h |
|---|---|
| x(t) drawing panel | 3, 3, 234, 124 |
| x buttons row (`Select:` + 4 SigButtons 41×23 at x = 53, 99, 145, 191) | 3, 127, 234, 29 |
| h(t) drawing panel | 243, 3, 234, 124 |
| h buttons row (buttons at x = 293, 339, 385, 431) | 243, 127, 234, 29 |
| "x(t - v) and h(v)" ConvPanel | 3, 162, 474, 124 |
| "x(t - v) h(v)" integrand panel | 3, 292, 474, 124 |
| y(t) panel (equation image top-left) | 3, 422, 474, 174 |
Internals: x/h signals 234 samples, amplitude 62 px (±1 tick at 31 px). ConvPanel W = 474,
fAmplitude = 62, fScale = 2/62. y panel 474 samples, amplitude 87. Background between panels
white in appletviewer; the JHU page put the applet in a `#C0C0C0` table cell.

### DT applet (Swing JApplet, 600×600; Ross 2001 update)
- No source anywhere; `reference/dt/javap/*.txt` holds the full `javap -c -p` disassembly (10 classes).
- GridBag layout, captured at (before the button GIFs were saved; **re-capture once they are**):
  x[n] panel 9,6,286,128 · h[n] panel 305,6,286,128 · button rows y = 139, h 45
  (`Select:` label 79 wide, five 41-wide icon JLabels) · "x[n-k] and h[k]" 9,189,582,128 ·
  "x[n-k]h[k]" 9,327,582,128 · y[n] 9,465,582,128.
- Presets (tooltips): Square pulse, One period of a square wave, Right-sided exponential,
  Unit Impulse, Clear. Button faces are `x_*.gif` / `h_*.gif` loaded from the codebase.
- Stem plots; fixed axes ±5 for x/h/dual, ±10 for product and y; n axis −12..12 (constants
  12.0, 24, 5.0 in DTConvolve). Colors: x green, h blue, product orange, y red.
  "n = 0" marker under the dual panel; a circle marks the current n in the lower panels.
