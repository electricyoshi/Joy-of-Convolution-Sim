# Hands-on checklist (Jon and the course professor)

What the automated tests can't cover: real mice, trackpads, touch, other browsers, and whether
it *feels* like the original. Do it once on a Windows laptop and once on a Mac. Open
`joy_of_convolution.html` by double-clicking it (no server needed).

Write down the browser and version for each run. Anything that fails: note what you did and
what you saw (a screenshot helps).

## Load
- [ ] The page opens with **no red error bar** at the top.
- [ ] The whole applet (five panels, two "Select:" rows) fits on screen without scrolling once
      it is scrolled into view, and nothing looks blurry.
- [ ] Resize the window narrower and shorter: the applet shrinks to fit and stays sharp.

## Presets and drawing (top two panels)
- [ ] Each of the four buttons under x(t) puts its shape in x(t): pulse, double pulse, decay,
      clear. Same for h(t).
- [ ] Click once in x(t): one point jumps to the mouse height.
- [ ] Press and drag across x(t): the signal follows the mouse smoothly with no gaps, even when
      moving fast. Dragging above/below the panel keeps drawing (off-scale; see QUIRKS.md 7).
- [ ] The far-left and far-right edge points never change.

## Convolution (bottom three panels)
- [ ] Pick pulse for x and decay for h. Click near the middle of "x(t − v) and h(v)": the
      flipped x appears in blue over h in red, the integrand appears, and a dot appears in y(t).
- [ ] Drag left and right: the blue shape slides with the mouse; y(t) is traced everywhere the
      mouse passes; the dot follows.
- [ ] Release, then click somewhere else (without dragging): y(t) shows only the traced parts
      plus the new dot (QUIRKS.md 3).
- [ ] Change x or h: the lower three panels clear until you click again.
- [ ] pulse ∗ pulse traces a triangle; pulse ∗ decay rises and then decays.

## Keyboard and touch (nice to have)
- [ ] Tab reaches the eight preset buttons (a blue focus ring), and Enter or Space applies them.
- [ ] On a touch screen or tablet: drawing and dragging t work with a finger.

## Page
- [ ] "Welcome!", "Exercises" and "Quiz" expand and collapse. The equation renders as math.
- [ ] Credits are visible at the top and bottom.

## Transcripts (Jon, once)
- [ ] Listen to `reference/ct/welcome.mp3` and `exercises.mp3` while reading the "Welcome!" and
      "Exercises" text on the page. Fix or note any wording that differs.
