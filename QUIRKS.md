# Quirks kept, and deliberate deviations

For Jon and the course professor. The port is meant to be a faithful copy first (PLAN.md), so
anything in the original that looks odd is **kept** and listed here rather than fixed. Any fix
would be an opt-in enhancement (ENHANCEMENT_OPTIONS.md).

## Continuous time (`joy_of_convolution.html`)

### Original behavior, kept on purpose
1. **No numbers on the time axis.** Only the origin line and the ±1 amplitude ticks. The implicit
   time unit is one pixel = 2π/474 (the integral's step), so the preset pulse is about 0.77
   (≈ π/4) wide and the decay is e^(−1.29t) (RESEARCH.md "Units/scales").
2. **The x(t) and h(t) panels show only the middle half of the time span** of the three wide
   panels (234 vs 474 px, pasted 1:1). A signal drawn right up to the edge of x(t) ends well
   inside the conv panel.
3. **y(t) is computed for every t on the first click**, but drawn only at the t values visited.
   Clicking (not dragging) from one t to another leaves gaps; dragging fills in every t passed.
4. **Any change to x or h clears the lower three panels.** The new y(t) is computed at the next
   click on the "x(t − v) and h(v)" panel.
5. **Only the "x(t − v) and h(v)" panel sets t.** Clicking the integrand or y(t) panels does nothing.
6. **Signals are stored in whole pixels.** y(t) and the integrand are truncated toward zero, so
   small outputs show as steps or as 0, e.g. pulse ∗ pulse peaks 1 px below the exact value, and
   overlaps of 1 or 2 samples show as exactly 0.
7. **Drawing isn't clamped.** Dragging above or below a panel stores values off the scale. They
   are drawn outside the panel and still count in the integral.
8. **The first and last samples can't be drawn** (they stay 0), and the double pulse leaves its
   very last sample at 0.
9. **Empty signals are drawn as a coloured line along the axis** (blue for x, red for h, black
   for the integrand): zero samples are drawn like any others.
10. **The "t" marker and its label slide with x(t − v)** and are clipped at the panel edges.
11. `startConvolution()` (which would pick a starting t automatically) exists in the original
    but is never called, so nothing happens until the first click.

### Deliberate deviations in the port
1. **The applet is scaled to the window** (fits the window height and the text column), and
   redrawn at the screen's real resolution. The original is 480 × 600 screen pixels, about 5 cm
   wide on a modern laptop. Lines are therefore smooth (antialiased) rather than jagged 1-px
   lines, and text uses the browser's Arial rather than Java's bitmap font.
2. **No JHU images or audio are used.** The equation in the y(t) panel is redrawn as text; the
   page's equation is MathML; the title banner is text with a drawn underline; the "Welcome!" and
   "Exercises" audio links became expandable transcripts; the quiz PDF became an expandable
   section of the page.
3. **The applet background is white**, as in the reference captures (appletviewer). Browsers'
   Java plugins could show a grey applet background.
4. **The page text is a centred column** (max about 52 em) instead of the full window width.
5. A credit and "work in progress" bar at the top, and a full credits section at the bottom.
6. Missing spaces in the saved original page text ("…of v.Then…", "below,or") are restored.
7. **Accessibility extras that don't change the look:** the preset buttons are real buttons
   (Tab + Enter/Space work), and a visually hidden live text gives t and y(t) to screen readers.
8. **Touch and pen work** (Pointer Events). Touching the applet doesn't scroll the page. Like the
   original's single mouse, **one pointer at a time** drives the applet: a second finger is ignored
   until the first one lifts (otherwise two fingers would splice their strokes into one drag).

### What is identical
The arithmetic: presets, freehand drawing, the Riemann sum, the integrand and the revealed-y
mask are bit-for-bit equal to the original's arrays in eight scripted scenarios: five preset
sweeps, plus drawing on h and over a preset, strokes and t sweeps that go leftward and outside
the panels, the cleared state after a change, and single clicks
(`py -m unittest discover -s tests -v`; needs the local reference captures). The panel geometry
is the original's GridBag result to the pixel. Under 1 % of pixels differ from the original's
captures, all in text and in the steep edges of pulses (`py tools/compare.py ct`).

## Discrete time (`joy_of_convolution_dt.html`)

No source code for the 2001 applet survives. The port was transcribed from its compiled code
(`javap -c` of `DTConvolve.jar`), and a separate Python transcription checks the reading.

### Original behavior, kept on purpose
1. **The y[n] axis is scaled to the wrong quantity.** When x or h changes, the applet picks the
   y[n] axis from the largest value of a sum that flips x twice, i.e. the *cross-correlation* of x
   and h rather than their convolution. When the two differ, y[n] can run past its axis (the
   drawn freehand ramp ∗ exponential in our tests reaches 10.4 on a ±10 axis) or the axis is
   larger than needed. The summand axis is scaled from the products of x's and h's extremes.
2. **The axes never shrink back while drawing.** The scaling uses the largest and smallest values
   ever written into x or h since the last preset, even if they were drawn over afterwards.
3. **The n = 0 click zone is twice as wide** as the others: n is computed with a truncating
   `(int)` cast, so everything from about −0.99 to +0.99 is n = 0. The n marker sits at the
   left edge of each positive n's zone and the right edge of each negative n's.
4. **Dragging walks n through every value** between the lowest n reached so far in the drag and
   the current one, revealing y[n] at each. Dragging left therefore leaves the marker one step
   behind the pointer.
5. **y[n] is revealed only at the n values visited**; elsewhere it is drawn as 0 (a dot on the
   axis), not hidden. Any change to x or h clears the three lower panels until the next click.
6. **The rightmost stem of every panel is always 0** (it is one sample past the end of the data),
   and x and h can't be drawn at n = 12.
7. **Drawing isn't clamped**: dragging above or below the x[n] or h[n] panel stores values off the
   ±5 scale.
8. The preset buttons are labels with a grey border that turns green (x) or blue (h) under the
   mouse; they act on mouse press.

### Deliberate deviations in the port
1. Scaled to the window and redrawn at screen resolution, as on the CT page.
2. **No JHU images or audio.** The ten preset icons are redrawn by our own code as small
   schematic stem plots (like the originals); the y[n] equation image is redrawn as text; the page
   equation is MathML; audio became transcripts; the quiz PDF became a section of the page.
3. Panels are white on the Swing grey (238) background, as in the reference captures.
4. Credit and "work in progress" bars; centred text column; missing spaces restored; the preset
   buttons are keyboard-operable; a hidden live text gives n and y[n] to screen readers.
5. Touch and pen work, one pointer at a time, as on the CT page.

### What is identical
x, h, x[n − k], h[k], the summand, y[n], n, both autoscaled axes and the reset state equal the
original's exactly (to the last bit of every double) in eight scripted scenarios (the same kinds
as for CT, including drawing far off the panel, which grows the axes). Panel geometry
is the original's GridBag result. About 1.7 % of pixels differ from the original's captures:
text antialiasing, the redrawn icons and equation (`py tools/compare.py dt`).
